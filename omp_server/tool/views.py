# Create your views here.

from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import RetrieveModelMixin
from db_models.models import (
    ToolExecuteMainHistory,
)
from tool.serializers import ToolDetailSerializer


class GetToolDetailView(GenericViewSet, RetrieveModelMixin):
    """
    获取可备份实例列表
    """

    queryset = ToolExecuteMainHistory.objects.all()
    get_description = "任务详情页"
    serializer_class = ToolDetailSerializer
