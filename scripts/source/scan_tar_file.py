# -*- coding:utf-8 -*-
import os
import sys
import time
from datetime import datetime

import django

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
sys.path.append(os.path.join(PROJECT_DIR, 'omp_server'))
# 加载django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "omp_server.settings")
django.setup()

from utils.plugin.public_utils import local_cmd
from app_store.tmp_exec_back_task import back_end_verified_init
from app_store.tmp_exec_back_task import RedisLock
from utils.parse_config import (
    OMP_REDIS_PORT, OMP_REDIS_PASSWORD, OMP_REDIS_HOST
)
from db_models.models import UploadPackageHistory


def log_print(message, level="info"):
    msg_str = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]} " \
              f"{level.upper()} " \
              f"{message}"
    print(msg_str)


class ScanFile:
    def __init__(self):
        self._scan_lock_key = "back_end_verified"
        self._move_lock_key = "mv_back_end_verified"
        self.redis = RedisLock(
            host=OMP_REDIS_HOST, port=OMP_REDIS_PORT,
            password=OMP_REDIS_PASSWORD)
        self.move = True
        self.count = 0

    def valid_package(self):
        while self.move:
            lock, redis_key = self.redis.get_lock(self._move_lock_key)
            if not lock:
                redis_key.lpush(self._move_lock_key, "moving")
                redis_key.expire(self._move_lock_key, 1200)
                self.move = False
            log_print("有安装包正在上传至back_end_verified路径")
            time.sleep(5)

        back_verified = os.path.join(
            PROJECT_DIR, "package_hub/back_end_verified"
        )
        tmp_verified = os.path.join(
            PROJECT_DIR, "package_hub/tmp_end_verified"
        )
        service_name = os.listdir(tmp_verified)
        exec_name = [
            os.path.join(tmp_verified, p) for p in service_name
            if os.path.isfile(os.path.join(tmp_verified, p)) and (p.endswith('.tar') or p.endswith('.tar.gz'))
        ]
        if not exec_name:
            log_print("无需要扫描的安装包，或安装包已被上一个任务获取送出。")
            sys.exit(2)
        while self.redis.get_lock()[0]:
            log_print(f"后台有扫描任务正在执行,等待次数{self.count}。")
            log_print(f"等待扫描安装包列表：{' '.join(exec_name)}")
            time.sleep(5)
            self.count += 1
            if self.count > 100:
                log_print("扫描超时，或队列积压严重，请重试。")
                sys.exit(1)
        try:
            _cmd_str = f'mv {" ".join(exec_name)} {back_verified}'
            _out, _err, _code = local_cmd(_cmd_str)
            if _code:
                log_print(f"执行移动文件:{_cmd_str}发生错误:{_out}")
                sys.exit(1)
            uuid, exec_name = back_end_verified_init(
                operation_user="admin"
            )
            log_print("后台安装包扫描提交至omp")
            result = True
            while result:
                valid_uuids = UploadPackageHistory.objects.filter(
                    operation_uuid=uuid,
                    package_parent__isnull=True,
                ).exclude(
                    package_status__in=[0, 1, 2, 5])
                if valid_uuids.count() == 0:
                    log_print("后台扫描中")
                    time.sleep(5)
                elif 4 in valid_uuids.values_list("package_status", flat=True):
                    log_print("后台扫描校验失败")
                    result = False
                else:
                    log_print("应用商店发布成功")
                    result = False
        except Exception as e:
            log_print(f"后台扫描失败:{e}")
        finally:
            self.redis.rdcon.delete(self._move_lock_key)


if __name__ == "__main__":
    scan = ScanFile()
    scan.valid_package()
