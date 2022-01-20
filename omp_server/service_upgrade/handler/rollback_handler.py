import logging
import os
import random
from datetime import datetime

from django.conf import settings
from django.db import transaction

from db_models.mixins import RollbackStateChoices
from db_models.models import RollbackDetail, Service, ServiceHistory
from service_upgrade.handler.base import BaseHandler, StartOperationMixin, \
    StopServiceMixin, StartServiceMixin

logger = logging.getLogger(__name__)


class RollbackBaseHandler(BaseHandler):
    operation_type = "ROLLBACK"

    @transaction.atomic
    def write_db(self, result=False):
        """写库"""
        if not result:
            # 升级失败，更新upgrade detail、service状态
            state = f"{self.operation_type}_FAIL"
            self.service.service_status = Service.SERVICE_STATUS_UNKNOWN
            self.service.save()
            self.detail.rollback_state = getattr(RollbackStateChoices, state)
            ServiceHistory.create_history(self.service, self.detail)
        self.detail.save()
        # 升级结束更新服务表
        self.sync_relation_details()

    def sync_relation_details(self):
        for relation_detail in self.relation_details:
            for k in {"path_info", "handler_info", "message", "rollback_state"}:
                v = getattr(self.detail, k)
                setattr(relation_detail, k, v)
            relation_detail.save()
            service = relation_detail.upgrade.service
            service.service_status = self.service.service_status
            service.save()
            ServiceHistory.create_history(service, relation_detail)
            relation_detail.refresh_from_db()

    def handler(self):
        raise NotImplementedError

    @property
    def detail_class(self):
        return RollbackDetail

    @property
    def union_server(self):
        return self.detail.upgrade.union_server


class StartRollbackHandler(StartOperationMixin, RollbackBaseHandler):
    log_message = "服务实例{}: 开始回滚..."
    operation_type = "ROLLBACK"

    @transaction.atomic
    def set_service_state(self):
        self.detail.rollback_state = RollbackStateChoices.ROLLBACK_ING
        self.detail.save()
        self.detail.refresh_from_db()
        self.service.service_status = Service.SERVICE_STATUS_ROLLBACK
        self.service.save()
        self.service.refresh_from_db()
        for detail in self.relation_details:
            detail.rollback_state = RollbackStateChoices.ROLLBACK_ING
            service = detail.upgrade.service
            service.service_status = Service.SERVICE_STATUS_ROLLBACK
            service.save()
            detail.save()
            detail.refresh_from_db()


class RollBackStopServiceHandler(StopServiceMixin, RollbackBaseHandler):
    operation_type = "ROLLBACK"

    def handler(self):
        if self.service.is_static:
            self._log("服务无需停止,跳过!")
            return True
        success = self.stop_service(self.service)
        if not success:
            return False
        for relation_detail in self.relation_details:
            success = self.stop_service(relation_detail.upgrade.service)
            if not success:
                return False
        return True


class RollBackServiceHandler(RollbackBaseHandler):
    log_message = "服务实例{}: 回滚{}"
    operation_type = "ROLLBACK"

    def backup_file_str(self):
        backup_package = os.path.join(
            os.path.dirname(self.service.install_folder),
            f"rollback_backup/"
        )
        time_str = datetime.today().strftime('%Y%m%d')
        backup_name = f"{self.service.service.app_name}.back-{time_str}-" \
                      f"{random.randint(1, 120)}"
        backup_file = os.path.join(backup_package, backup_name)
        rollback_file = self.detail.upgrade.path_info.get('backup_file_path')
        return f"mkdir -p {backup_package} && " \
               f"mv {self.service.install_folder} {backup_file} && " \
               f"mv {rollback_file} {self.service.install_folder} && " \
               f"echo 备份路径:{backup_file}"

    def handler(self):
        rollback_file = self.detail.upgrade.path_info.get('backup_file_path')
        if not rollback_file:
            return True
        data_json_path = os.path.join(
            self.detail.data_path,
            f"omp_packages/{self.service._uuid}.json"
        )
        rollback_path = self.service.service_controllers.get("rollback")
        if not rollback_path:
            cmd_str = self.backup_file_str()
        else:
            cmd_str = f"python {rollback_path} " \
                      f"--local_ip {self.service.ip} " \
                      f"--data_json {data_json_path} " \
                      f"--version {self.detail.upgrade.current_app.app_version} " \
                      f"--backup_path {rollback_file}"
        state, message = self.salt_client.cmd(
            self.service.ip,
            cmd_str,
            settings.SSH_CMD_TIMEOUT
        )
        if not state:
            self._log(f"执行回滚命令失败:{cmd_str}!\n错误信息: {message}", "error")
            return False
        if "备份路径:" in message:
            self.detail.path_info.update(
                rollback_backup_path=message.split("备份路径:")[-1]
            )
        return True


class RollBackStartServiceHandler(StartServiceMixin, RollbackBaseHandler):
    operation_type = "ROLLBACK"

    def sync_relation_details(self):
        for relation_detail in self.relation_details:
            for k in {"path_info", "handler_info", "message", "rollback_state"}:
                v = getattr(self.detail, k)
                setattr(relation_detail, k, v)
            relation_detail.save()
            relation_detail.upgrade.has_rollback = True
            relation_detail.upgrade.save()
            service = relation_detail.upgrade.service
            service.update_application(
                self.detail.upgrade.current_app,
                True,
                self.service.install_folder
            )
            ServiceHistory.create_history(service, relation_detail)
            relation_detail.refresh_from_db()

    def write_db(self, result=False):
        """写库"""
        state = f"{self.operation_type}_SUCCESS"
        self.detail.rollback_state = getattr(RollbackStateChoices, state)
        self.detail.upgrade.has_rollback = True
        self.detail.upgrade.save()
        self.detail.save()
        # 创建服务操作记录
        ServiceHistory.create_history(self.service, self.detail)
        # 升级结束更新服务表
        self.service.update_application(
            self.detail.upgrade.current_app,
            True,
            self.service.install_folder
        )
        # 同步关联服务
        self.sync_relation_details()

    def handler(self):
        if self.service.is_static:
            self._log("服务无需启动,跳过!")
            return True
        self.start_service(self.service)
        for relation_detail in self.relation_details:
            self.start_service(relation_detail.upgrade.service)
        return True


"""
回滚流程：
    1、停服务
    2、调用回滚脚本（参数传目标主机ip、data.json、目标版本version、升级步骤2的包路径）
    3、启动服务（回滚成功以步骤2的结果为准）
"""
rollback_handlers = [
    StartRollbackHandler,
    RollBackStopServiceHandler,
    RollBackServiceHandler,
    RollBackStartServiceHandler
]
