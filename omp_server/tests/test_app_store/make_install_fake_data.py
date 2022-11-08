# -*- coding: utf-8 -*-
# Project: make_fake_data_for_testPro
# Author: jon.liu@yunzhihui.com
# Create time: 2021-11-17 14:53
# IDE: PyCharm
# Version: 1.0
# Introduction:

import os
import json

from db_models.models import (
    Host,
    ProductHub,
    ApplicationHub,
    UploadPackageHistory
)
from omp_server.settings import PROJECT_DIR

# ######################### 测试应用A ################################
# 创建testPro产品安装包数据
testPro_package = {
    "operation_uuid": "1636770501006",
    "operation_user": "admin",
    "package_name": "testPro-5.3.0-ompopen-20211111-install.tar.gz",
    "package_md5": "ca1601ceb5c0682a565120e0d74376f9",
    "package_path": "verified",
    "package_status": 3,
    "error_msg": None,
    "package_parent_id": None,
    "is_deleted": 0
}

# 创建testPro产品安装包对象
testPro_package_obj = UploadPackageHistory(**testPro_package)
testPro_package_obj.save()

# 创建testPro下的服务安装包数据
testPro_services_packages = [
    {
        "operation_uuid": "1636770501006",
        "operation_user": "admin",
        "package_name": "testProApi-2.3.0-20211019113204-ae8557f.tar.gz",
        "package_md5": "b2efb6e605d797e29bb45fc1d7ea376d",
        "package_path": "verified/testPro-5.3.0",
        "package_status": 0,
        "error_msg": None,
        "is_deleted": 0
    },
    {
        "operation_uuid": "1636770501006",
        "operation_user": "admin",
        "package_name": "testProSso-2.3.0-20211019113204-ae8557f.tar.tar.gz",
        "package_md5": "4ec22b75cb963573ef75a80289db32ee",
        "package_path": "verified/testPro-5.3.0",
        "package_status": 0,
        "error_msg": None,
        "is_deleted": 0
    },
    {
        "operation_uuid": "1636770501006",
        "operation_user": "admin",
        "package_name": "testProDubboRpc-2.3.0-20211019113204-ae8557f.tar.gz",
        "package_md5": "bf2aeb1fa188303499a0ec32cc1763b6",
        "package_path": "verified/testPro-5.3.0",
        "package_status": 0,
        "error_msg": None,
        "is_deleted": 0
    },
    {
        "operation_uuid": "1636770501006",
        "operation_user": "admin",
        "package_name": "testProAdmin-2.3.0-20211019113204-ae8557f.tar.gz",
        "package_md5": "49844baddab9c8e610f784c10a500612",
        "package_path": "verified/testPro-5.3.0",
        "package_status": 0,
        "error_msg": None,
        "is_deleted": 0
    },
    {
        "operation_uuid": "1636770501006",
        "operation_user": "admin",
        "package_name": "testProZabbixApi-2.3.0-20211019113204-ae8557f.tar.gz",
        "package_md5": "8404acc041ae783c3798fda1b19321b9",
        "package_path": "verified/testPro-5.3.0",
        "package_status": 0,
        "error_msg": None,
        "is_deleted": 0
    },
    {
        "operation_uuid": "1636770501006",
        "operation_user": "admin",
        "package_name": "testProWeb-2.3.0-20211018115934-5aee074.tar.gz",
        "package_md5": "d924cdc23c7b21eef6d33b9c2572c354",
        "package_path": "verified/testPro-5.3.0",
        "package_status": 0,
        "error_msg": None,
        "is_deleted": 0
    },
    {
        "operation_uuid": "1636770501006",
        "operation_user": "admin",
        "package_name": "testProAdminWeb-2.3.0-20211009023221-748f711.tar.gz",
        "package_md5": "34f6eb46b862701c54e2a8f178afc470",
        "package_path": "verified/testPro-5.3.0",
        "package_status": 0,
        "error_msg": None,
        "is_deleted": 0
    },
    {
        "operation_uuid": "1636770501006",
        "operation_user": "admin",
        "package_name": "gatewayServer-3.1.0-20211016154930-69a1a6c.tar.gz",
        "package_md5": "f8fa68eb4acf31294975f817d4159938",
        "package_path": "verified/testPro-5.3.0",
        "package_status": 0,
        "error_msg": None,
        "is_deleted": 0
    },
    {
        "operation_uuid": "1636770501006",
        "operation_user": "admin",
        "package_name": "gatewayServerApi-3.1.0-20211016154930-69a1a6c.tar.gz",
        "package_md5": "9e124dd9c0eb2b0ad15e6b87f5c2c894",
        "package_path": "verified/testPro-5.3.0",
        "package_status": 0,
        "error_msg": None,
        "is_deleted": 0
    },
    {
        "operation_uuid": "1636770501006",
        "operation_user": "admin",
        "package_name": "portalWeb-5.3.0-20211017051255-2e0af78.tar.gz",
        "package_md5": "ee1a1763e0576e2e496073b4e66fa1c4",
        "package_path": "verified/testPro-5.3.0",
        "package_status": 0,
        "error_msg": None,
        "is_deleted": 0
    },
    {
        "operation_uuid": "1636770501006",
        "operation_user": "admin",
        "package_name": "portalServer-5.3.0-20211014164210-a9f3fba.tar.gz",
        "package_md5": "643102cc5cd6373266f9fde42c33f033",
        "package_path": "verified/testPro-5.3.0",
        "package_status": 0,
        "error_msg": None,
        "is_deleted": 0
    }
]

# 创建testPro下的服务安装包对象
for item in testPro_services_packages:
    item["package_parent_id"] = testPro_package_obj.id
UploadPackageHistory.objects.bulk_create(
    [UploadPackageHistory(**el) for el in testPro_services_packages]
)

# 创建 testPro ProductHub 对象数据
testPro = {
    'is_release': True,
    'pro_name': 'testPro',
    'pro_version': '5.3.0',
    'pro_description': '用户中心（Digital Operation User Center，简称 DOUC',
    'pro_dependence': None,
    'pro_services': json.dumps([
        {"name": "testProApi", "version": "2.3.0"},
        {"name": "testProSso", "version": "2.3.0"},
        {"name": "testProDubboRpc", "version": "2.3.0"},
        {"name": "testProAdmin", "version": "2.3.0"},
        {"name": "testProZabbixApi", "version": "2.3.0"},
        {"name": "testProWeb", "version": "2.3.0"},
        {"name": "testProAdminWeb", "version": "2.3.0"},
        {"name": "gatewayServer", "version": "3.1.0"},
        {"name": "gatewayServerApi", "version": "3.1.0"},
        {"name": "portalWeb", "version": "5.3.0"},
        {"name": "portalServer", "version": "5.3.0"}
    ]),
    'pro_logo': None,
    'extend_fields': {},
    'pro_package_id': testPro_package_obj.id
}
testPro_product_obj = ProductHub(**testPro)
testPro_product_obj.save()

