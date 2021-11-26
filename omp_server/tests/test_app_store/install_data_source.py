# -*- coding: utf-8 -*-
# Project: install_data_source
# Author: jon.liu@yunzhihui.com
# Create time: 2021-11-25 15:47
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
安装过程中的数据
"""

import time
import json
import random
import string

from db_models.models import (
    Host,
    ProductHub,
    ApplicationHub,
    UploadPackageHistory
)


def create_host(ip="127.0.0.1"):
    """
    创建主机对象
    :param ip: ip地址
    :return:
    """
    host_dic = {
        "instance_name": f"host-{ip}",
        "ip": ip,
        "port": 22,
        "username": "root",
        "password": "fake_password",
        "data_folder": "/test",
        "operate_system": "CentOS",
        "host_name": f"hostname-{ip}",
        "agent_dir": "/test"
    }
    host_obj = Host(**host_dic)
    host_obj.save()
    return host_obj


def create_product(pro_name="test", pro_version="1.0.0"):
    """
    创建产品
    :param pro_name: 产品名称
    :param pro_version: 产品版本
    :return:
    """
    _operation_uuid = str(int(time.time()))
    # 创建产品安装包数据
    test_pro_package = {
        "operation_uuid": _operation_uuid,
        "operation_user": "admin",
        "package_name": f"{pro_name}-{pro_version}-20211111-install.tar.gz",
        "package_md5": ''.join(
            random.sample(string.ascii_letters + string.digits, 32)),
        "package_path": "verified",
        "package_status": 3,
        "error_msg": None,
        "package_parent_id": None,
        "is_deleted": 0
    }
    package_obj = UploadPackageHistory(**test_pro_package)
    package_obj.save()

    # 创建产品数据
    test_pro_dic = {
        'is_release': True,
        'pro_name': pro_name,
        'pro_version': pro_version,
        'pro_description': pro_name,
        'pro_dependence': None,
        'pro_services': json.dumps([
            {"name": "ser1", "version": pro_version},
            {"name": "ser2", "version": pro_version},
        ]),
        'pro_logo': None,
        'extend_fields': {},
        'pro_package_id': package_obj.id
    }
    test_product_obj = ProductHub(**test_pro_dic)
    test_product_obj.save()

    create_service(pro_obj=test_product_obj)


def create_service_package(pro_obj, ser_name, ser_version):
    """
    创建服务包
    :param pro_obj:
    :param ser_name:
    :param ser_version:
    :return:
    """
    ser_pack_dic = {
        "operation_uuid": pro_obj.pro_package.operation_uuid,
        "operation_user": "admin",
        "package_name": f"{ser_name}-{ser_version}-2021111-ae8557f.tar.gz",
        "package_md5": ''.join(
            random.sample(string.ascii_letters + string.digits, 32)),
        "package_path": f"verified/{pro_obj.pro_name}-{pro_obj.pro_version}",
        "package_parent_id": pro_obj.pro_package.id,
        "package_status": 0,
        "error_msg": None,
        "is_deleted": 0
    }
    ser_pack_obj = UploadPackageHistory(**ser_pack_dic)
    ser_pack_obj.save()
    return ser_pack_obj


def create_service(pro_obj):
    """
    创建服务
    :param pro_obj:
    :return:
    """
    ser_lst = json.loads(pro_obj.pro_services)
    for item in ser_lst:
        ser_name = item["name"]
        ser_version = item["version"]
        ser_pack_obj = create_service_package(
            pro_obj=pro_obj, ser_name=ser_name, ser_version=ser_version
        )
        ser_dic = {
            "is_release": True,
            "app_type": 1,
            "app_name": ser_name,
            "app_version": ser_version,
            "app_description": ser_name,
            "app_port": json.dumps([
                {
                    "name": "服务端口",
                    "protocol": "TCP",
                    "key": "service_port",
                    "default": "8080"
                }
            ]),
            "app_dependence": json.dumps([
                {
                    "name": "kafka",
                    "version": "2.2.2"
                }
            ]),
            "app_install_args": json.dumps([
                {
                    "name": "安装目录",
                    "key": "base_dir",
                    "default": "{data_path}/app/%s" % ser_name
                },
                {
                    "name": "日志目录",
                    "key": "log_dir",
                    "default": "{data_path}/logs/%s" % ser_name
                },
                {
                    "name": "数据目录",
                    "key": "data_dir",
                    "default": "{data_path}/appData/%s" % ser_name
                },
                {
                    "name": "启动内存",
                    "key": "memory",
                    "default": "1g"
                },
                {
                    "name": "安装用户",
                    "key": "run_user",
                    "default": "commonuser"
                }
            ]),
            "app_controllers": json.dumps({
                "start": f"./bin/{ser_name} start",
                "stop": f"./bin/{ser_name} stop",
                "restart": f"./bin/{ser_name} restart",
                "reload": "",
                "install": "./scripts/install.py",
                "init": "./scripts/init.py"
            }),
            "app_logo": None,
            "extend_fields": {
                "level": "0",
                "deploy": "",
                "affinity": "",
                "resources": "",
                "auto_launch": "True",
                "post_action": "./scripts/bash/registerService.sh"
            },
            "is_base_env": False,
            "app_monitor": {
                "type": "JavaSpringBoot",
                "metric_port": "{service_port}",
                "process_name": ""
            },
            "product": pro_obj,
            "app_package_id": ser_pack_obj.id
        }
        ser_obj = ApplicationHub(**ser_dic)
        ser_obj.save()
