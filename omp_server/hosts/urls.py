# -*- coding: utf-8 -*-
# Project: urls
# Author: jon.liu@yunzhihui.com
# Create time: 2021-09-12 11:44
# IDE: PyCharm
# Version: 1.0
# Introduction:

from rest_framework.routers import DefaultRouter

from hosts.views import (
    HostListView, HostDetailView, HostUpdateView,
    HostFieldCheckView, IpListView, HostMaintenanceView,
    HostAgentRestartView, HostOperateLogView, HostBatchValidateView,
    HostBatchImportView, HostInitView, HostsAgentStatusView,
    HostReinstallView, MonitorReinstallView,
    HostUninstallView
)

router = DefaultRouter()
router.register("hosts", HostListView, basename="hosts")
router.register("hosts", HostUpdateView, basename="hosts")
router.register("hostsDetail", HostDetailView, basename="hostsDetail")
router.register("fields", HostFieldCheckView, basename="fields")
router.register("ips", IpListView, basename="ips")
router.register("maintain", HostMaintenanceView, basename="maintain")
router.register("restartHostAgent", HostAgentRestartView,
                basename="restartHostAgent")
router.register("operateLog", HostOperateLogView, basename="operateLog")
router.register("batchValidate", HostBatchValidateView,
                basename="batchValidate")
router.register("batchImport", HostBatchImportView,
                basename="batchImport")
router.register("hostInit", HostInitView, basename="hostInit")
router.register("hostsAgentStatus",
                HostsAgentStatusView, basename="hostsAgentStatus")
router.register("hostReinstall",
                HostReinstallView, basename="hostReinstall")
router.register("monitorReinstall",
                MonitorReinstallView, basename="monitorReinstall")
router.register("hostUninstall",
                HostUninstallView, basename="hostUninstall")
