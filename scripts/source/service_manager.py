# -*- coding:utf-8 -*-
import os
import sys
import time

import django

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
sys.path.append(os.path.join(PROJECT_DIR, 'omp_server'))
# 加载django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "omp_server.settings")
django.setup()

from services.tasks import exec_action
from db_models.models import Service, ApplicationHub
from concurrent.futures import (
    ThreadPoolExecutor, as_completed
)
from utils.parse_config import BASIC_ORDER
import logging
from utils.plugin.salt_client import SaltClient

logger = logging.getLogger('server')

THREAD_POOL_MAX_WORKERS = 20


def check_result(future_list):
    """
    查看线程结果
    """
    for future in as_completed(future_list):
        ip, message = future.result()
        print(f"{ip} {message}")
    time.sleep(5)


def order(service_obj, actions):
    """
    执行顺序排序
    """
    basic_lists = []
    for m in range(10):
        if m not in BASIC_ORDER:
            break
        basic_list = [
            item for item in service_obj
            if item.service.app_name in BASIC_ORDER[m]
        ]
        basic_lists.append(basic_list)
    self_service = [
        item for item in service_obj
        if item.service.app_type == ApplicationHub.APP_TYPE_SERVICE
    ]
    basic_lists.append(self_service)
    if actions == "stop":
        basic_lists.reverse()
    if actions == "restart":
        basic_copy = basic_lists[:]
        basic_lists.reverse()
        basic_lists.extend(basic_copy)
    return basic_lists


def service_status(service_objs):
    """
    查询全局状态
    """
    salt_obj = SaltClient()
    ips = {}
    for obj in service_objs:
        exec_cmd = obj.service_controllers.get(
            "start", "").replace(" start", " status")
        if not ips.get(obj.ip):
            ips[obj.ip] = exec_cmd
        else:
            ips[obj.ip] = ips.get(obj.ip) + f" && {exec_cmd}"

    for ip, exe_action in ips.items():
        is_success, info = salt_obj.cmd(ip, exe_action, 600)
        print(f"{ip}:{is_success}\n{info}")


def service_actions(actions, ip=None):
    """
    执行服务启停，支持ip筛选
    状态为删除中，安装中，升级中，会滚中状态不被允许执行服务起停操作
    """
    choice = {
        "start": ["1", Service.SERVICE_STATUS_STARTING],
        "stop": ["2", Service.SERVICE_STATUS_STOPPING],
        "restart": ["3", Service.SERVICE_STATUS_RESTARTING]
    }
    action = choice.get(actions)
    actions = "start" if actions == "status" else actions
    service_obj = Service.objects.filter(service_controllers__has_key=actions).exclude(
        service_status__in=[Service.SERVICE_STATUS_INSTALLING,
                            Service.SERVICE_STATUS_UPGRADE,
                            Service.SERVICE_STATUS_ROLLBACK,
                            Service.SERVICE_STATUS_DELETING
                            ]
    ).select_related("service")
    if not action:
        service_status(service_obj)
        return
    if ip:
        service_obj = service_obj.filter(ip=ip)
    service_obj.update(service_status=action[1])
    service_ls = order(service_obj, actions)
    for index, service_ids in enumerate(service_ls):
        # 重启重写
        if actions == "restart":
            if index < len(service_ls) / 2:
                action[0] = "2"
            else:
                action[0] = "1"
        with ThreadPoolExecutor(THREAD_POOL_MAX_WORKERS) as executor:
            future_list = []
            for i in service_ids:
                # print(i.get("service_instance_name"))
                future_obj = executor.submit(
                    exec_action, action[0],
                    i.id, "admin", need_sleep=False
                )
                future_list.append(future_obj)
            check_result(future_list)


if __name__ == '__main__':
    try:
        actions = sys.argv[1:]
        if actions[0] not in ["start", "stop", "restart", "status"]:
            print("请输入正确的(start,stop,restart,status)参数")
            sys.exit(1)
        service_actions(*actions)
    except Exception as err:
        print(f"请输入参数(start,stop,restart,status):{err}")
