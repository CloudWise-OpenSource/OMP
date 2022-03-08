# -*- coding: utf-8 -*-
# Project: parse_config
# Author: jon.liu@yunzhihui.com
# Create time: 2021-09-15 09:26
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
解析配置文件
"""

import os

from ruamel import yaml

project_path = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
config_file_path = os.path.join(project_path, "config/omp.yaml")

private_key_path = os.path.join(project_path, "config/private_key.pem")

# openssl genrsa -out private_key.pem 2048
# openssl rsa -in private_key.pem -out public_key.pem -pubout
with open(private_key_path, "r") as key_f:
    PRIVATE_KEY = key_f.read()

with open(config_file_path, "r") as fp:
    CONFIG_DIC = yaml.load(fp, Loader=yaml.SafeLoader)

GLOBAL_RUNUSER = CONFIG_DIC.get("global_runuser")
LOCAL_IP = CONFIG_DIC.get("local_ip")
SSH_CMD_TIMEOUT = CONFIG_DIC.get("ssh_cmd_timeout", 60)
SSH_CHECK_TIMEOUT = CONFIG_DIC.get("ssh_check_timeout", 10)
THREAD_POOL_MAX_WORKERS = CONFIG_DIC.get("thread_pool_max_workers", 20)
SALT_RET_PORT = CONFIG_DIC.get("salt_master", {}).get("ret_port", 19005)
TOKEN_EXPIRATION = CONFIG_DIC.get("token_expiration", 1)
MONITOR_PORT = CONFIG_DIC.get("monitor_port")
GRAFANA_API_KEY = CONFIG_DIC.get("grafana_api_key")
PROMETHEUS_AUTH = CONFIG_DIC.get("prometheus_auth", {})
OMP_REDIS_HOST = os.getenv(
    "OMP_REDIS_HOST",
    CONFIG_DIC.get("redis", {}).get("host")
)
OMP_REDIS_PORT = os.getenv(
    "OMP_REDIS_PORT",
    CONFIG_DIC.get("redis", {}).get("port")
)
OMP_REDIS_PASSWORD = os.getenv(
    "OMP_REDIS_PASSWORD",
    CONFIG_DIC.get("redis", {}).get("password")
)
OMP_MYSQL_HOST = os.getenv(
    "OMP_MYSQL_HOST",
    CONFIG_DIC.get("mysql", {}).get("host")
)
OMP_MYSQL_PORT = os.getenv(
    "OMP_MYSQL_PORT",
    CONFIG_DIC.get("mysql", {}).get("port")
)
OMP_MYSQL_USERNAME = os.getenv(
    "OMP_MYSQL_USERNAME",
    CONFIG_DIC.get("mysql", {}).get("username")
)
OMP_MYSQL_PASSWORD = os.getenv(
    "OMP_MYSQL_PASSWORD",
    CONFIG_DIC.get("mysql", {}).get("password")
)
BASIC_ORDER = CONFIG_DIC.get("basic_order", {})
AFFINITY_FIELD = CONFIG_DIC.get("affinity", {})
HADOOP_ROLE = CONFIG_DIC.get("hadoop_role", {})
HOSTNAME_PREFIX = CONFIG_DIC.get("hostname_prefix", {})
