# -*- coding:utf-8 -*-
# Project: urls
# Create time: 2022/2/10 6:23 下午
from django.urls import path
from rest_framework.routers import DefaultRouter
from tool.views import ToolListView, ToolDetailView, GetToolDetailView, \
    ToolFormDetailAPIView, ToolTargetObjectAPIView, ToolFormAnswerAPIView, \
    ToolExecuteHistoryListApiView

router = DefaultRouter()
router.register("toolList", ToolListView, basename="toolList")
router.register("toolList", ToolDetailView, basename="toolList")
router.register(r'result', GetToolDetailView, basename="result")
router.register(r'form', ToolFormDetailAPIView, basename="form")

urlpatterns = [
    path(
        'form/<int:pk>/target-object',
        ToolTargetObjectAPIView.as_view(),
        name="target-object"
    ),
    path(
        'form/<int:pk>/answer',
        ToolFormAnswerAPIView.as_view(),
        name="answer"
    ),
    path(
        'execute-history',
        ToolExecuteHistoryListApiView.as_view(),
        name="execute-history"
    ),
]

urlpatterns += router.urls


