import json
import logging
import time
import os
import random
from datetime import datetime

from django.conf import settings
from django.db import transaction

from db_models.mixins import UpgradeStateChoices
from db_models.models import UpgradeDetail, Service, Maintain
from promemonitor.alertmanager import Alertmanager
from service_upgrade.handler.base import BaseHandler

logger = logging.getLogger(__name__)


class UpgradeBaseHandler(BaseHandler):
    operation_type = "UPGRADE"

    @transaction.atomic
    def write_db(self, result=False):
        """写库"""
        if not result:
            # 升级失败，更新upgrade detail、service状态
            state = f"{self.operation_type}_FAIL"
            self.service.service_status = Service.SERVICE_STATUS_UNKNOWN
            self.service.save()
            self.detail.upgrade_state = getattr(UpgradeStateChoices, state)
        self.detail.save()
        # 升级结束更新服务表
        self.sync_relation_details()

    def sync_relation_details(self):
        for relation_detail in self.relation_details:
            for k in {"path_info", "handler_info", "message", "upgrade_state"}:
                v = getattr(self.detail, k)
                setattr(relation_detail, k, v)
            relation_detail.save()
            service = relation_detail.service
            service.service_status = self.service.service_status
            service.save()
            relation_detail.refresh_from_db()

    def handler(self):
        raise NotImplementedError

    @property
    def detail_class(self):
        return UpgradeDetail

    @property
    def union_server(self):
        return self.detail.union_server


class StartUpgradeHandler(UpgradeBaseHandler):
    log_message = "服务实例{}: 开始升级..."

    def set_alert_maintain(self):
        has_maintain = Maintain.objects.filter(
            matcher_name="env", matcher_value=self.service.env.name
        ).exists()
        if not has_maintain:
            Alertmanager().set_maintain_by_env_name(self.service.env.name)

    @transaction.atomic
    def set_service_state(self):
        self.detail.upgrade_state = UpgradeStateChoices.UPGRADE_ING
        self.detail.save()
        self.detail.refresh_from_db()
        self.service.service_status = Service.SERVICE_STATUS_UPGRADE
        self.service.save()
        self.service.refresh_from_db()
        for detail in self.relation_details:
            detail.upgrade_state = UpgradeStateChoices.UPGRADE_ING
            detail.service.service_status = \
                Service.SERVICE_STATUS_UPGRADE
            detail.service.save()
            detail.save()
            detail.refresh_from_db()

    def handler(self):
        self.set_alert_maintain()
        self.set_service_state()
        return self.detail, self.service, self.relation_details

    def __call__(self, operation_args, *args, **kwargs):
        if not self.valid_args(operation_args, self.detail_class):
            return None
        self.detail = operation_args[0]
        self.service = operation_args[1]
        self.relation_details = operation_args[2]
        self._log(self.log_message.format(self.union_server), "info")
        return self.handler()


class StopServiceHandler(UpgradeBaseHandler):
    log_message = "服务实例{}: 停止服务{}"

    def stop_service(self, service):
        for i in range(2):
            state, message = self.salt_client.cmd(
                self.service.ip,
                f'bash {service.service_controllers.get("stop")}',
                timeout=settings.SSH_CMD_TIMEOUT
            )
            if not state:
                raise Exception(f"salt执行命令失败，错误输出: {str(message)}")
            if "[not  running]" in message:
                # 休眠5秒等待停止
                time.sleep(5)
                return True
            time.sleep(5)
        return False

    def handler(self):
        if self.service.is_static:
            self._log("服务无需停止,跳过!")
            return True
        success = self.stop_service(self.service)
        if not success:
            return False
        for relation_detail in self.relation_details:
            success = self.stop_service(relation_detail.service)
            if not success:
                return False
        return True


class BackupServiceHandler(UpgradeBaseHandler):
    log_message = "服务实例{}: 备份服务包{}"

    def do_backup(self, backup_package):
        # 生成备份文件名
        time_str = datetime.now().strftime("%Y%m%d%H%M")
        backup_name = f"{self.service.service.app_name}.back-{time_str}-" \
                      f"{random.randint(1, 120)}"
        # 备份服务文件
        backup_file = os.path.join(backup_package, backup_name)
        backup_str = f"mkdir -p {backup_package} && " \
            f"mv {self.service.install_folder} {backup_file}"
        state, result = self.salt_client.cmd(
            self.service.ip, backup_str, settings.SSH_CMD_TIMEOUT)
        if not state:
            raise Exception("备份原服务文件失败!\n 错误信息:{}".format(result))
        self.detail.path_info.update(
            {
                "old_file_path": self.service.install_folder,
                "backup_file_path": backup_file,
            }
        )
        return state

    def handler(self):
        backup_package = os.path.join(
            os.path.dirname(self.service.install_folder),
            f"upgrade_backup/{datetime.today().strftime('%Y%m%d')}"
        )
        return self.do_backup(backup_package)


