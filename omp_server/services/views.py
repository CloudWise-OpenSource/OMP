from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    ListModelMixin, RetrieveModelMixin,
    CreateModelMixin
)
from rest_framework.filters import OrderingFilter

from django_filters.rest_framework.backends import DjangoFilterBackend

from db_models.models import Service
from services.services_filters import ServiceFilter
from services.services_serializers import (
    ServiceSerializer, ServiceDetailSerializer,
    ServiceActionSerializer
)
from utils.common.paginations import PageNumberPager
from promemonitor.grafana_url import explain_url
from services.tasks import exec_action
from utils.common.exceptions import OperateError
from rest_framework.response import Response


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
    get_description = "查询服务列表"

    def list(self, request, *args, **kwargs):
        # 获取序列化数据列表
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(
            self.paginate_queryset(queryset), many=True)
        serializer_data = serializer.data

        # 获取监控及日志的url
        serializer_data = explain_url(
            serializer_data, is_service=True)
        return self.get_paginated_response(serializer_data)


class ServiceDetailView(GenericViewSet, RetrieveModelMixin):
    """
        read:
        查询服务详情
    """
    queryset = Service.objects.all()
    serializer_class = ServiceDetailSerializer
    # 操作描述信息
    get_description = "查询服务详情"


class ServiceActionView(GenericViewSet, CreateModelMixin):
    queryset = Service.objects.all()
    serializer_class = ServiceActionSerializer

    def create(self, request, *args, **kwargs):
        many_data = self.request.data.get('data')
        for data in many_data:
            action = data.get("action")
            instance = data.get("id")
            operation_user = data.get("operation_user")
            if action and instance and operation_user:
                exec_action.delay(action, instance, operation_user)
            else:
                raise OperateError("请输入action或id")
        return Response("执行成功")
