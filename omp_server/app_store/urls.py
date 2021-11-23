# -*- coding: utf-8 -*-
# Project: urls
# Author: jon.liu@yunzhihui.com
# Create time: 2021-10-08 15:54
# IDE: PyCharm
# Version: 1.0
# Introduction:


from rest_framework.routers import DefaultRouter
from app_store.views import (
    LabelListView, ComponentListView, ServiceListView,
    UploadPackageView, RemovePackageView,
    ComponentDetailView, ServiceDetailView,
    ServicePackPageVerificationView, PublishViewSet,
    ExecuteLocalPackageScanView, LocalPackageScanResultView,
    ApplicationTemplateView
)
from app_store.views_for_install import (
    ComponentEntranceView,
    ProductEntranceView,
    ExecuteInstallView,
    InstallHistoryView,
    ServiceInstallHistoryDetailView
)

from app_store.new_install_view import (
    BatchInstallEntranceView,
    CreateInstallInfoView,
    CheckInstallInfoView,
    CreateServiceDistributionView,
    CheckServiceDistributionView,
    GetInstallHostRangeView,
    GetInstallArgsByIpView,
    CreateInstallPlanView,
    ListServiceByIpView,
    ShowInstallProcessView,
    ShowSingleServiceInstallLogView
)

router = DefaultRouter()
router.register("labels", LabelListView, basename="labels")
router.register("components", ComponentListView, basename="components")
router.register("services", ServiceListView, basename="appServices")
router.register("upload", UploadPackageView, basename="upload")
router.register("remove", RemovePackageView, basename="remove")
router.register("componentDetail", ComponentDetailView,
                basename="componentDetail")
router.register("serviceDetail", ServiceDetailView,
                basename="appServiceDetail")
router.register("pack_verification_results",
                ServicePackPageVerificationView, basename="pack_verification_results")
router.register("publish", PublishViewSet, basename="publish")
router.register("executeLocalPackageScan", ExecuteLocalPackageScanView,
                basename="executeLocalPackageScan")
router.register("localPackageScanResult", LocalPackageScanResultView,
                basename="localPackageScanResult")
router.register(
    "executeLocalPackageScan", ExecuteLocalPackageScanView,
    basename='executeLocalPackageScan')
router.register(
    "localPackageScanResult", LocalPackageScanResultView,
    basename='localPackageScanResult')
router.register(
    "applicationTemplate", ApplicationTemplateView,
    basename='applicationTemplate')

# 安装部分使用路由
router.register(
    "componentEntrance", ComponentEntranceView,
    basename='componentEntrance')
router.register(
    "productEntrance", ProductEntranceView,
    basename='productEntrance')
router.register(
    "executeInstall", ExecuteInstallView,
    basename='executeInstall')
router.register(
    "installHistory", InstallHistoryView,
    basename='installHistory')
router.register(
    "serviceInstallHistoryDetail", ServiceInstallHistoryDetailView,
    basename='serviceInstallHistoryDetail')

# 新版安装逻辑
router.register(
    "batchInstallEntrance",
    BatchInstallEntranceView,
    basename="batchInstallEntrance"
)
router.register(
    "createInstallInfo",
    CreateInstallInfoView,
    basename="createInstallInfo"
)
router.register(
    "checkInstallInfo",
    CheckInstallInfoView,
    basename="checkInstallInfo"
)
router.register(
    "createServiceDistribution",
    CreateServiceDistributionView,
    basename="createServiceDistribution"
)
router.register(
    "checkServiceDistribution",
    CheckServiceDistributionView,
    basename="checkServiceDistribution"
)
router.register(
    "getInstallHostRange",
    GetInstallHostRangeView,
    basename="getInstallHostRange"
)
router.register(
    "getInstallArgsByIp",
    GetInstallArgsByIpView,
    basename="getInstallArgsByIp"
)
router.register(
    "createInstallPlan",
    CreateInstallPlanView,
    basename="createInstallPlan"
)
router.register(
    "listServiceByIp",
    ListServiceByIpView,
    basename="listServiceByIp"
)
router.register(
    "showInstallProcess",
    ShowInstallProcessView,
    basename="showInstallProcess"
)
router.register(
    "showSingleServiceInstallLog",
    ShowSingleServiceInstallLogView,
    basename="showSingleServiceInstallLog"
)
