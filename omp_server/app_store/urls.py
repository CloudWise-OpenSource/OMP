# -*- coding: utf-8 -*-
# Project: urls
# Author: jon.liu@yunzhihui.com
# Create time: 2021-10-08 15:54
# IDE: PyCharm
# Version: 1.0
# Introduction:


from rest_framework.routers import DefaultRouter

from app_store.views import LabelListView
from app_store.views import UploadPackageView

router = DefaultRouter()
router.register("labels", LabelListView, basename="labels")
router.register("upload", UploadPackageView, basename="upload")