testPro_services_app = [
    {
        "is_release": True,
        "app_type": 1,
        "app_name": "testProApi",
        "app_version": "2.3.0",
        "app_description": None,
        "app_port": [
            {
                "name": "服务端口",
                "protocol": "TCP",
                "key": "service_port",
                "default": "18241"
            },
            {
                "name": "metric端口",
                "protocol": "TCP",
                "key": "metrics_port",
                "default": "18241"
            }
        ],
        "app_dependence": [
            {
                "name": "kafka",
                "version": "2.2.2"
            },
            {
                "name": "nacos",
                "version": "2.0.3"
            },
            {
                "name": "jdk",
                "version": "1.8.0"
            },
            {
                "name": "mysql",
                "version": "5.7.34"
            },
            {
                "name": "rocketmq",
                "version": "5.0"
            },
            {
                "name": "redis",
                "version": "5.0.12"
            }
        ],
        "app_install_args": [
            {
                "name": "安装目录",
                "key": "base_dir",
                "default": "{data_path}/app/testProApi"
            },
            {
                "name": "日志目录",
                "key": "log_dir",
                "default": "{data_path}/logs/testProApi"
            },
            {
                "name": "数据目录",
                "key": "data_dir",
                "default": "{data_path}/appData/testProApi"
            },
            {
                "name": "启动内存",
                "key": "memory",
                "default": "1g"
            },
            {
                "name": "数据库",
                "key": "dbname",
                "default": "cw_testPro"
            },
            {
                "name": "安装用户",
                "key": "run_user",
                "default": "commonuser"
            },
            {
                "name": "kafka_topic名字",
                "key": "kafka_topic",
                "default": "cw-logs"
            }
        ],
        "app_controllers": {
            "start": "./bin/testProApi start",
            "stop": "./bin/testProApi stop",
            "restart": "./bin/testProApi restart",
            "reload": "",
            "install": "./scripts/install.py",
            "init": "./scripts/init.py"
        },
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
        }
    },
    {
        "is_release": True,
        "app_type": 1,
        "app_name": "testProSso",
        "app_version": "2.3.0",
        "app_description": None,
        "app_port": [
            {
                "name": "服务端口",
                "protocol": "TCP",
                "key": "service_port",
                "default": "18256"
            },
            {
                "name": "metric端口",
                "protocol": "TCP",
                "key": "metrics_port",
                "default": "18256"
            }
        ],
        "app_dependence": [
            {
                "name": "kafka",
                "version": "2.2.2"
            },
            {
                "name": "nacos",
                "version": "2.0.3"
            },
            {
                "name": "jdk",
                "version": "1.8.0"
            },
            {
                "name": "mysql",
                "version": "5.7.34"
            }
        ],
        "app_install_args": [
            {
                "name": "安装目录",
                "key": "base_dir",
                "default": "{data_path}/app/testProSso"
            },
            {
                "name": "日志目录",
                "key": "log_dir",
                "default": "{data_path}/logs/testProSso"
            },
            {
                "name": "数据目录",
                "key": "data_dir",
                "default": "{data_path}/appData/testProSso"
            },
            {
                "name": "启动内存",
                "key": "memory",
                "default": "1g"
            },
            {
                "name": "数据库",
                "key": "dbname",
                "default": "cw_testPro"
            },
            {
                "name": "安装用户",
                "key": "run_user",
                "default": "commonuser"
            },
            {
                "name": "kafka_topic名字",
                "key": "kafka_topic",
                "default": "cw-logs"
            }
        ],
        "app_controllers": {
            "start": "./bin/testProSso start",
            "stop": "./bin/testProSso stop",
            "restart": "./bin/testProSso restart",
            "reload": "",
            "install": "./scripts/install.py",
            "init": ""
        },
        "app_package_id": 8,
        "product_id": 1,
        "app_logo": None,
        "extend_fields": {
            "level": "0",
            "deploy": "",
            "affinity": "",
            "resources": "",
            "auto_launch": "True",
            "post_action": ""
        },
        "is_base_env": False,
        "app_monitor": {
            "type": "JavaSpringBoot",
            "metric_port": {
                "service_port": ""
            },
            "process_name": ""
        }
    },
    {
        "is_release": True,
        "app_type": 1,
        "app_name": "testProDubboRpc",
        "app_version": "2.3.0",
        "app_description": None,
        "app_port": [
            {
                "name": "服务端口",
                "protocol": "TCP",
                "key": "service_port",
                "default": "18246"
            },
            {
                "name": "metric端口",
                "protocol": "TCP",
                "key": "metrics_port",
                "default": "18247"
            },
            {
                "name": "test端口",
                "protocol": "TCP",
                "key": "test_port",
                "default": "18247"
            }
        ],
        "app_dependence": [
            {
                "name": "kafka",
                "version": "2.2.2"
            },
            {
                "name": "nacos",
                "version": "2.0.3"
            },
            {
                "name": "jdk",
                "version": "1.8.0"
            },
            {
                "name": "mysql",
                "version": "5.7.34"
            }
        ],
        "app_install_args": [
            {
                "name": "安装目录",
                "key": "base_dir",
                "default": "{data_path}/app/testProDubboRpc"
            },
            {
                "name": "日志目录",
                "key": "log_dir",
                "default": "{data_path}/logs/testProDubboRpc"
            },
            {
                "name": "数据目录",
                "key": "data_dir",
                "default": "{data_path}/appData/testProDubboRpc"
            },
            {
                "name": "启动内存",
                "key": "memory",
                "default": "2g"
            },
            {
                "name": "数据库",
                "key": "dbname",
                "default": "cw_testPro"
            },
            {
                "name": "安装用户",
                "key": "run_user",
                "default": "commonuser"
            },
            {
                "name": "kafka_topic名字",
                "key": "kafka_topic",
                "default": "cw-logs"
            }
        ],
        "app_controllers": {
            "start": "./bin/testProDubboRpc start",
            "stop": "./bin/testProDubboRpc stop",
            "restart": "./bin/testProDubboRpc restart",
            "reload": "",
            "install": "./scripts/install.py",
            "init": ""
        },
        "app_package_id": 9,
        "product_id": 1,
        "app_logo": None,
        "extend_fields": {
            "level": "0",
            "deploy": "",
            "affinity": "",
            "resources": "",
            "auto_launch": "True",
            "post_action": ""
        },
        "is_base_env": False,
        "app_monitor": {
            "type": "JavaSpringBoot",
            "metric_port": {
                "service_port": ""
            },
            "process_name": ""
        }
    },
    {
        "is_release": True,
        "app_type": 1,
        "app_name": "testProAdmin",
        "app_version": "2.3.0",
        "app_description": None,
        "app_port": [
            {
                "name": "服务端口",
                "protocol": "TCP",
                "key": "service_port",
                "default": "18266"
            },
            {
                "name": "metric端口",
                "protocol": "TCP",
                "key": "metrics_port",
                "default": "18266"
            }
        ],
        "app_dependence": [
            {
                "name": "kafka",
                "version": "2.2.2"
            },
            {
                "name": "nacos",
                "version": "2.0.3"
            },
            {
                "name": "jdk",
                "version": "1.8.0"
            },
            {
                "name": "mysql",
                "version": "5.7.34"
            }
        ],
        "app_install_args": [
            {
                "name": "安装目录",
                "key": "base_dir",
                "default": "{data_path}/app/testProAdmin"
            },
            {
                "name": "日志目录",
                "key": "log_dir",
                "default": "{data_path}/logs/testProAdmin"
            },
            {
                "name": "数据目录",
                "key": "data_dir",
                "default": "{data_path}/appData/testProAdmin"
            },
            {
                "name": "启动内存",
                "key": "memory",
                "default": "1g"
            },
            {
                "name": "数据库",
                "key": "dbname",
                "default": "cw_testPro"
            },
            {
                "name": "安装用户",
                "key": "run_user",
                "default": "commonuser"
            },
            {
                "name": "kafka_topic名字",
                "key": "kafka_topic",
                "default": "cw-logs"
            }
        ],
        "app_controllers": {
            "start": "./bin/testProAdmin start",
            "stop": "./bin/testProAdmin stop",
            "restart": "./bin/testProAdmin restart",
            "reload": "",
            "install": "./scripts/install.py",
            "init": ""
        },
        "app_package_id": 10,
        "product_id": 1,
        "app_logo": None,
        "extend_fields": {
            "level": "0",
            "deploy": "",
            "affinity": "",
            "resources": "",
            "auto_launch": "True",
            "post_action": ""
        },
        "is_base_env": False,
        "app_monitor": {
            "type": "JavaSpringBoot",
            "metric_port": {
                "service_port": ""
            },
            "process_name": ""
        }
    },
    {
        "is_release": True,
        "app_type": 1,
        "app_name": "testProZabbixApi",
        "app_version": "2.3.0",
        "app_description": None,
        "app_port": [
            {
                "name": "服务端口",
                "protocol": "TCP",
                "key": "service_port",
                "default": "18260"
            },
            {
                "name": "metric端口",
                "protocol": "TCP",
                "key": "metrics_port",
                "default": "18260"
            },
            {
                "name": "rpc端口",
                "protocol": "TCP",
                "key": "rpc_port",
                "default": "18261"
            }
        ],
        "app_dependence": [
            {
                "name": "kafka",
                "version": "2.2.2"
            },
            {
                "name": "nacos",
                "version": "2.0.3"
            },
            {
                "name": "jdk",
                "version": "1.8.0"
            },
            {
                "name": "mysql",
                "version": "5.7.34"
            }
        ],
        "app_install_args": [
            {
                "name": "安装目录",
                "key": "base_dir",
                "default": "{data_path}/app/testProZabbixApi"
            },
            {
                "name": "日志目录",
                "key": "log_dir",
                "default": "{data_path}/logs/testProZabbixApi"
            },
            {
                "name": "数据目录",
                "key": "data_dir",
                "default": "{data_path}/appData/testProZabbixApi"
            },
            {
                "name": "启动内存",
                "key": "memory",
                "default": "1g"
            },
            {
                "name": "数据库",
                "key": "dbname",
                "default": "cw_testPro"
            },
            {
                "name": "安装用户",
                "key": "run_user",
                "default": "commonuser"
            },
            {
                "name": "kafka_topic名字",
                "key": "kafka_topic",
                "default": "cw-logs"
            }
        ],
        "app_controllers": {
            "start": "./bin/testProZabbixApi start",
            "stop": "./bin/testProZabbixApi stop",
            "restart": "./bin/testProZabbixApi restart",
            "reload": "",
            "install": "./scripts/install.py",
            "init": ""
        },
        "app_package_id": 11,
        "product_id": 1,
        "app_logo": None,
        "extend_fields": {
            "level": "0",
            "deploy": "",
            "affinity": "",
            "resources": "",
            "auto_launch": "True",
            "post_action": ""
        },
        "is_base_env": False,
        "app_monitor": {
            "type": "JavaSpringBoot",
            "metric_port": {
                "service_port": ""
            },
            "process_name": ""
        }
    },
    {
        "is_release": True,
        "app_type": 1,
        "app_name": "testProWeb",
        "app_version": "2.3.0",
        "app_description": None,
        "app_port": None,
        "app_dependence": [
            {
                "name": "portalWeb",
                "version": "5.3.0"
            },
            {
                "name": "tengine",
                "version": "1.20.1"
            }
        ],
        "app_install_args": [
            {
                "name": "安装目录",
                "key": "base_dir",
                "default": "{data_path}/app/testProWeb"
            }
        ],
        "app_controllers": {
            "start": "",
            "stop": "",
            "restart": "",
            "reload": "",
            "install": "./scripts/install.py",
            "init": ""
        },
        "app_package_id": 12,
        "product_id": 1,
        "app_logo": None,
        "extend_fields": {
            "level": "1",
            "deploy": "",
            "affinity": "portalWeb",
            "resources": "",
            "auto_launch": "False",
            "post_action": ""
        },
        "is_base_env": False,
        "app_monitor": None
    },
    {
        "is_release": True,
        "app_type": 1,
        "app_name": "testProAdminWeb",
        "app_version": "2.3.0",
        "app_description": None,
        "app_port": None,
        "app_dependence": [
            {
                "name": "portalWeb",
                "version": "5.3.0"
            },
            {
                "name": "tengine",
                "version": "1.20.1"
            }
        ],
        "app_install_args": [
            {
                "name": "安装目录",
                "key": "base_dir",
                "default": "{data_path}/app/testProAdminWeb"
            }
        ],
        "app_controllers": {
            "start": "",
            "stop": "",
            "restart": "",
            "reload": "",
            "install": "./scripts/install.py",
            "init": ""
        },
        "app_package_id": 13,
        "product_id": 1,
        "app_logo": None,
        "extend_fields": {
            "level": "1",
            "deploy": "",
            "affinity": "portalWeb",
            "resources": "",
            "auto_launch": "False",
            "post_action": ""
        },
        "is_base_env": False,
        "app_monitor": None
    },
    {
        "is_release": True,
        "app_type": 1,
        "app_name": "gatewayServer",
        "app_version": "3.1.0",
        "app_description": None,
        "app_port": [
            {
                "name": "服务端口",
                "protocol": "TCP",
                "key": "service_port",
                "default": "18201"
            },
            {
                "name": "metric端口",
                "protocol": "TCP",
                "key": "metrics_port",
                "default": "18202"
            },
            {
                "name": "devtools端口",
                "protocol": "TCP",
                "key": "devtools_port",
                "default": "18203"
            },
            {
                "name": "sentinel端口",
                "protocol": "TCP",
                "key": "sentinel_port",
                "default": "18208"
            }
        ],
        "app_dependence": [
            {
                "name": "kafka",
                "version": "2.2.2"
            },
            {
                "name": "nacos",
                "version": "2.0.3"
            },
            {
                "name": "jdk",
                "version": "1.8.0"
            },
            {
                "name": "tengine",
                "version": "1.20.1"
            }
        ],
        "app_install_args": [
            {
                "name": "安装目录",
                "key": "base_dir",
                "default": "{data_path}/app/gatewayServer"
            },
            {
                "name": "日志目录",
                "key": "log_dir",
                "default": "{data_path}/logs/gatewayServer"
            },
            {
                "name": "数据目录",
                "key": "data_dir",
                "default": "{data_path}/appData/gatewayServer"
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
            },
            {
                "name": "kafka_topic名字",
                "key": "kafka_topic",
                "default": "cw-logs"
            }
        ],
        "app_controllers": {
            "start": "./bin/gatewayServer start",
            "stop": "./bin/gatewayServer stop",
            "restart": "./bin/gatewayServer restart",
            "reload": "",
            "install": "./scripts/install.py",
            "init": ""
        },
        "app_package_id": 14,
        "product_id": 1,
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
            "metric_port": {
                "service_port": ""
            },
            "process_name": ""
        }
    },
    {
        "is_release": True,
        "app_type": 1,
        "app_name": "gatewayServerApi",
        "app_version": "3.1.0",
        "app_description": None,
        "app_port": [
            {
                "name": "服务端口",
                "protocol": "TCP",
                "key": "service_port",
                "default": "18204"
            },
            {
                "name": "metric端口",
                "protocol": "TCP",
                "key": "metrics_port",
                "default": "18205"
            },
            {
                "name": "devtools端口",
                "protocol": "TCP",
                "key": "devtools_port",
                "default": "18207"
            },
            {
                "name": "sentinel端口",
                "protocol": "TCP",
                "key": "sentinel_port",
                "default": "18209"
            }
        ],
        "app_dependence": [
            {
                "name": "kafka",
                "version": "2.2.2"
            },
            {
                "name": "nacos",
                "version": "2.0.3"
            },
            {
                "name": "jdk",
                "version": "1.8.0"
            },
            {
                "name": "tengine",
                "version": "1.20.1"
            }
        ],
        "app_install_args": [
            {
                "name": "安装目录",
                "key": "base_dir",
                "default": "{data_path}/app/gatewayServerApi"
            },
            {
                "name": "日志目录",
                "key": "log_dir",
                "default": "{data_path}/logs/gatewayServerApi"
            },
            {
                "name": "数据目录",
                "key": "data_dir",
                "default": "{data_path}/appData/gatewayServerApi"
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
            },
            {
                "name": "kafka_topic名字",
                "key": "kafka_topic",
                "default": "cw-logs"
            }
        ],
        "app_controllers": {
            "start": "./bin/gatewayServerApi start",
            "stop": "./bin/gatewayServerApi stop",
            "restart": "./bin/gatewayServerApi restart",
            "reload": "",
            "install": "./scripts/install.py",
            "init": ""
        },
        "app_package_id": 15,
        "product_id": 1,
        "app_logo": None,
        "extend_fields": {
            "level": "0",
            "deploy": "",
            "affinity": "",
            "resources": "",
            "auto_launch": "True",
            "post_action": ""
        },
        "is_base_env": False,
        "app_monitor": {
            "type": "JavaSpringBoot",
            "metric_port": {
                "service_port": ""
            },
            "process_name": ""
        }
    },
    {
        "is_release": True,
        "app_type": 1,
        "app_name": "portalWeb",
        "app_version": "5.3.0",
        "app_description": None,
        "app_port": None,
        "app_dependence": None,
        "app_install_args": [
            {
                "name": "安装目录",
                "key": "base_dir",
                "default": "{data_path}/app/portalWeb"
            }
        ],
        "app_controllers": {
            "start": "",
            "stop": "",
            "restart": "",
            "reload": "",
            "install": "./scripts/install.py",
            "init": ""
        },
        "app_package_id": 16,
        "product_id": 1,
        "app_logo": None,
        "extend_fields": {
            "level": "0",
            "deploy": "",
            "affinity": "",
            "resources": "",
            "auto_launch": "False",
            "post_action": ""
        },
        "is_base_env": False,
        "app_monitor": None
    },
    {
        "is_release": True,
        "app_type": 1,
        "app_name": "portalServer",
        "app_version": "5.3.0",
        "app_description": None,
        "app_port": [
            {
                "name": "服务端口",
                "protocol": "TCP",
                "key": "service_port",
                "default": "18206"
            },
            {
                "name": "metric端口",
                "protocol": "TCP",
                "key": "metrics_port",
                "default": "18206"
            }
        ],
        "app_dependence": [
            {
                "name": "kafka",
                "version": "2.2.2"
            },
            {
                "name": "nacos",
                "version": "2.0.3"
            },
            {
                "name": "jdk",
                "version": "1.8.0"
            },
            {
                "name": "mysql",
                "version": "5.7.34"
            }
        ],
        "app_install_args": [
            {
                "name": "安装目录",
                "key": "base_dir",
                "default": "{data_path}/app/portalServer"
            },
            {
                "name": "日志目录",
                "key": "log_dir",
                "default": "{data_path}/logs/portalServer"
            },
            {
                "name": "数据目录",
                "key": "data_dir",
                "default": "{data_path}/appData/portalServer"
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
            },
            {
                "name": "kafka_topic名字",
                "key": "kafka_topic",
                "default": "cw-logs"
            },
            {
                "name": "数据库名",
                "key": "dbname",
                "default": "cw_portal"
            }
        ],
        "app_controllers": {
            "start": "./bin/portalServer start",
            "stop": "./bin/portalServer stop",
            "restart": "./bin/portalServer restart",
            "reload": "",
            "install": "./scripts/install.py",
            "init": "./scripts/init.py"
        },
        "app_package_id": 17,
        "product_id": 1,
        "app_logo": None,
        "extend_fields": {
            "level": "0",
            "deploy": "",
            "affinity": "",
            "resources": "",
            "auto_launch": "True",
            "post_action": ""
        },
        "is_base_env": False,
        "app_monitor": {
            "type": "JavaSpringBoot",
            "metric_port": {
                "service_port": ""
            },
            "process_name": ""
        }
    }
]

