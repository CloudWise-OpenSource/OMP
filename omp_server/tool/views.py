# Create your views here.
from django.shortcuts import get_object_or_404
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from db_models.models import (ToolExecuteMainHistory, ToolInfo, Host, Service)
from tool.tool_filters import ToolFilter, ToolInfoKindFilter
from tool.serializers import ToolListSerializer, ToolInfoDetailSerializer, \
    ToolTargetObjectServiceSerializer, ToolFormAnswerSerializer, \
    ToolExecuteHistoryListSerializer
from utils.common.paginations import PageNumberPager
from tool.serializers import ToolDetailSerializer, ToolFormDetailSerializer, \
    ToolTargetObjectHostSerializer


class ToolRetrieveAPIMixin:

    def load_tool_obj(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        tool = get_object_or_404(
            ToolInfo.objects.all(),
            **{self.lookup_field: self.kwargs[lookup_url_kwarg]}
        )
        self.kwargs.update(tool=tool)
        return tool


class GetToolDetailView(GenericViewSet, RetrieveModelMixin):
    """
    任务详情页
    """
    queryset = ToolExecuteMainHistory.objects.all()
    get_description = "任务详情页"
    serializer_class = ToolDetailSerializer


class ToolFormDetailAPIView(GenericViewSet, RetrieveModelMixin):
    queryset = ToolInfo.objects.all()
    get_description = "小工具执行表单页"
    serializer_class = ToolFormDetailSerializer


class ToolListView(GenericViewSet, ListModelMixin):
    """查询所有实用工具列表"""
    queryset = ToolInfo.objects.all().order_by("-created")
    serializer_class = ToolListSerializer
    pagination_class = PageNumberPager
    # 过滤排序字段
    filter_backends = (DjangoFilterBackend,)
    filter_class = ToolFilter
    # 操作信息描述
    get_description = "查询所有实用工具列表"


class ToolDetailView(GenericViewSet, RetrieveModelMixin):
    """获取实用工具详情"""
    queryset = ToolInfo.objects.all().order_by("-created")
    serializer_class = ToolInfoDetailSerializer
    # 操作描述信息
    get_description = "获取实用工具详情"


class ToolTargetObjectAPIView(ListAPIView, ToolRetrieveAPIMixin):
    get_description = "小工具执行对象展示页"
    pagination_class = PageNumberPager

    def get(self, request, *args, **kwargs):
        self.load_tool_obj()
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


class ToolFormAnswerAPIView(CreateAPIView, ToolRetrieveAPIMixin):
    get_description = "小工具执行表单页"
    serializer_class = ToolFormAnswerSerializer

    def post(self, request, *args, **kwargs):
        self.load_tool_obj()
        return self.create(request, *args, **kwargs)


class ToolExecuteHistoryListApiView(ListAPIView):
    get_description = "小工具执行列表页"
    pagination_class = PageNumberPager
    serializer_class = ToolExecuteHistoryListSerializer
    queryset = ToolExecuteMainHistory.objects.all().select_related("tool")
    filter_backends = (SearchFilter, OrderingFilter, ToolInfoKindFilter)
    search_fields = ("task_name", )
    ordering_fields = ("start_time",)
    ordering = ('-start_time',)
