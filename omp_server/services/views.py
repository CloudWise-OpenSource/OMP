from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    ListModelMixin, RetrieveModelMixin,
    CreateModelMixin
)
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter

from django_filters.rest_framework.backends import DjangoFilterBackend

from db_models.models import Service
from services.tasks import exec_action
from services.services_filters import ServiceFilter
from services.services_serializers import (
    ServiceSerializer, ServiceDetailSerializer,
    ServiceActionSerializer
)
from promemonitor.prometheus import Prometheus
from promemonitor.grafana_url import explain_url
from utils.common.exceptions import OperateError
from utils.common.paginations import PageNumberPager


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

        # 实时获取服务动态git
        prometheus_obj = Prometheus()
        is_success, prometheus_dict = prometheus_obj.get_all_service_status()
        # 若获取成功，则动态覆盖服务状态
        if is_success:
            status_dict = {
                True: "正常",
                False: "停止",
            }
            for service_obj in serializer_data:
                # 如果服务状态为 '正常' 和 '停止' 的服务，通过 Prometheus 动态更新
                if service_obj.get("service_status") in ("正常", "停止"):
                    key_name = f"{service_obj.get('ip')}_{service_obj.get('service_instance_name')}"
                    status = prometheus_dict.get(key_name, None)
                    if status is not None:
                        service_obj["service_status"] = status_dict.get(status)

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
