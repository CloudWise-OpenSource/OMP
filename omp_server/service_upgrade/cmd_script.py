import re
import time
from datetime import datetime

from django.db import transaction

from app_store import tmp_exec_back_task
from db_models.mixins import UpgradeStateChoices
from db_models.models import UserProfile, UploadPackageHistory, \
    ApplicationHub, Service, UpgradeHistory, Env, UpgradeDetail
from service_upgrade.tasks import upgrade_service


def log_print(level, message):
    msg_str = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]} " \
              f"{level.upper()} " \
              f"{message}"
    print(msg_str)


class CmdSingleServiceUpgrade:
    """
    1、校验升级包
    2、生成升级记录
    2、调用升级
    """
    def __init__(self, service_packages, ip=None):
        self.service_packages = service_packages
        regular = re.compile("([a-zA-Z0-9]+)-*.tar.gz")
        service_info = regular.findall(service_packages)
        self.app_name = service_info[0]
        self.services = Service.objects.filter(service__app_name=self.app_name)
        if ip:
            self.services = self.services.filter(ip=ip)

    def valid_package(self):
        tmp_exec_back_task.back_end_verified_init(
            operation_user=UserProfile.objects.first().username
        )

        package = UploadPackageHistory.objects.filter(
            package_name=self.service_packages
        ).last()
        while True:
            package.refresh_from_db()
            if package.package_status in [
                package.PACKAGE_STATUS_FAILED,
                package.PACKAGE_STATUS_PUBLISH_FAILED
            ]:
                log_print("error", f"校验服务包失败，失败详情:{package.error_msg}")
                return None
            if package.package_status == package.PACKAGE_STATUS_PUBLISH_SUCCESS:
                log_print("info", "校验服务包通过！")
                return package
            log_print("info", "校验服务包中...")
            time.sleep(3)

    def upgrade(self):
        app = ApplicationHub.objects.filter(
            app_name=self.app_name,
            app_package=self.service_packages
        ).last()
        if not app:
            log_print("error", f"获取服务升级包失败！")
        with transaction.atomic():
            history = UpgradeHistory.objects.create(
                env=Env.objects.first(),
                operator=UserProfile.objects.first()
            )
            details = []
            for service in self.services:
                details.append(
                    UpgradeDetail(
                        history=history,
                        service_id=service.id,
                        union_server=f"{service.ip}-{self.app_name}",
                        target_app=app,
                        current_app=service.service
                    )
                )
            UpgradeDetail.objects.bulk_create(details)
        upgrade_service(history.id)
        return history

    def run(self):
        state = self.valid_package()
        if not state:
            return False
        history = self.upgrade()
        history.refresh_from_db()
        if history.upgrade_state != UpgradeStateChoices.UPGRADE_SUCCESS:
            return False
        return True
