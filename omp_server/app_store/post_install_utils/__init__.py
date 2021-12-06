# -*- coding: utf-8 -*-
# Project: __init__.py
# Author: jon.liu@yunzhihui.com
# Create time: 2021-12-06 11:47
# IDE: PyCharm
# Version: 1.0
# Introduction:

from app_store.post_install_utils.nacos import Nacos
from app_store.post_install_utils.tengine import Tengine

POST_INSTALL_SERVICE = {
    "nacos": Nacos,
    "tengine": Tengine
}
