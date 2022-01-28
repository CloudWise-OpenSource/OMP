# -*- coding:utf-8 -*-
import os
import re
import sys
import time
from datetime import datetime
import random

import django
from django.db import transaction

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
sys.path.append(os.path.join(PROJECT_DIR, 'omp_server'))
# 加载django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "omp_server.settings")
django.setup()

from app_store.new_install_utils import RedisDB
from app_store.tmp_exec_back_task import back_end_verified_init
from db_models.models import UserProfile, UploadPackageHistory, Service, \
    ApplicationHub, UpgradeHistory, Env, UpgradeDetail, RollbackHistory, \
    RollbackDetail
from db_models.mixins import UpgradeStateChoices, RollbackStateChoices
from service_upgrade.tasks import get_service_order, upgrade_service, \
    rollback_service
from utils.plugin.public_utils import local_cmd


def log_print(message, level="info"):
    msg_str = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]} " \
              f"{level.upper()} " \
              f"{message}"
    print(msg_str)


class BaseOperation:
    services_level_key = "service_levels"
    _lock_key = "operation_lock"

    def __init__(self, service_package, ip=None):
        self.redis = RedisDB()
        self.service_package = service_package
        self.ip = ip

    @property
    def service_level(self):
        if hasattr(self, "_level"):
            return getattr(self, "_level")
        service_level = int(self.app.extend_fields.get("level", 0))
        services_layer = get_service_order()
        level = services_layer.get(self.app_name, None)
        if level is None:
            level = service_level + max(services_layer.values()) + 1
        setattr(self, "_level", level)
        return level

    @property
    def get_services_level(self):
        state, levels = self.redis.get(self.services_level_key)
        if state:
            return levels
        return set()

    def set_levels(self, levels):
        self.redis.set(self.services_level_key, levels)

    def incr(self):
        level_key = f"service_level:{self.service_level}"
        self.redis.conn.incr(level_key)

    def decr(self):
        level_key = f"service_level:{self.service_level}"
        self.redis.conn.decr(level_key)

    def set_app_name(self):
        self.redis.set(self.app_name, True)

    def delete_app_name(self):
        self.redis.delete_keys(self.app_name)

    def get_app_name(self):
        state, data = self.redis.get(self.app_name)
        if state:
            return data
        return False

    def can_operation(self):
        levels = self.get_services_level
        if self.service_level in levels:
            levels.remove(self.service_level)
        can_operation = True
        for i in levels:
            service_level_key = f"service_level:{i}"
            state, service_data = self.redis.get(service_level_key)
            if not state:
                continue
            return False, levels
        levels.add(self.service_level)
        return can_operation, levels

    def _wait(self):
        # 非队列形式，后续优化 & 同时同一服务正在升级或回滚
        while True:
            with self.redis.conn.lock(self._lock_key):
                can_operation, levels = self.can_operation()
                if not can_operation:
                    log_print("存在不同优先级服务在升级/回滚, 稍等片刻...")
                    continue
                operating = self.get_app_name()
                if operating:
                    continue
                self.set_levels(levels)
                self.incr()
                break

    def handle(self):
        pass

    def __call__(self, *args, **kwargs):
        regular = re.compile(r"([a-zA-Z0-9]+)-.*\.tar\.gz")
        service_info = regular.findall(self.service_package)
        if not service_info:
            log_print("服务包包名格式错误！", "error")
            return False
        self.app_name = service_info[0]
        self.services = Service.objects.filter(service__app_name=self.app_name)
        if self.ip:
            self.services = self.services.filter(ip=self.ip)
        if not self.services.exists():
            log_print("环境未安装该服务，请先安装！", "error")
            return False
        return self.handle()


