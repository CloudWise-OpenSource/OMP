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
    ApplicationDetailView, ProductDetailView,
    ServicePackPageVerificationView, PublishViewSet
)

router = DefaultRouter()
router.register("labels", LabelListView, basename="labels")
router.register("components", ComponentListView, basename="components")
router.register("services", ServiceListView, basename="services")
router.register("upload", UploadPackageView, basename="upload")
router.register("remove", RemovePackageView, basename="remove")
router.register("componentDetail", ComponentDetailView,
                basename='componentDetail')
router.register("serviceDetail", ServiceDetailView, basename='serviceDetail')
router.register("ApplicationDetail", ApplicationDetailView,
                basename='ApplicationDetail')
router.register("ProductDetail", ProductDetailView, basename='ProductDetail')
router.register("pack_verification_results", ServicePackPageVerificationView, basename="pack_verification_results")
router.register("publish", PublishViewSet, basename="publish")

