# -*- coding: utf-8 -*-
# Project: __init__.py
# Author: jon.liu@yunzhihui.com
# Create time: 2021-11-16 16:44
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
服务部署模式
"""

from app_store.deploy_mode_utils.mysql import MysqlUtils
# from app_store.deploy_mode_utils.normal import NormalUtils
from app_store.deploy_mode_utils.odd_num import OddNumUtils
# from app_store.deploy_mode_utils.even_num import EvenNumUtils
from app_store.deploy_mode_utils.tengine import TengineUtils
from app_store.deploy_mode_utils.rocketmq import RocketmqUtils


SERVICE_MAP = {
    "mysql": MysqlUtils,
    "zookeeper": OddNumUtils,
    "kafka": OddNumUtils,
    "nacos": OddNumUtils,
    "tengine": TengineUtils,
    "rocketmq": RocketmqUtils
}
