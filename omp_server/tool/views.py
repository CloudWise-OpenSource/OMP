from django.shortcuts import render

# Create your views here.
import os
import logging

from django.conf import settings
from django.http import FileResponse
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from db_models.models import ToolInfo
from app_store.views import AppStoreListView
from tool.tool_serializers import (ToolListSerializer, ToolDetailSerializer)
from tool.tool_filters import ToolFilter
from django_filters.rest_framework.backends import DjangoFilterBackend
from utils.common.paginations import PageNumberPager
from utils.common.exceptions import OperateError

logger = logging.getLogger("server")


class ToolListView(AppStoreListView):
    """查询所有实用工具列表"""
    queryset = ToolInfo.objects.all().order_by("-created")
    serializer_class = ToolListSerializer
    pagination_class = PageNumberPager
    # 过滤排序字段
    filter_backends = (DjangoFilterBackend,)
    filter_class = ToolFilter
    # 操作信息描述
    get_description = "查询所有实用工具列表"

    def list(self, request, *args, **kwargs):
        return super(ToolListView, self).list(request, name_field="name", *args, **kwargs)


class ToolDetailView(GenericViewSet, RetrieveModelMixin):
    """获取实用工具详情"""
    queryset = ToolInfo.objects.all().order_by("-created")
    serializer_class = ToolDetailSerializer
    # 操作描述信息
    get_description = "获取实用工具详情"
