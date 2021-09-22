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
    # 动态排序字段
    dynamic_fields = ("cpu_num", "memory_num", "root_use_num", "data_use_num")
    # 操作描述信息
    get_description = "查询主机"
    post_description = "创建主机"

    def list(self, request, *args, **kwargs):

        # 获取序列化数据列表
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(
            self.paginate_queryset(queryset), many=True)
        serializer_data = serializer.data

        # TODO 实时获取主机动态
        for i, d in enumerate(serializer_data):
            d["cpu_num"] = i + 1
            d["memory_num"] = i + 1
            d["root_use_num"] = i + 1
            d["data_use_num"] = i + 1

        # 获取请求中 ordering 字段
        query_field = request.query_params.get("ordering", "")
        reverse_flag = False
        if query_field.startswith("-"):
            reverse_flag = True
            query_field = query_field[1:]

        # 若排序字段在类视图 dynamic_fields 中，则对根据动态数据进行排序
        if query_field in self.dynamic_fields:
            serializer_data = sorted(
                serializer_data,
                key=lambda x: x.get(query_field),
                reverse=reverse_flag)

        return self.get_paginated_response(serializer_data)


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