for item in testPro_services_app:
    item["product_id"] = testPro_product_obj.id
    item["app_package_id"] = UploadPackageHistory.objects.filter(
        package_name__startswith=f"{item['app_name']}-{item['app_version']}"
    ).last().id
    if item["app_port"]:
        item["app_port"] = json.dumps(item["app_port"])
    if item["app_dependence"]:
        item["app_dependence"] = json.dumps(item["app_dependence"])
    if item["app_install_args"]:
        item["app_install_args"] = json.dumps(item["app_install_args"])
    if item["app_controllers"]:
        item["app_controllers"] = json.dumps(item["app_controllers"])

ApplicationHub.objects.bulk_create(
    [ApplicationHub(**el) for el in testPro_services_app]
)

# ######################### 测试应用A ################################

# ######################### 测试应用B ################################

testProB_package = {
    "operation_uuid": "1636770501006",
    "operation_user": "admin",
    "package_name": "testProB-5.3.0-ompopen-20211111-install.tar.gz",
    "package_md5": "ca1601ceb5c0682a565220e0d74376f9",
    "package_path": "verified",
    "package_status": 3,
    "error_msg": None,
    "package_parent_id": None,
    "is_deleted": 0
}
testProB_package_obj = UploadPackageHistory(**testProB_package)
testProB_package_obj.save()

