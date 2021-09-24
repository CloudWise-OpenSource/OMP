# -*- coding: utf-8 -*-
# Project: urls
# Author: jon.liu@yunzhihui.com
# Create time: 2021-09-12 11:44
# IDE: PyCharm
# Version: 1.0
# Introduction:

from rest_framework.routers import DefaultRouter

from hosts.views import (
    HostListView, HostDetailView,
    IpListView, HostMaintenanceView
)

router = DefaultRouter()
router.register("hosts", HostListView, basename="hosts")
router.register("hosts", HostDetailView, basename="hosts")
router.register("ips", IpListView, basename="ips")
router.register("maintain", HostMaintenanceView, basename="maintain")
