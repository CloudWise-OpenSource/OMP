# -*- coding: utf-8 -*-
# Project: update_data
# Author: jon.liu@yunzhihui.com
# Create time: 2021-09-18 10:36
# IDE: PyCharm
# Version: 1.0
# Introduction:

import os
import sys

import django

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
PYTHON_PATH = os.path.join(PROJECT_DIR, "component/env/bin/python3")
MANAGE_PATH = os.path.join(PROJECT_DIR, "omp_server/manage.py")
sys.path.append(os.path.join(PROJECT_DIR, "omp_server"))

# 加载Django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "omp_server.settings")
django.setup()

from db_models.models import UserProfile
from db_models.models import MonitorUrl
from utils.parse_config import MONITOR_PORT
from db_models.models import Env
from db_models.models import HostThreshold
from db_models.models import ServiceThreshold
from db_models.models import ServiceCustomThreshold


def create_default_user():
    """
    创建基础用户
    :return:
    """
    username = "admin"
    password = "Common@123"
    if UserProfile.objects.filter(username=username).count() != 0:
        return
    UserProfile.objects.create_superuser(
        username=username,
        password=password,
        email="admin@yunzhihui.com"
    )


def create_default_monitor_url():
    """
    配置监控地址初始入库
    :return:
    """
    if MonitorUrl.objects.all().count() != 0:
        return
    monitor_list = []
    local_ip = "127.0.0.1:"
    monitor_list.append(
        MonitorUrl(id="1", name="prometheus", monitor_url=local_ip + str(
            MONITOR_PORT.get("prometheus", "19011"))))
    monitor_list.append(
        MonitorUrl(id="2", name="alertmanager", monitor_url=local_ip + str(
            MONITOR_PORT.get("alertmanager", "19013"))))
    monitor_list.append(MonitorUrl(
        id="3", name="grafana",
        monitor_url=local_ip + str(MONITOR_PORT.get("grafana", "19014"))))
    MonitorUrl.objects.bulk_create(monitor_list)


def create_default_env():
    """
    创建默认环境
    :return:
    """
    env_name = "default"
    if Env.objects.filter(name=env_name).count() != 0:
        return
    Env(name=env_name).save()


def create_threshold():
    """
    为告警添加默认的告警阈值规则
    :return:
    """
    host_threshold = [
        {'index_type': 'cpu_used', 'condition': '>=', 'condition_value': '90',
         'alert_level': 'critical'},
        {'index_type': 'cpu_used', 'condition': '>=', 'condition_value': '80',
         'alert_level': 'warning'},
        {'index_type': 'memory_used', 'condition': '>=',
         'condition_value': '90', 'alert_level': 'critical'},
        {'index_type': 'memory_used', 'condition': '>=',
         'condition_value': '80', 'alert_level': 'warning'},
        {'index_type': 'disk_root_used', 'condition': '>=',
         'condition_value': '90', 'alert_level': 'critical'},
        {'index_type': 'disk_root_used', 'condition': '>=',
         'condition_value': '80', 'alert_level': 'warning'},
        {'index_type': 'disk_data_used', 'condition': '>=',
         'condition_value': '90', 'alert_level': 'critical'},
        {'index_type': 'disk_data_used', 'condition': '>=',
         'condition_value': '80', 'alert_level': 'warning'}
    ]
    service_threshold = [
        {'index_type': 'service_active', 'condition': '==',
         'condition_value': 'False', 'alert_level': 'critical'},
        {'index_type': 'service_cpu_used', 'condition': '>=',
         'condition_value': '90', 'alert_level': 'critical'},
        {'index_type': 'service_cpu_used', 'condition': '>=',
         'condition_value': '80', 'alert_level': 'warning'},
        {'index_type': 'service_memory_used', 'condition': '>=',
         'condition_value': '90', 'alert_level': 'critical'},
        {'index_type': 'service_memory_used', 'condition': '>=',
         'condition_value': '80', 'alert_level': 'warning'}]
    custom_threshold = [
        {'index_type': 'kafka_consumergroup_lag', 'condition': '>=',
         'condition_value': '5000', 'alert_level': 'critical'},
        {'index_type': 'kafka_consumergroup_lag', 'condition': '>=',
         'condition_value': '3000', 'alert_level': 'warning'}]
    # 保持更新数据的幂等性
    for item in host_threshold:
        if HostThreshold.objects.filter(
                index_type=item.get("index_type"),
                condition=item.get("condition"),
                alert_level=item.get("alert_level")
        ).exists():
            continue
        HostThreshold(**item).save()

    for item in service_threshold:
        if ServiceThreshold.objects.filter(
                index_type=item.get("index_type"),
                condition=item.get("condition"),
                alert_level=item.get("alert_level")
        ).exists():
            continue
        ServiceThreshold(**item).save()

    for item in custom_threshold:
        if ServiceCustomThreshold.objects.filter(
                index_type=item.get("index_type"),
                condition=item.get("condition"),
                alert_level=item.get("alert_level")
        ).exists():
            continue
        ServiceCustomThreshold(**item).save()


def main():
    """
    基础数据创建流程
    :return:
    """
    # 创建默认用户
    create_default_user()
    # 创建监控配置项
    create_default_monitor_url()
    # 创建默认环境
    create_default_env()
    # 添加默认告警阈值规则
    create_threshold()


if __name__ == '__main__':
    main()
