# -*- coding: utf-8 -*-
# Project: views_for_install
# Author: jon.liu@yunzhihui.com
# Create time: 2021-10-21 17:59
# IDE: PyCharm
# Version: 1.0
# Introduction:

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    ListModelMixin, CreateModelMixin
)
from django_filters.rest_framework.backends import DjangoFilterBackend

from db_models.models import (
    ApplicationHub, ProductHub,
    MainInstallHistory, Service
)

from app_store.app_store_serializers import (
    ComponentEntranceSerializer,
    ProductEntranceSerializer,
    ExecuteInstallSerializer,
    InstallHistorySerializer,
    ServiceInstallHistorySerializer
)

from app_store.app_store_filters import (
    ComponentEntranceFilter,
    ProductEntranceFilter,
    InstallHistoryFilter,
    ServiceInstallHistoryFilter
)


class ComponentEntranceView(GenericViewSet, ListModelMixin):
    """
        list:
        组件安装入口
    """
    queryset = ApplicationHub.objects.filter(
        is_release=True,
        app_type=ApplicationHub.APP_TYPE_COMPONENT
    ).order_by("-created")
    serializer_class = ComponentEntranceSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_class = ComponentEntranceFilter
    get_description = "获取组件安装数据入口"

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        # 对返回数据重新进行处理，对process_continue字段进行提取
        for el in serializer.data:
            if len(el.get("app_dependence", [])) != 0:
                for item in el.get("app_dependence", []):
                    if "process_continue" in item and \
                            not item["process_continue"] and \
                            el.get("process_continue"):
                        el["process_continue"] = False
                        el["process_message"] = item.get("process_message")
                        break
        return Response(serializer.data)


class ProductEntranceView(GenericViewSet, ListModelMixin):
    """
        list:
        产品、应用安装入口
    """
    queryset = ProductHub.objects.filter(
        is_release=True,
    ).order_by("-created")
    serializer_class = ProductEntranceSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_class = ProductEntranceFilter
    get_description = "获取产品应用安装数据入口"


class ExecuteInstallView(GenericViewSet, CreateModelMixin):

    serializer_class = ExecuteInstallSerializer
    post_description = "执行安装入口接口"

    def create(self, request, *args, **kwargs):
        """
            post:
            执行安装按钮接口
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class InstallHistoryView(GenericViewSet, ListModelMixin):
    """
        list:
        获取安装记录
    """
    queryset = MainInstallHistory.objects.all().order_by("-created")
    serializer_class = InstallHistorySerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = InstallHistoryFilter
    get_description = "获取安装历史数据入口"


class ServiceInstallHistoryDetailView(GenericViewSet, ListModelMixin):
    """
        list:
        获取安装记录
    """
    queryset = Service.objects.all().order_by("-created")
    serializer_class = ServiceInstallHistorySerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = ServiceInstallHistoryFilter
    get_description = "获取单个服务安装记录"
