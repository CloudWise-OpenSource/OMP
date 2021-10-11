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
from db_models.models import MonitorUrl, GrafanaMainPage
from utils.parse_config import MONITOR_PORT
from db_models.models import Env
import requests
import json


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
        MonitorUrl(id="1", name="prometheus", monitor_url=local_ip + str(MONITOR_PORT.get("prometheus", "19011"))))
    monitor_list.append(
        MonitorUrl(id="2", name="alertmanager", monitor_url=local_ip + str(MONITOR_PORT.get("alertmanager", "19013"))))
    monitor_list.append(MonitorUrl(
        id="3", name="grafana", monitor_url=local_ip + str(MONITOR_PORT.get("grafana", "19014"))))
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


def synch_grafana_info():
    """如果存在则不再添加,修改会追加一条数据"""
    monitor_ip = MonitorUrl.objects.filter(name="grafana")
    monitor_url = monitor_ip[0].monitor_url if len(
        monitor_ip) else "127.0.0.1:19014"

    token = "Bearer eyJrIjoiWE9tWEhsZ1p6WG41YVd1Mlh1ODF1Qlo2RzNiQkFMR3oiLCJuIjoiYWRtaW4iLCJpZCI6MX0="
    url = """http://{0}/proxy/v1/grafana/api/search?query=&
          starred=false&skipRecent=false&
          skipStarred=false&folderIds=0&layout=folders""".format(monitor_url)
    payload = {}
    headers = {
        'Authorization': token
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    r = json.loads(response.text)

    url_type = {"service": "fu", "node": "zhu", "log": "applogs"}
    url_dict = {}
    for url in r:
        url_name = url.get("uri").rsplit("/", 1)[1].split("-", 1)[0]
        url_dict[url_name.lower()] = url.get("url")

    for key, value in url_type.items():
        url_dict.update({key: url_dict.pop(value)})

    if GrafanaMainPage.objects.all().count() != len(url_dict):
        dbname = [i.instance_name for i in GrafanaMainPage.objects.all()]
        difference = list(set(url_dict.keys()).difference(set(dbname)))
        grafana_obj = [GrafanaMainPage(
            instance_name=i, instance_url=url_dict.get(i)) for i in difference]
        GrafanaMainPage.objects.bulk_create(grafana_obj)


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


if __name__ == '__main__':
    main()
