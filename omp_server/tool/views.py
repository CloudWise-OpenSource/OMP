# Create your views here.

from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import RetrieveModelMixin
from db_models.models import (ToolExecuteMainHistory, ToolInfo)
from tool.serializers import ToolDetailSerializer, ToolFormDetailSerializer


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
