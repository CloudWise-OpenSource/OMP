# -*- coding: utf-8 -*-
# Project: __init__.py
# Author: jon.liu@yunzhihui.com
# Create time: 2021-11-16 16:44
# IDE: PyCharm
# Version: 1.0
# Introduction:

from app_store.deploy_mode_utils.mysql import MysqlUtils


SERVICE_MAP = {
    "mysql": MysqlUtils
}
