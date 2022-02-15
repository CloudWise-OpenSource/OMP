# -*- coding:utf-8 -*-
# Project: urls
# Create time: 2022/2/10 6:23 下午

from rest_framework.routers import DefaultRouter
from tool.views import (
    ToolListView,
    ToolDetailView,
    GetToolDetailView,
    ToolFormDetailAPIView,
)

router = DefaultRouter()
router.register("toolList", ToolListView, basename="toolList")
router.register("toolList", ToolDetailView, basename="toolList")
router.register(r'result', GetToolDetailView, basename="result")
router.register(r'form', ToolFormDetailAPIView, basename="form")
urlpatterns = router.urls
