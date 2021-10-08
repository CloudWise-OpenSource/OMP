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

config_file_path = os.path.join(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ), "config/omp.yaml"
)


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