testProB_services_packages = [
    {
        "operation_uuid": "1636770501006",
        "operation_user": "admin",
        "package_name": "testProBServer-2.3.0-20211019113204-ae8557f.tar.gz",
        "package_md5": "b2efb6e605d797f29bb45fc1d7ea376d",
        "package_path": "verified/testProB-5.3.0",
        "package_status": 0,
        "error_msg": None,
        "is_deleted": 0
    },
    {
        "operation_uuid": "1636770501006",
        "operation_user": "admin",
        "package_name": "testProBWeb-2.3.0-20211019113204-ae8557f.tar.tar.gz",
        "package_md5": "4ec22b75cb9f3573ef75a80289db32ee",
        "package_path": "verified/testProB-5.3.0",
        "package_status": 0,
        "error_msg": None,
        "is_deleted": 0
    }
]

for item in testProB_services_packages:
    item["package_parent_id"] = testProB_package_obj.id
UploadPackageHistory.objects.bulk_create(
    [UploadPackageHistory(**el) for el in testProB_services_packages]
)

testProB = {
    'is_release': True,
    'pro_name': 'testProB',
    'pro_version': '5.3.0',
    'pro_description': '配置中心',
    'pro_dependence': json.dumps([
        {
            "name": "testPro",
            "version": "5.3.0"
        }
    ]),
    'pro_services': json.dumps([
        {"name": "testProBServer", "version": "2.3.0"},
        {"name": "testProBWeb", "version": "2.3.0"}
    ]),
    'pro_logo': None,
    'extend_fields': {},
    'pro_package_id': testProB_package_obj.id
}
testProB_product_obj = ProductHub(**testProB)
testProB_product_obj.save()

