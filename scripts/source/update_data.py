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

from django.contrib.auth.hashers import make_password
from db_models.models import UserProfile
from db_models.models import MonitorUrl
from utils.parse_config import MONITOR_PORT

def create_default_user():
    """
    创建基础用户
    :return:
    """
    username = "admin"
    password = "Common@123"
    if UserProfile.objects.filter(username=username).count() != 0:
        return
    UserProfile(
        username=username,
        password=make_password(password),
        email="admin@yunzhihui.com"
    ).save()

def create_default_monitor_url():
    """
    配置监控地址初始入库
    :return:
    """
    if MonitorUrl.objects.all().count() != 0:
        return
    MonitorList=[]
    local_ip="127.0.0.1:"
    MonitorList.append(MonitorUrl(id="1",name="prometheus",monitor_url=local_ip+str(MONITOR_PORT.get("prometheus","19011"))))
    MonitorList.append(MonitorUrl(id="2",name="alertmanager", monitor_url=local_ip+str(MONITOR_PORT.get("alertmanager","19013"))))
    MonitorList.append(MonitorUrl(id="3",name="grafana", monitor_url=local_ip+str(MONITOR_PORT.get("grafana","19014"))))
    MonitorUrl.objects.bulk_create(MonitorList)

def main():
    """
    基础数据创建流程
    :return:
    """
    # 创建默认用户
    create_default_user()
    # 创建监控配置项
    create_default_monitor_url()

if __name__ == '__main__':
    main()
