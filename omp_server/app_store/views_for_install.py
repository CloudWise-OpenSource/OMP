# -*- coding: utf-8 -*-
# Project: views_for_install
# Author: jon.liu@yunzhihui.com
# Create time: 2021-10-21 17:59
# IDE: PyCharm
# Version: 1.0
# Introduction:

from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    ListModelMixin
)
from django_filters.rest_framework.backends import DjangoFilterBackend

from db_models.models import ApplicationHub

from app_store.app_store_serializers import (
    ComponentEntranceSerializer
)

from app_store.app_store_filters import (
    ComponentEntranceFilter
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
