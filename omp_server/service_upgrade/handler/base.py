import logging
import time
from datetime import datetime
from functools import reduce

from django.conf import settings

from db_models.models import UpgradeDetail, RollbackDetail, Service
from utils.plugin.salt_client import SaltClient

logger = logging.getLogger(__name__)


def get_install_detail(detail, service):
    install_history = service.detailinstallhistory_set.filter(
        install_step_status=2).last()

    if not install_history:
        return None, None

    # 设置安装路径
    install_args = install_history.install_detail_args
    install_folder = ""
    for item in install_args.get("install_args"):
        if item.get("key") == "base_dir":
            install_folder = item.get("default")
            break
    if not install_folder:
        logger.error("找不到服务安装目录!")
        return None, None
    setattr(service, "install_folder", install_folder)

    # 判断静态服务
    setattr(
        service,
        "is_static",
        bool(not service.service_controllers.get("start"))
    )
    # 升级的data path
    setattr(
        detail, "data_path", install_args.get("data_folder")
    )
    # 安装的uuid
    setattr(
        service,
        "_uuid",
        install_history.main_install_history.operation_uuid
    )
    return detail, service


def load_upgrade_detail(upgrade_detail):
    service = upgrade_detail.service
    upgrade_detail, service = get_install_detail(upgrade_detail, service)
    # 加载关联的升级对象
    relation_details = list(
        UpgradeDetail.objects.filter(
            union_server=upgrade_detail.union_server
        ).exclude(id=upgrade_detail.id)
    )
    return upgrade_detail, service, relation_details


def load_rollback_detail(rollback_detail):
    service = rollback_detail.upgrade.service
    # 安装成功记录
    rollback_detail, service = get_install_detail(rollback_detail, service)
    # 加载关联的升级对象
    relation_details = list(
        RollbackDetail.objects.filter(
            upgrade__union_server=rollback_detail.upgrade.union_server
        ).exclude(id=rollback_detail.id).exclude(
            history_id=rollback_detail.history.id
        )
    )
    return rollback_detail, service, relation_details


class BaseHandler:
    log_message = ""
    operation_type = ""
    no_need_print = False

    def __init__(self, salt_client):
        self.salt_client = salt_client

    def _log(self, message, level="info"):
        message = f"\n{' ' * 30}".join(message.split("\n"))
        getattr(logger, level)(message)
        msg_str = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]} " \
                  f"{level.upper()} " \
                  f"{message}"
        # 适配命令行输出
        print(msg_str)
        if not self.detail.message:
            self.detail.message = ""
        self.detail.message += f"{msg_str}\n"
        # todo： 优化下写库？
        self.detail.save()

    def success_handler(self):
        """成功处理"""
        self.detail.handler_info[self.__class__.__name__] = True
        if not (self.service.is_static and self.no_need_print):
            self._log(
                self.log_message.format(self.union_server, '成功!'),
                "info"
            )
        self.write_db(True)
        return self.detail, self.service, self.relation_details

    def fail_handler(self):
        """失败处理"""
        self.detail.handler_info[self.__class__.__name__] = False
        self._log(self.log_message.format(self.union_server, '失败!'), "error")
        self.write_db(False)
        return None

    @classmethod
    def valid_args(cls, detail_args, detail):
        if not isinstance(detail_args, tuple) or len(detail_args) != 3:
            return False
        if not all([
            isinstance(detail_args[0], detail),
            isinstance(detail_args[1], Service)
        ]):
            return False
        return True

    def __call__(self, operation_args, *args, **kwargs):
        if not self.valid_args(operation_args, self.detail_class):
            return None
        self.detail = operation_args[0]
        self.service = operation_args[1]
        self.relation_details = operation_args[2]

        # 执行成功部分跳过
        if self.detail.handler_info.get(self.__class__.__name__):
            return self.detail, self.service, self.relation_details
        if not (self.service.is_static and self.no_need_print):
            self._log(self.log_message.format(
                self.union_server, '中...'), "info"
            )

        try:
            success_state = self.handler()
        except Exception as e:
            self._log(
                f"服务实例:{self.union_server} "
                f"{self.operation_type.lower()}过程中出现异常：{str(e)}",
                "error"
            )
            success_state = False
        if not success_state:
            return self.fail_handler()
        return self.success_handler()


class StartOperationMixin:

    def handler(self):
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


class StopServiceMixin:
    log_message = "服务实例{}: 停止服务{}"
    no_need_print = True

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
            # 回滚有可能服务无包报错,也算停止
            if "[running]" not in message:
                time.sleep(5)
                return True
            time.sleep(5)
        return False


class StartServiceMixin:
    log_message = "服务实例{}: 启动服务{}"
    no_need_print = True

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


def handler_pipeline(handlers, objs):
    """
    升级、回滚处理
    :param handlers: handler类列表: upgrade_handlers, rollback_handlers
    :param objs: 操作对象(upgrade_detail, service)
    :return:
    """
    salt_client = SaltClient()
    return reduce(lambda x, handler: handler(salt_client)(x), handlers, objs)
