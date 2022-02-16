# Create your views here.
from django.shortcuts import get_object_or_404
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import RetrieveModelMixin
from db_models.models import (ToolExecuteMainHistory, ToolInfo, Host, Service)
from tool.tool_filters import ToolFilter
from tool.serializers import ToolListSerializer, ToolInfoDetailSerializer, \
    ToolTargetObjectServiceSerializer
from app_store.views import AppStoreListView
from utils.common.paginations import PageNumberPager
from tool.serializers import ToolDetailSerializer, ToolFormDetailSerializer,\
    ToolTargetObjectHostSerializer


class GetToolDetailView(GenericViewSet, RetrieveModelMixin):
    """
    获取可备份实例列表
    """

    queryset = ToolExecuteMainHistory.objects.all()
    get_description = "任务详情页"
    serializer_class = ToolDetailSerializer


class ToolFormDetailAPIView(GenericViewSet, RetrieveModelMixin):
    queryset = ToolInfo.objects.all()
    get_description = "小工具执行表单页"
    serializer_class = ToolFormDetailSerializer


class ToolListView(AppStoreListView):
    """查询所有实用工具列表"""
    queryset = ToolInfo.objects.all().order_by("-created")
    serializer_class = ToolListSerializer
    pagination_class = PageNumberPager
    # 过滤排序字段
    filter_backends = (DjangoFilterBackend,)
    filter_class = ToolFilter
    # 操作信息描述
    get_description = "查询所有实用工具列表"

    def list(self, request, *args, **kwargs):
        return super(ToolListView, self).list(
            request, name_field="name", *args, **kwargs)


class ToolDetailView(GenericViewSet, RetrieveModelMixin):
    """获取实用工具详情"""
    queryset = ToolInfo.objects.all().order_by("-created")
    serializer_class = ToolInfoDetailSerializer
    # 操作描述信息
    get_description = "获取实用工具详情"


class ToolTargetObjectAPIView(ListAPIView):

    get_description = "小工具执行对象展示页"
    pagination_class = PageNumberPager

    def get(self, request, *args, **kwargs):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        tool = get_object_or_404(
            ToolInfo.objects.all(),
            **{self.lookup_field: self.kwargs[lookup_url_kwarg]}
        )
        self.kwargs.update(tool=tool)
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        if self.kwargs["tool"].target_name == "host":
            return Host.objects.all()
        return Service.objects.filter(
            service__app_name=self.kwargs["tool"].target_name
        )

    def get_serializer_class(self):
        if self.kwargs["tool"].target_name == "host":
            return ToolTargetObjectHostSerializer
        return ToolTargetObjectServiceSerializer
