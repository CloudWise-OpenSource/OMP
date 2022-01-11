# -*- coding:utf-8 -*-
# Project: uninstall_services
# Author:Times.niu@yunzhihui.com
# Create time: 2022/1/7 2:37 下午

import os
import sys
import django

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
PYTHON_PATH = os.path.join(PROJECT_DIR, 'component/env/bin/python3')
sys.path.append(os.path.join(PROJECT_DIR, 'omp_server'))

# 加载django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "omp_server.settings")
django.setup()

from db_models.models import Service, ApplicationHub, Host
from utils.parse_config import BASIC_ORDER
from services.tasks import exec_action as uninstall_exec_action


class UninstallServices(object):
    def __init__(self):
        self.ips_list = list()

    # 1.通过环境名找到所有的服务
    def get_all_services(self, env_id):
        services = Service.objects.filter(env_id=env_id)
        if not services:
            return []
        hosts = Host.objects.filter(env_id=env_id)
        self.ips_list = list(set([host.ip for host in hosts]))
        return services

    # 2.卸载服务排序（与安装顺序相反）
    def get_uninstall_order(self, service_list):
        uninstall_list = list()

        # 过滤出自研服务
        self_service = [
            item for item in service_list
            if item.service.app_type == ApplicationHub.APP_TYPE_SERVICE
        ]
        # level不为0 自研服务
        uninstall_list.append(
            [
                item for item in self_service
                if str(item.service.extend_fields.get('level')) != "0"
            ]
        )
        # level为0 自研服务
        uninstall_list.append(
            [
                item for item in self_service
                if str(item.service.extend_fields.get('level')) == "0"
            ]
        )
        # 基础组件
        basic_lists = list()
        for m in range(10):
            if m not in BASIC_ORDER:
                break
            basic_list = [
                item for item in service_list
                if item.service.app_name in BASIC_ORDER[m]
            ]
            basic_lists.append(basic_list)
        basic_lists.reverse()
        uninstall_list.extend(basic_lists)
        return uninstall_list

    # 调用卸载函数执行卸载
    def uninstall_service(self, item_list):
        ids_uninstall_list = [item.id for item in item_list]
        for id in ids_uninstall_list:
            uninstall_exec_action.delay(action="4", instance=id, operation_user="command_line", del_file=True)

    def uninstall_all_services(self, uninstall_list):
        for item_list in uninstall_list:
            if not item_list:
                continue
            self.uninstall_service(item_list)

    def run(self, env_id):
        # 通过env_id获取该环境下的所有服务
        service_list = self.get_all_services(env_id=env_id)
        # 卸载服务排序
        uninstall_list = self.get_uninstall_order(service_list=service_list)
        # 掉用异步celery卸载服务
        self.uninstall_all_services(uninstall_list=uninstall_list)


if __name__ == '__main__':
    env_id = 1
    UninstallServices().run(env_id=env_id)