testProB_services_app = [
    {
        "is_release": True,
        "app_type": 1,
        "app_name": "testProBServer",
        "app_version": "2.3.0",
        "app_description": None,
        "app_port": [
            {
                "name": "服务端口",
                "protocol": "TCP",
                "key": "service_port",
                "default": "18341"
            },
            {
                "name": "metric端口",
                "protocol": "TCP",
                "key": "metrics_port",
                "default": "18352"
            }
        ],
        "app_dependence": [
            {
                "name": "nacos",
                "version": "2.0.3"
            },
            {
                "name": "jdk",
                "version": "1.8.0"
            },
            {
                "name": "mysql",
                "version": "5.7.34"
            },
            {
                "name": "arangodb",
                "version": "3.6.5"
            },
            {
                "name": "redis",
                "version": "5.0.12"
            }
        ],
        "app_install_args": [
            {
                "name": "安装目录",
                "key": "base_dir",
                "default": "{data_path}/app/testProBServer"
            },
            {
                "name": "日志目录",
                "key": "log_dir",
                "default": "{data_path}/logs/testProBServer"
            },
            {
                "name": "数据目录",
                "key": "data_dir",
                "default": "{data_path}/appData/testProBServer"
            },
            {
                "name": "启动内存",
                "key": "memory",
                "default": "1g"
            },
            {
                "name": "数据库",
                "key": "dbname",
                "default": "cw_testProB"
            },
            {
                "name": "安装用户",
                "key": "run_user",
                "default": "commonuser"
            }
        ],
        "app_controllers": {
            "start": "./bin/testProBServer start",
            "stop": "./bin/testProBServer stop",
            "restart": "./bin/testProBServer restart",
            "reload": "",
            "install": "./scripts/install.py",
            "init": "./scripts/init.py"
        },
        "app_logo": None,
        "extend_fields": {
            "level": "0",
            "deploy": "",
            "affinity": "",
            "resources": "",
            "auto_launch": "True",
            "post_action": ""
        },
        "is_base_env": False,
        "app_monitor": {
            "type": "JavaSpringBoot",
            "metric_port": "{service_port}",
            "process_name": ""
        }
    },
    {
        "is_release": True,
        "app_type": 1,
        "app_name": "testProBWeb",
        "app_version": "2.3.0",
        "app_description": None,
        "app_port": None,
        "app_dependence": None,
        "app_install_args": [
            {
                "name": "安装目录",
                "key": "base_dir",
                "default": "{data_path}/app/testProBWeb"
            }
        ],
        "app_controllers": {
            "start": "",
            "stop": "",
            "restart": "",
            "reload": "",
            "install": "./scripts/install.py",
            "init": ""
        },
        "app_package_id": 16,
        "product_id": 1,
        "app_logo": None,
        "extend_fields": {
            "level": "0",
            "deploy": "",
            "affinity": "",
            "resources": "",
            "auto_launch": "False",
            "post_action": ""
        },
        "is_base_env": False,
        "app_monitor": None
    },
]

for item in testProB_services_app:
    item["product_id"] = testProB_product_obj.id
    item["app_package_id"] = UploadPackageHistory.objects.filter(
        package_name__startswith=f"{item['app_name']}-{item['app_version']}"
    ).last().id
    if item["app_port"]:
        item["app_port"] = json.dumps(item["app_port"])
    if item["app_dependence"]:
        item["app_dependence"] = json.dumps(item["app_dependence"])
    if item["app_install_args"]:
        item["app_install_args"] = json.dumps(item["app_install_args"])
    if item["app_controllers"]:
        item["app_controllers"] = json.dumps(item["app_controllers"])

ApplicationHub.objects.bulk_create(
    [ApplicationHub(**el) for el in testProB_services_app]
)

# ######################### 测试应用B ################################

