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
from hosts.hosts_serializers import HostSerializer


class HostView(GenericViewSet, ListModelMixin, CreateModelMixin):
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
    filter_fields = ("ip",)
    ordering_fields = ("ip", "host_agent", "monitor_agent", "service_num", "alert_num")
    get_description = "查询主机"
    post_description = "创建主机"
