import logging
import json

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.mixins import CreateModelMixin, ListModelMixin, DestroyModelMixin, UpdateModelMixin
from services.self_heal_serializers import SelfHealingSettingSerializer, ListSelfHealingHistorySerializer, \
    UpdateSelfHealingHistorySerializer
from services.self_heal_filter import SelfHealingTimeFilter, SelfHealingHistoryFilter
from db_models.models import SelfHealingSetting, SelfHealingHistory
from utils.common.paginations import PageNumberPager
from services.self_healing import get_enable_health
from rest_framework_bulk import BulkUpdateAPIView

logger = logging.getLogger("server")


class SelfHealingSettingView(GenericViewSet, ListModelMixin, CreateModelMixin, BulkUpdateAPIView, DestroyModelMixin,
                             UpdateModelMixin):
    """自愈策略"""
    queryset = SelfHealingSetting.objects.all()
    serializer_class = SelfHealingSettingSerializer
    # 操作信息描述
    get_description = "自愈策略"
    post_description = "自愈策略"

    def list(self, request, *args, **kwargs):
        query_field = request.query_params.get("instance", False)
        if query_field:
            # 查看还有多少服务需要
            repair_ls = self.get_queryset().values_list("repair_instance", flat=True)
            repairs = []
            for _ in repair_ls:
                repairs.extend(_)
            if "all" in repairs:
                data = {"all": False,
                        "service_name": []}
            else:
                data = {"all": False if repairs else True,
                        "service_name": get_enable_health(repairs)
                        }
            return Response(data)
        else:
            return super(SelfHealingSettingView, self
                         ).list(request, *args, **kwargs)


class ListSelfHealingHistoryView(GenericViewSet, ListModelMixin):
    """自愈历史记录"""
    queryset = SelfHealingHistory.objects.all().order_by("-alert_time", "-end_time")
    serializer_class = ListSelfHealingHistorySerializer
    pagination_class = PageNumberPager
    filter_backends = (
        DjangoFilterBackend,
        OrderingFilter,
        SelfHealingTimeFilter,
    )
    filter_class = SelfHealingHistoryFilter
    ordering_fields = ("host_ip", "instance_name", "state", "alert_time", "end_time")


class UpdateSelfHealingHistoryView(CreateModelMixin, GenericViewSet):
    """更新自愈历史记录试图"""
    serializer_class = UpdateSelfHealingHistorySerializer
    queryset = SelfHealingHistory.objects.all().order_by("id")
    post_description = "更新自愈历史记录（已读/未读）"