# 公共组件部分
jdk_package = {
    "operation_uuid": "1636770501006",
    "operation_user": "admin",
    "package_name": "jdk-1.8.0-20211019113204-ae8557f.tar.gz",
    "package_md5": "b2efb6e604d797e29bb45fc1d7ea376d",
    "package_path": "verified",
    "package_status": 0,
    "error_msg": None,
    "is_deleted": 0
}
jdk_package_obj = UploadPackageHistory(**jdk_package)
jdk_package_obj.save()
jdk_app = {
    "is_release": True,
    "app_type": 0,
    "app_name": "jdk",
    "app_version": "1.8.0",
    "app_description": "jdk",
    "app_port": None,
    "app_dependence": None,
    "app_install_args": json.dumps([
        {
            "name": "安装目录",
            "key": "base_dir",
            "default": "{data_path}/app/jdk"
        }
    ]),
    "app_controllers": json.dumps({
        "start": "",
        "stop": "",
        "restart": "",
        "reload": "",
        "install": "./scripts/install.py",
        "init": ""
    }),
    "app_logo": None,
    "extend_fields": {
        "deploy": "",
        "affinity": "",
        "resources": "",
        "auto_launch": "True",
        "post_action": "",
        "is_base_env": True
    },
    "is_base_env": True,
    "app_monitor": {
        "type": "",
        "metric_port": "",
        "process_name": ""
    },
    "app_package_id": jdk_package_obj.id
}
ApplicationHub.objects.create(**jdk_app)

mysql_package = {
    "operation_uuid": "1636770501006",
    "operation_user": "admin",
    "package_name": "mysql-5.7.34-20211019113204-ae8557f.tar.gz",
    "package_md5": "b2efb6e605d797e29bb45fc1d7ea376d",
    "package_path": "verified",
    "package_status": 0,
    "error_msg": None,
    "is_deleted": 0
}
mysql_package_obj = UploadPackageHistory(**mysql_package)
mysql_package_obj.save()
mysql_app = {
    "is_release": True,
    "app_type": 0,
    "app_name": "mysql",
    "app_version": "5.7.34",
    "app_description": "mysql数据库",
    "app_port": json.dumps([
        {
            "name": "服务端口",
            "protocol": "TCP",
            "key": "service_port",
            "default": "18103"
        }
    ]),
    "app_dependence": None,
    "app_install_args": json.dumps([
        {
            "name": "安装目录",
            "key": "base_dir",
            "default": "{data_path}/app/mysql"
        },
        {
            "name": "日志目录",
            "key": "log_dir",
            "default": "{data_path}/logs/mysql"
        },
        {
            "name": "数据目录",
            "key": "data_dir",
            "default": "{data_path}/appData/mysql"
        },
        {
            "name": "安装用户",
            "key": "run_user",
            "default": "commonuser"
        }
    ]),
    "app_controllers": json.dumps({
        "start": "./scripts/mysql start",
        "stop": "./scripts/mysql stop",
        "restart": "./scripts/mysql restart",
        "reload": "",
        "install": "./scripts/install.py",
        "init": "./scripts/init.py"
    }),
    "app_logo": None,
    "extend_fields": {
        "deploy": "",
        "affinity": "",
        "resources": "",
        "auto_launch": "True",
        "post_action": ""
    },
    "is_base_env": False,
    "app_monitor": {
        "type": "",
        "metric_port": "{service_port}",
        "process_name": ""
    },
    "app_package_id": mysql_package_obj.id
}
ApplicationHub.objects.create(**mysql_app)

nacos_package = {
    "operation_uuid": "1636770501006",
    "operation_user": "admin",
    "package_name": "nacos-2.0.3-20211019113204-ae8557f.tar.gz",
    "package_md5": "b2efb6e605d697e29bb45fc1d7ea376d",
    "package_path": "verified",
    "package_status": 0,
    "error_msg": None,
    "is_deleted": 0
}
nacos_package_obj = UploadPackageHistory(**nacos_package)
nacos_package_obj.save()
nacos_app = {
    "is_release": True,
    "app_type": 0,
    "app_name": "nacos",
    "app_version": "2.0.3",
    "app_description": "",
    "app_port": json.dumps([
        {
            "name": "服务端口",
            "protocol": "TCP",
            "key": "service_port",
            "default": "18117"
        }
    ]),
    "app_dependence": json.dumps([{
        "name": "jdk",
        "version": "1.8.0"
    }]),
    "app_install_args": json.dumps([
        {
            "name": "安装目录",
            "key": "base_dir",
            "default": "{data_path}/app/nacos"
        },
        {
            "name": "日志目录",
            "key": "log_dir",
            "default": "{data_path}/logs/nacos"
        },
        {
            "name": "数据目录",
            "key": "data_dir",
            "default": "{data_path}/appData/nacos"
        },
        {
            "name": "安装用户",
            "key": "run_user",
            "default": "commonuser"
        }
    ]),
    "app_controllers": json.dumps({
        "start": "./scripts/nacos start",
        "stop": "./scripts/nacos stop",
        "restart": "./scripts/nacos restart",
        "reload": "",
        "install": "./scripts/install.py",
        "init": "./scripts/init.py"
    }),
    "app_logo": None,
    "extend_fields": {
        "deploy": "",
        "affinity": "",
        "resources": "",
        "auto_launch": "True",
        "post_action": ""
    },
    "is_base_env": False,
    "app_monitor": {
        "type": "",
        "metric_port": "{service_port}",
        "process_name": ""
    },
    "app_package_id": nacos_package_obj.id
}
ApplicationHub.objects.create(**nacos_app)

kafka_package = {
    "operation_uuid": "1636770501006",
    "operation_user": "admin",
    "package_name": "kafka-2.2.2-20211019113204-ae8557f.tar.gz",
    "package_md5": "b2eb6e605d697e29bb45fc1d7ea376d",
    "package_path": "verified",
    "package_status": 0,
    "error_msg": None,
    "is_deleted": 0
}
kafka_package_obj = UploadPackageHistory(**kafka_package)
kafka_package_obj.save()
kafka_app = {
    "is_release": True,
    "app_type": 0,
    "app_name": "kafka",
    "app_version": "2.2.2",
    "app_description": "",
    "app_port": json.dumps([
        {
            "name": "服务端口",
            "protocol": "TCP",
            "key": "service_port",
            "default": "18217"
        }
    ]),
    "app_dependence": json.dumps([
        {
            "name": "jdk",
            "version": "1.8.0"
        },
        {
            "name": "zookeeper",
            "version": "1.2.2"
        }
    ]),
    "app_install_args": json.dumps([
        {
            "name": "安装目录",
            "key": "base_dir",
            "default": "{data_path}/app/kafka"
        },
        {
            "name": "日志目录",
            "key": "log_dir",
            "default": "{data_path}/logs/kafka"
        },
        {
            "name": "数据目录",
            "key": "data_dir",
            "default": "{data_path}/appData/kafka"
        },
        {
            "name": "安装用户",
            "key": "run_user",
            "default": "commonuser"
        }
    ]),
    "app_controllers": json.dumps({
        "start": "./scripts/kafka start",
        "stop": "./scripts/kafka stop",
        "restart": "./scripts/kafka restart",
        "reload": "",
        "install": "./scripts/install.py",
        "init": "./scripts/init.py"
    }),
    "app_logo": None,
    "extend_fields": {
        "deploy": "",
        "affinity": "",
        "resources": "",
        "auto_launch": "True",
        "post_action": ""
    },
    "is_base_env": False,
    "app_monitor": {
        "type": "",
        "metric_port": "{service_port}",
        "process_name": ""
    },
    "app_package_id": kafka_package_obj.id
}
ApplicationHub.objects.create(**kafka_app)

