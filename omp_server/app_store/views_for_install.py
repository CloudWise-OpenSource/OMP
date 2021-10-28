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
    MainInstallHistory
)

from app_store.app_store_serializers import (
    ComponentEntranceSerializer,
    ProductEntranceSerializer,
    ExecuteInstallSerializer,
    InstallHistorySerializer
)

from app_store.app_store_filters import (
    ComponentEntranceFilter,
    ProductEntranceFilter
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
    get_description = "获取安装历史数据入口"