class Upgrade(BaseOperation):
    _valid_lock_key = "valid_package"

    def valid_package(self):
        # 校验服务包会删目录，需要锁,并且保证back_end_verified_path目录下无其他包
        with self.redis.conn.lock(self._valid_lock_key):
            frond_package_path = os.path.join(
                PROJECT_DIR,
                "package_hub/front_end_verified",
                self.service_package
            )
            back_end_verified_path = os.path.join(
                PROJECT_DIR, "package_hub/back_end_verified"
            )
            _cmd_str = f'mv {frond_package_path} {back_end_verified_path}'
            _out, _err, _code = local_cmd(_cmd_str)
            if _code:
                log_print(f"执行移动文件:{_cmd_str}发生错误:{_out}")
            back_end_verified_init(
                operation_user=UserProfile.objects.first().username
            )
            package = UploadPackageHistory.objects.filter(
                package_name=self.service_package
            ).last()
            if not package:
                log_print(f"未找到服务包：{self.service_package}!", "error")
                return None
            while True:
                package.refresh_from_db()
                if package.package_status in [
                    package.PACKAGE_STATUS_FAILED,
                    package.PACKAGE_STATUS_PUBLISH_FAILED
                ]:
                    log_print(
                        f"校验服务包失败，失败详情:{package.error_msg}", "error")
                    return None
                if package.package_status == \
                        package.PACKAGE_STATUS_PUBLISH_SUCCESS:
                    log_print("校验服务包通过！")
                    return ApplicationHub.objects.filter(
                        app_package=package).first()
                log_print("校验服务包中...")
                time.sleep(random.uniform(1, 2))

    def upgrade(self, app):
        # 重新升级，原有升级记录不动
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

    def handle(self):
        app = self.valid_package()
        if not app:
            return False
        self.app = app
        self.services = self.services.exclude(service=app)
        if not self.services.exists():
            log_print("该服务包已被升级！", "error")
            return False
        self._wait()
        history = self.upgrade(app)
        self.decr()
        history.refresh_from_db()
        if history.upgrade_state != UpgradeStateChoices.UPGRADE_SUCCESS:
            return False
        return True


class Rollback(BaseOperation):

    def roll_back(self, upgrade_details):
        with transaction.atomic():
            history = RollbackHistory.objects.create(
                env=Env.objects.first(),
                operator=UserProfile.objects.first()
            )
            RollbackDetail.objects.bulk_create(
                [
                    RollbackDetail(
                        history=history,
                        upgrade_id=upgrade_detail.id
                    )
                    for upgrade_detail in upgrade_details
                ]
            )
        rollback_service(history.id)
        return history

    def handle(self):
        app = ApplicationHub.objects.filter(
            app_package__package_name=self.service_package
        ).first()
        if not app:
            log_print("未找到该服务包相关信息，不可回滚！", "error")
        self.app = app
        details = UpgradeDetail.objects.filter(
            target_app=app,
            upgrade_state__in=[
                UpgradeStateChoices.UPGRADE_SUCCESS,
                UpgradeStateChoices.UPGRADE_FAIL
            ],
            has_rollback=False
        )
        if self.ip:
            details = details.filter(service__ip=self.ip)
        if not details.exists():
            log_print("该服务包无可回滚记录，不可回滚！", "error")
            return False
        can_roll_back_details = []
        for detail in details:
            if not UpgradeDetail.objects.filter(
                service=detail.service,
                id__gt=detail.id,
                has_rollback=False
            ).exists():
                can_roll_back_details.append(detail)
        if not can_roll_back_details:
            log_print("该服务包无可回滚记录，不可回滚！", "error")
            return False
        self._wait()
        history = self.roll_back(can_roll_back_details)
        self.decr()
        history.refresh_from_db()
        if history.rollback_state != RollbackStateChoices.ROLLBACK_SUCCESS:
            return False
        return True


if __name__ == '__main__':
    # env 暂时不考虑
    sys_args = sys.argv[1:]
    if len(sys_args) < 2 or len(sys_args) > 3:
        print("执行命令出错，请执行 "
              "bash cmd_manager [upgrade|rollback] "
              "[服务安装包(如: mysql-xxxxx.tar.gz)] "
              "[服务所在ip(不填默认升级该服务所有实例)]")
        exit(1)
    operation = sys_args[0]
    if operation not in ["rollback", "upgrade"]:
        print("执行命令出错，请执行 "
              "bash cmd_manager [upgrade|rollback] "
              "[服务安装包(如: mysql-xxxxx.tar.gz)] "
              "[服务所在ip(不填默认升级该服务所有实例)]")
        exit(1)
    result = eval(operation.capitalize())(*sys_args[1:])()
    if result:
        log_print("操作成功，即将退出！")
        exit(0)
    log_print("操作失败，即将退出！", "error")
    exit(1)