zookeeper_package = {
    "operation_uuid": "1636770501006",
    "operation_user": "admin",
    "package_name": "zookeeper-1.2.2-20211019113204-ae8557f.tar.gz",
    "package_md5": "b2eb6e605d697f29bb45fc1d7ea376d",
    "package_path": "verified",
    "package_status": 0,
    "error_msg": None,
    "is_deleted": 0
}
zookeeper_package_obj = UploadPackageHistory(**zookeeper_package)
zookeeper_package_obj.save()
zookeeper_app = {
    "is_release": True,
    "app_type": 0,
    "app_name": "zookeeper",
    "app_version": "1.2.2",
    "app_description": "",
    "app_port": json.dumps([
        {
            "name": "服务端口",
            "protocol": "TCP",
            "key": "service_port",
            "default": "18227"
        }
    ]),
    "app_dependence": json.dumps([{
        "name": "jdk",
        "version": "1.8.0"
    }]),
    "app_install_args": json.dumps([
        {
            "name": "安装目录",
            "key": "base_dir",
            "default": "{data_path}/app/zookeeper"
        },
        {
            "name": "日志目录",
            "key": "log_dir",
            "default": "{data_path}/logs/zookeeper"
        },
        {
            "name": "数据目录",
            "key": "data_dir",
            "default": "{data_path}/appData/zookeeper"
        },
        {
            "name": "安装用户",
            "key": "run_user",
            "default": "commonuser"
        }
    ]),
    "app_controllers": json.dumps({
        "start": "./scripts/zookeeper start",
        "stop": "./scripts/zookeeper stop",
        "restart": "./scripts/zookeeper restart",
        "reload": "",
        "install": "./scripts/install.py",
        "init": "./scripts/init.py"
    }),
    "app_logo": None,
    "extend_fields": {
        "deploy": "",
        "affinity": "",
        "resources": "",
        "auto_launch": "True",
        "post_action": ""
    },
    "is_base_env": False,
    "app_monitor": {
        "type": "",
        "metric_port": "{service_port}",
        "process_name": ""
    },
    "app_package_id": zookeeper_package_obj.id
}
ApplicationHub.objects.create(**zookeeper_app)

redis_package = {
    "operation_uuid": "1636770501006",
    "operation_user": "admin",
    "package_name": "redis-5.0.12-20211019113204-ae8557f.tar.gz",
    "package_md5": "b2eb6e605d697f29bb45fd1d7ea376d",
    "package_path": "verified",
    "package_status": 0,
    "error_msg": None,
    "is_deleted": 0
}
redis_package_obj = UploadPackageHistory(**redis_package)
redis_package_obj.save()
redis_app = {
    "is_release": True,
    "app_type": 0,
    "app_name": "redis",
    "app_version": "5.0.12",
    "app_description": "",
    "app_port": json.dumps([
        {
            "name": "服务端口",
            "protocol": "TCP",
            "key": "service_port",
            "default": "18137"
        }
    ]),
    "app_dependence": None,
    "app_install_args": json.dumps([
        {
            "name": "安装目录",
            "key": "base_dir",
            "default": "{data_path}/app/redis"
        },
        {
            "name": "日志目录",
            "key": "log_dir",
            "default": "{data_path}/logs/redis"
        },
        {
            "name": "数据目录",
            "key": "data_dir",
            "default": "{data_path}/appData/redis"
        },
        {
            "name": "安装用户",
            "key": "run_user",
            "default": "commonuser"
        }
    ]),
    "app_controllers": json.dumps({
        "start": "./scripts/redis start",
        "stop": "./scripts/redis stop",
        "restart": "./scripts/redis restart",
        "reload": "",
        "install": "./scripts/install.py",
        "init": "./scripts/init.py"
    }),
    "app_logo": None,
    "extend_fields": {
        "deploy": "",
        "affinity": "",
        "resources": "",
        "auto_launch": "True",
        "post_action": ""
    },
    "is_base_env": False,
    "app_monitor": {
        "type": "",
        "metric_port": "{service_port}",
        "process_name": ""
    },
    "app_package_id": redis_package_obj.id
}
ApplicationHub.objects.create(**redis_app)

rocketmq_package = {
    "operation_uuid": "1636770501006",
    "operation_user": "admin",
    "package_name": "rocketmq-5.0-20211019113204-ae8557f.tar.gz",
    "package_md5": "b2eb6e605d697f29bb45fd1d7ea376d",
    "package_path": "verified",
    "package_status": 0,
    "error_msg": None,
    "is_deleted": 0
}
rocketmq_package_obj = UploadPackageHistory(**rocketmq_package)
rocketmq_package_obj.save()
rocketmq_app = {
    "is_release": True,
    "app_type": 0,
    "app_name": "rocketmq",
    "app_version": "5.0",
    "app_description": "",
    "app_port": json.dumps([
        {
            "name": "服务端口",
            "protocol": "TCP",
            "key": "service_port",
            "default": "18147"
        }
    ]),
    "app_dependence": None,
    "app_install_args": json.dumps([
        {
            "name": "安装目录",
            "key": "base_dir",
            "default": "{data_path}/app/rocketmq"
        },
        {
            "name": "日志目录",
            "key": "log_dir",
            "default": "{data_path}/logs/rocketmq"
        },
        {
            "name": "数据目录",
            "key": "data_dir",
            "default": "{data_path}/appData/rocketmq"
        },
        {
            "name": "安装用户",
            "key": "run_user",
            "default": "commonuser"
        }
    ]),
    "app_controllers": json.dumps({
        "start": "./scripts/rocketmq start",
        "stop": "./scripts/rocketmq stop",
        "restart": "./scripts/rocketmq restart",
        "reload": "",
        "install": "./scripts/install.py",
        "init": "./scripts/init.py"
    }),
    "app_logo": None,
    "extend_fields": {
        "deploy": "",
        "affinity": "",
        "resources": "",
        "auto_launch": "True",
        "post_action": ""
    },
    "is_base_env": False,
    "app_monitor": {
        "type": "",
        "metric_port": "{service_port}",
        "process_name": ""
    },
    "app_package_id": rocketmq_package_obj.id
}
ApplicationHub.objects.create(**rocketmq_app)

