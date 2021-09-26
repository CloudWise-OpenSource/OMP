"""
主机相关视图
"""
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    ListModelMixin, CreateModelMixin, UpdateModelMixin
)
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from django_filters.rest_framework.backends import DjangoFilterBackend

from db_models.models import Host
from utils.pagination import PageNumberPager
from utils.plugin.crypto import AESCryptor
from hosts.hosts_filters import HostFilter
from hosts.hosts_serializers import (
    HostSerializer, HostMaintenanceSerializer,
    HostFieldCheckSerializer, HostAgentRestartSerializer
)
from promemonitor.prometheus import Prometheus


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
    ordering_fields = ("ip", "host_agent", "monitor_agent",
                       "service_num", "alert_num")
    # 动态排序字段
    dynamic_fields = ("cpu_usage", "mem_usage",
                      "root_disk_usage", "data_disk_usage")
    # 操作描述信息
    get_description = "查询主机"
    post_description = "创建主机"

    def list(self, request, *args, **kwargs):
        # 获取序列化数据列表
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(
            self.paginate_queryset(queryset), many=True)
        serializer_data = serializer.data
        # 主机密码解密
        for host_info in serializer_data:
            aes_crypto = AESCryptor()
            host_info["password"] = aes_crypto.decode(
                host_info.get("password"))

        # 实时获取主机动态
        prometheus_obj = Prometheus()
        serializer_data = prometheus_obj.get_host_info(serializer_data)
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


class HostFieldCheckView(GenericViewSet, CreateModelMixin):
    """
        create:
        验证主机 instance_name/ip 字段重复性
    """
    queryset = Host.objects.filter(is_deleted=False)
    serializer_class = HostFieldCheckSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        return Response(serializer.is_valid())


class IpListView(GenericViewSet, ListModelMixin):
    """
        list:
        查询所有 IP 列表
    """
    queryset = Host.objects.filter(
        is_deleted=False).values_list("ip", flat=True)
    # 操作信息描述
    get_description = "查询主机"

    def list(self, request, *args, **kwargs):
        return Response(list(self.get_queryset()))


class HostMaintenanceView(GenericViewSet, CreateModelMixin):
    """
        create:
        主机进入 / 退出维护模式
    """
    queryset = Host.objects.filter(is_deleted=False)
    # 操作信息描述
    post_description = "修改主机维护模式"
    serializer_class = HostMaintenanceSerializer


class HostAgentRestartView(GenericViewSet, CreateModelMixin):
    """
        create:
        主机重启Agent接口
    """
    queryset = Host.objects.filter(is_deleted=False)
    # 操作信息描述
    post_description = "重启主机Agent"
    serializer_class = HostAgentRestartSerializer
