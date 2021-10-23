from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework.filters import OrderingFilter

from django_filters.rest_framework.backends import DjangoFilterBackend

from db_models.models import Service
from services.services_filters import ServiceFilter
from services.services_serializers import (
    ServiceSerializer
)
from utils.common.paginations import PageNumberPager
from promemonitor.grafana_url import explain_url


class ServiceListView(GenericViewSet, ListModelMixin):
    """
        list:
        查询服务列表
    """
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    pagination_class = PageNumberPager
    # 过滤，排序字段
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_class = ServiceFilter
    ordering_fields = ("ip", "service_instance_name")
    # 操作描述信息
    get_description = "查询服务"

    def list(self, request, *args, **kwargs):
        # 获取序列化数据列表
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(
            self.paginate_queryset(queryset), many=True)
        serializer_data = serializer.data

        # 获取监控及日志的url
        serializer_data = explain_url(serializer_data)
        return self.get_paginated_response(serializer_data)