class SendPackageHandler(UpgradeBaseHandler):
    log_message = "服务实例{}: 发送升级包{}"

    def handler(self):
        tar_package = os.path.join(
            self.detail.target_app.app_package.package_path,
            self.detail.target_app.app_package.package_name
        )
        if not tar_package:
            raise Exception(f"升级包{tar_package}不存在")
        send_packages = os.path.join(
            self.detail.data_path,
            f"omp_packages"
        )
        state, message = self.salt_client.cp_file(
            self.service.ip,
            tar_package,
            send_packages
        )
        if not state:
            raise Exception("发送升级包失败!\n错误信息: {}".format(message))
        return True


class UnzipPackageHandler(UpgradeBaseHandler):
    log_message = "服务实例{}: 解压升级包{}"

    def handler(self):
        tar_packages_path = os.path.join(
            self.detail.data_path,
            "omp_packages"
        )
        package_name = self.detail.target_app.app_package.package_name
        install_path = os.path.dirname(self.service.install_folder)

        cmd_str = f"cd {tar_packages_path} &&" \
                  f"tar -xf {package_name} -C {install_path}"
        state, message = self.salt_client.cmd(
            self.service.ip, cmd_str, settings.SSH_CMD_TIMEOUT)
        if not state:
            raise Exception(f"解压升级包失败!\n错误信息: {message}")
        return state


class UpgradeServiceHandler(UpgradeBaseHandler):
    log_message = "服务实例{}: 升级{}"

    def handler(self):
        upgrade_file = json.loads(
            self.detail.target_app.app_controllers
        ).get("upgrade", "scripts/upgrade.py")
        upgrade_path = os.path.join(
            self.service.install_folder,
            upgrade_file
        )
        data_json_path = os.path.join(
            self.detail.data_path,
            f"omp_packages/{self.service._uuid}.json"
        )
        cmd_str = f"python {upgrade_path} " \
                  f"--local_ip {self.service.ip} " \
                  f"--data_json {data_json_path} " \
                  f"--version {self.detail.current_app.app_version}" \
                  f"--backup_path " \
                  f"{self.detail.path_info.get('backup_file_path')}"
        state, message = self.salt_client.cmd(
            self.service.ip, cmd_str, settings.SSH_CMD_TIMEOUT)
        if not state:
            raise Exception(f"通过salt执行命令:{cmd_str};\n错误输出:{message}!")
        return state


class StartServiceHandler(UpgradeBaseHandler):
    log_message = "服务实例{}: 启动服务{}"

    def sync_relation_details(self):
        for relation_detail in self.relation_details:
            for k in {"path_info", "handler_info", "message", "upgrade_state"}:
                v = getattr(self.detail, k)
                setattr(relation_detail, k, v)
            relation_detail.save()
            service = relation_detail.service
            service.update_application(
                self.detail.target_app,
                True,
                self.service.install_folder
            )
            relation_detail.refresh_from_db()

    def write_db(self, result=False):
        """写库"""
        state = f"{self.operation_type}_SUCCESS"
        self.detail.upgrade_state = getattr(UpgradeStateChoices, state)
        self.detail.save()
        self.service.update_application(
            self.detail.target_app,
            True,
            self.service.install_folder
        )
        # 升级结束更新服务表
        self.sync_relation_details()

    def fail_handler(self):
        """失败处理"""
        self.detail.handler_info[self.__class__.__name__] = False
        self._log(self.log_message.format(self.union_server, '失败!'), "error")
        self.write_db(False)
        return self.detail, self.service, self.relation_details

    def start_service(self, service):
        for i in range(2):
            state, message = self.salt_client.cmd(
                self.service.ip,
                service.service_controllers.get("start"),
                timeout=settings.SSH_CMD_TIMEOUT
            )
            if not state:
                raise Exception(f"salt执行命令失败，错误输出: {str(message)}")
            time.sleep(10)
            return True

    def handler(self):
        if self.service.is_static:
            self._log("服务无需启动,跳过!")
            return True
        self.start_service(self.service)
        for relation_detail in self.relation_details:
            self.start_service(relation_detail.service)
        return True


"""
升级流程：
    1、停服务
    2、备份服务安装目录
    3、发送服务升级包
    4、解压升级包
    5、调用服务升级流程（参数传目标主机ip、data.json、前一版本version、步骤2的包路径）
    6、启动服务（升级成功以步骤5结果为准）
"""
upgrade_handlers = [
    StartUpgradeHandler,
    StopServiceHandler,
    BackupServiceHandler,
    SendPackageHandler,
    UnzipPackageHandler,
    UpgradeServiceHandler,
    StartServiceHandler
]
