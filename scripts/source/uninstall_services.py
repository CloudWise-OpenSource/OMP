# -*- coding:utf-8 -*-
# Project: uninstall_services
# Author:Times.niu@yunzhihui.com
# Create time: 2022/1/7 2:37 下午

import os
import sys
import django
import subprocess
import time

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
PYTHON_PATH = os.path.join(PROJECT_DIR, 'component/env/bin/python3')
SALT_KEY_PATH = os.path.join(PROJECT_DIR, "component/env/bin/salt-key")
SALT_CONFIG_PATH = os.path.join(PROJECT_DIR, "config/salt")
sys.path.append(os.path.join(PROJECT_DIR, 'omp_server'))
MAX_NUM = 8

# 加载django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "omp_server.settings")
django.setup()

import logging
from db_models.models import (Service, ApplicationHub, Host, HostOperateLog,
                              PreInstallHistory, DetailInstallHistory,
                              PostInstallHistory, MainInstallHistory, Alert,
                              ExecutionRecord, UpgradeHistory, RollbackDetail,
                              RollbackHistory, UpgradeDetail, DeploymentPlan)
from utils.parse_config import BASIC_ORDER
from services.tasks import exec_action as uninstall_exec_action
from utils.plugin.salt_client import SaltClient
from hosts.tasks import UninstallHosts

logger = logging.getLogger("server")


class UninstallServices(object):
    def __init__(self, env_id):
        self.env_id = env_id
        self.salt_obj = SaltClient()
        self.is_success = True
        self.all_host = Host.objects.filter(env_id=self.env_id)
        self.service_num = Service.objects.filter(env_id=self.env_id).count()

    @staticmethod
    def cmd(command):
        """执行本地shell命令"""
        p = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )
        stdout, stderr = p.communicate()
        _out, _err, _code = stdout.decode(
            "utf8"), stderr.decode("utf8"), p.returncode
        return _out, _err, _code

    def get_all_services(self):
        """通过环境名找到所有的服务"""
        services = Service.objects.filter(env_id=self.env_id)
        if not services:
            return []
        return services

    def get_uninstall_order(self, service_list):
        """卸载服务排序（与安装顺序相反）"""
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

    def uninstall_service(self, item_list):
        """调用卸载函数执行卸载"""
        need_split = ["hadoop"]
        for service_obj in item_list:
            if service_obj and service_obj.service.app_name in need_split:
                delete_objs = Service.objects.filter(ip=service_obj.ip, service__app_name="hadoop")
                status = service_obj.service_status
                delete_objs.update(service_status=Service.SERVICE_STATUS_DELETING)
                if status != Service.SERVICE_STATUS_DELETING \
                        and delete_objs.first().id == service_obj.id:
                    del_file = True
                else:
                    del_file = False
            else:
                del_file = True
            uninstall_exec_action.delay(
                action="4", instance=service_obj.id, operation_user="command_line", del_file=del_file)

    def uninstall_all_services(self, uninstall_list):
        """卸载所有的服务"""
        for item_list in uninstall_list:
            if not item_list:
                continue
            self.uninstall_service(item_list)

    def clean_db(self):
        """清理数据库"""
        HostOperateLog.objects.all().delete()
        self.all_host.delete()
        PreInstallHistory.objects.all().delete()
        DetailInstallHistory.objects.all().delete()
        PostInstallHistory.objects.all().delete()
        MainInstallHistory.objects.all().delete()
        Service.all_objects.all().delete()
        # TODO Alert.objects.filter(env_id=self.env_id).delete()
        Alert.objects.all().delete()
        ExecutionRecord.objects.all().delete()
        RollbackDetail.objects.all().delete()
        RollbackHistory.objects.all().delete()
        UpgradeDetail.objects.all().delete()
        UpgradeHistory.objects.all().delete()
        DeploymentPlan.objects.all().delete()

    def run(self):
        """卸载的总控制函数"""
        service_list = self.get_all_services()
        uninstall_list = self.get_uninstall_order(service_list=service_list)
        self.uninstall_all_services(uninstall_list=uninstall_list)
        for i in range(10):
            if Service.objects.all().count() != 0:
                time.sleep(int(self.service_num))
                print(f"等待服务删除第{i}次")
            else:
                break
        uninstall_host_obj = UninstallHosts(self.all_host)
        self.is_success = uninstall_host_obj.delete_all_omp_agent()
        self.clean_db()
        if not self.is_success:
            raise Exception("本次卸载失败，请按照上述打印信息手动进行卸载")


if __name__ == '__main__':
    env_id = 1
    UninstallServices(env_id).run()
