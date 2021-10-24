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
    ExecuteLocalPackageScanView, LocalPackageScanResultView
)
from app_store.views_for_install import (
    ComponentEntranceView,
    ProductEntranceView
)

router = DefaultRouter()
router.register("labels", LabelListView, basename="labels")
router.register("components", ComponentListView, basename="components")
router.register("services", ServiceListView, basename="appServices")
router.register("upload", UploadPackageView, basename="upload")
router.register("remove", RemovePackageView, basename="remove")
router.register("componentDetail", ComponentDetailView,
                basename='componentDetail')
router.register("serviceDetail", ServiceDetailView, basename='serviceDetail')
router.register("pack_verification_results",
                ServicePackPageVerificationView, basename="pack_verification_results")
router.register("publish", PublishViewSet, basename="publish")
router.register(
    "executeLocalPackageScan", ExecuteLocalPackageScanView,
    basename='executeLocalPackageScan')
router.register(
    "localPackageScanResult", LocalPackageScanResultView,
    basename='localPackageScanResult')

# 安装部分使用路由
router.register(
    "componentEntrance", ComponentEntranceView,
    basename='componentEntrance')
router.register(
    "productEntrance", ProductEntranceView,
    basename='productEntrance')