tengine_package = {
    "operation_uuid": "1636770501006",
    "operation_user": "admin",
    "package_name": "tengine-1.20.1-20211019113204-ae8557f.tar.gz",
    "package_md5": "b2eb6e60dd697f29bb45fd1d7ea376d",
    "package_path": "verified",
    "package_status": 0,
    "error_msg": None,
    "is_deleted": 0
}
tengine_package_obj = UploadPackageHistory(**tengine_package)
tengine_package_obj.save()
tengine_app = {
    "is_release": True,
    "app_type": 0,
    "app_name": "tengine",
    "app_version": "1.20.1",
    "app_description": "",
    "app_port": json.dumps([
        {
            "name": "服务端口",
            "protocol": "TCP",
            "key": "service_port",
            "default": "18080"
        }
    ]),
    "app_dependence": None,
    "app_install_args": json.dumps([
        {
            "name": "安装目录",
            "key": "base_dir",
            "default": "{data_path}/app/tengine"
        },
        {
            "name": "日志目录",
            "key": "log_dir",
            "default": "{data_path}/logs/tengine"
        },
        {
            "name": "数据目录",
            "key": "data_dir",
            "default": "{data_path}/appData/tengine"
        },
        {
            "name": "安装用户",
            "key": "run_user",
            "default": "commonuser"
        }
    ]),
    "app_controllers": json.dumps({
        "start": "./scripts/tengine start",
        "stop": "./scripts/tengine stop",
        "restart": "./scripts/tengine restart",
        "reload": "",
        "install": "./scripts/install.py",
        "init": "./scripts/init.py"
    }),
    "app_logo": None,
    "extend_fields": {
        "deploy": "",
        "affinity": "",
        "resources": "",
        "auto_launch": "True",
        "post_action": ""
    },
    "is_base_env": False,
    "app_monitor": {
        "type": "",
        "metric_port": "{service_port}",
        "process_name": ""
    },
    "app_package_id": tengine_package_obj.id
}
ApplicationHub.objects.create(**tengine_app)

arangodb_package = {
    "operation_uuid": "1636770501006",
    "operation_user": "admin",
    "package_name": "arangodb-5.6.5-20211019113204-ae8557f.tar.gz",
    "package_md5": "b2eb6e60dd697f29bb45fd1d7ea376d",
    "package_path": "verified",
    "package_status": 0,
    "error_msg": None,
    "is_deleted": 0
}
arangodb_package_obj = UploadPackageHistory(**arangodb_package)
arangodb_package_obj.save()
arangodb_app = {
    "is_release": True,
    "app_type": 0,
    "app_name": "arangodb",
    "app_version": "3.6.5",
    "app_description": "",
    "app_port": json.dumps([
        {
            "name": "服务端口",
            "protocol": "TCP",
            "key": "service_port",
            "default": "12345"
        }
    ]),
    "app_dependence": None,
    "app_install_args": json.dumps([
        {
            "name": "安装目录",
            "key": "base_dir",
            "default": "{data_path}/app/arangodb"
        },
        {
            "name": "日志目录",
            "key": "log_dir",
            "default": "{data_path}/logs/arangodb"
        },
        {
            "name": "数据目录",
            "key": "data_dir",
            "default": "{data_path}/appData/arangodb"
        },
        {
            "name": "安装用户",
            "key": "run_user",
            "default": "commonuser"
        }
    ]),
    "app_controllers": json.dumps({
        "start": "./scripts/arangodb start",
        "stop": "./scripts/arangodb stop",
        "restart": "./scripts/arangodb restart",
        "reload": "",
        "install": "./scripts/install.py",
        "init": "./scripts/init.py"
    }),
    "app_logo": None,
    "extend_fields": {
        "deploy": "",
        "affinity": "",
        "resources": "",
        "auto_launch": "True",
        "post_action": ""
    },
    "is_base_env": False,
    "app_monitor": {
        "type": "",
        "metric_port": "{service_port}",
        "process_name": ""
    },
    "app_package_id": arangodb_package_obj.id
}
ApplicationHub.objects.create(**arangodb_app)

# 全部安装包的创建操作
package_lst = UploadPackageHistory.objects.values(
    "package_path", "package_name")
for item in package_lst:
    _path = os.path.join(
        PROJECT_DIR, "package_hub",
        item["package_path"], item["package_name"]
    )
    if not os.path.exists(os.path.dirname(_path)):
        os.system(f"mkdir {os.path.dirname(_path)}")
    a = os.system(f"touch {_path}")

hosts = [
    {
        "is_deleted": 0,
        "instance_name": "127.0.0.1",
        "ip": "127.0.0.1",
        "port": 36000,
        "username": "root",
        "password": "pMMkpa5jqlJG4A-ROeMlsEHj8YvMTRpMYnNFD2YS7MA",
        "data_folder": "/test",
        "service_num": 0,
        "alert_num": 0,
        "operate_system": "CentOS",
        "memory": 32,
        "cpu": 8,
        "disk": {"/": 50, "/data": 47},
        "host_agent": "0",
        "monitor_agent": "0",
        "is_maintenance": 0,
        "env_id": 1,
        "host_agent_error": None,
        "host_name": "localhost",
        "monitor_agent_error": None,
        "agent_dir": "/test"
    },
    {
        "is_deleted": 0,
        "instance_name": "127.0.0.2",
        "ip": "127.0.0.2",
        "port": 36000,
        "username": "root",
        "password": "pMMkpa5jqlJG4A-ROeMlsEHj8YvMTRpMYnNFD2YS7MA",
        "data_folder": "/test",
        "service_num": 0,
        "alert_num": 0,
        "operate_system": "CentOS",
        "memory": 32,
        "cpu": 8,
        "disk": {"/": 50, "/data": 47},
        "host_agent": "0",
        "monitor_agent": "0",
        "is_maintenance": 0,
        "env_id": 1,
        "host_agent_error": None,
        "host_name": "localhost",
        "monitor_agent_error": None,
        "agent_dir": "/test"
    },
    {
        "is_deleted": 0,
        "instance_name": "127.0.0.3",
        "ip": "127.0.0.3",
        "port": 36000,
        "username": "root",
        "password": "pMMkpa5jqlJG4A-ROeMlsEHj8YvMTRpMYnNFD2YS7MA",
        "data_folder": "/test",
        "service_num": 0,
        "alert_num": 0,
        "operate_system": "CentOS",
        "memory": 32,
        "cpu": 8,
        "disk": {"/": 50, "/data": 47},
        "host_agent": "0",
        "monitor_agent": "0",
        "is_maintenance": 0,
        "env_id": 1,
        "host_agent_error": None,
        "host_name": "localhost",
        "monitor_agent_error": None,
        "agent_dir": "/test"
    }
]
host_lst = list()
for item in hosts:
    host_lst.append(Host(**item))
Host.objects.bulk_create(host_lst)
