"""
主机相关视图
"""
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    ListModelMixin, CreateModelMixin, RetrieveModelMixin,
    DestroyModelMixin, UpdateModelMixin
)
from rest_framework.filters import OrderingFilter

from django_filters.rest_framework.backends import DjangoFilterBackend

from db_models.models import Host
from utils.pagination import PageNumberPager
from hosts.hosts_filters import HostFilter
from hosts.hosts_serializers import HostSerializer


class HostListView(GenericViewSet, ListModelMixin, CreateModelMixin):
    """
        list:
        查询主机列表

        create:
        创建一个新主机
    """
    queryset = Host.objects.filter(is_deleted=False)
    serializer_class = HostSerializer
    pagination_class = PageNumberPager
    # 过滤，排序字段
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_class = HostFilter
    ordering_fields = ("ip", "host_agent", "monitor_agent", "service_num", "alert_num")
    # 操作描述信息
    get_description = "查询主机"
    post_description = "创建主机"

    def list(self, request, *args, **kwargs):
        # 重写 list 方法，实时获取主机动态数据，并注入
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(
            self.paginate_queryset(queryset), many=True)
        # TODO 实时获取主机动态
        for i in serializer.data:
            i["nei"] = 1111111
        return self.get_paginated_response(serializer.data)


class HostDetailView(GenericViewSet, UpdateModelMixin):
    """
        update:
        更新一个主机

        partial_update:
        更新一个现有主机的一个或多个字段
    """
    queryset = Host.objects.filter(is_deleted=False)
    serializer_class = HostSerializer
    # 操作描述信息
    put_description = patch_description = "更新主机"
