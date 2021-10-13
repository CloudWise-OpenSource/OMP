"""
应用商店相关视图
"""
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response

from django_filters.rest_framework.backends import DjangoFilterBackend

from db_models.models import (
    Labels, ApplicationHub
)
from utils.pagination import PageNumberPager
from app_store.app_store_filters import (
    LabelFilter, ComponentFilter
)
from app_store.app_store_serializers import ComponentListSerializer


class LabelListView(GenericViewSet, ListModelMixin):
    """
        list:
        查询所有标签列表
    """
    queryset = Labels.objects.all().values_list(
        "label_name", flat=True)
    # 过滤，排序字段
    filter_backends = (DjangoFilterBackend,)
    filter_class = LabelFilter
    # 操作信息描述
    get_description = "查询所有标签列表"

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return Response(list(queryset))


class ComponentListView(GenericViewSet, ListModelMixin):
    """
        list:
        查询所有组件列表
    """
    queryset = ApplicationHub.objects.filter(
        app_type=ApplicationHub.APP_TYPE_COMPONENT,
        is_release=True,
    ).order_by("-created")
    serializer_class = ComponentListSerializer
    pagination_class = PageNumberPager
    # 过滤，排序字段
    filter_backends = (DjangoFilterBackend,)
    filter_class = ComponentFilter
    ordering_fields = ("ip", "host_agent", "monitor_agent",
                       "service_num", "alert_num")
    # 操作信息描述
    get_description = "查询所有组件列表"

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # 根据名称进行去重，同名取最新
        result_ls = []
        name_set = set()
        for component_info in queryset:
            app_name = component_info.app_name
            if app_name not in name_set:
                name_set.add(app_name)
                result_ls.append(component_info)

        serializer = self.get_serializer(
            self.paginate_queryset(result_ls), many=True)

        return self.get_paginated_response(serializer.data)


class ServiceListView(GenericViewSet, ListModelMixin):
    """
        list:
        查询所有服务列表
    """
    # 操作信息描述
    get_description = "查询所有服务列表"
    pass
