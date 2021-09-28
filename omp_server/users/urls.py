# -*- coding: utf-8 -*-
# Project: urls
# Author: jon.liu@yunzhihui.com
# Create time: 2021-09-10 17:21
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
用户相关的路由
"""

from rest_framework.routers import DefaultRouter

from users.views import (
    UsersView, OperateLogView,
)

router = DefaultRouter()
router.register("users", UsersView, basename="users")
router.register("operateLog", OperateLogView, basename="operateLog")
# router.register("updatePassword", UserUpdatePasswordView, basename="updatePassword")
