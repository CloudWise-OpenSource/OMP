import logging
import json

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from services.self_heal_serializers import SelfHealingSettingSerializer, ListSelfHealingHistorySerializer, \
    UpdateSelfHealingHistorySerializer
from services.self_heal_filter import SelfHealingTimeFilter, SelfHealingHistoryFilter
from db_models.models import SelfHealingSetting, SelfHealingHistory, Env
from utils.common.paginations import PageNumberPager

logger = logging.getLogger("server")


class SelfHealingSettingView(GenericViewSet, ListModelMixin, CreateModelMixin):
    """自愈策略"""
    serializer_class = SelfHealingSettingSerializer
    # 操作信息描述
    get_description = "自愈策略"
    post_description = "自愈策略"

    def list(self, request, *args, **kwargs):
        env_id = request.GET.get("env_id", "1")
        try:
            Env.objects.get(id=int(env_id))
        except Exception as e:
            logger.error(f"id为{env_id}的环境不存在!详情：{e}")
            return Response(data={"code": 1, "message": f"id为{env_id}的环境不存在!"})
        self_healing_instance = SelfHealingSetting.objects.filter(env_id=env_id).last()
        serializer = self.get_serializer(self_healing_instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        request_data = json.loads(request.body)
        env_id = request_data.get("env_id", "1")
        alert_count = request_data.get("alert_count", 1)
        max_healing_count = request_data.get("max_healing_count", 5)
        used = request_data.get("used", False)
        try:
            Env.objects.get(id=int(env_id))
        except Exception as e:
            logger.error(f"id为{env_id}的环境不存在!详情：{e}")
            return Response(data={"code": 1, "message": f"id为{env_id}的环境不存在!"})
        if not isinstance(alert_count, int) or not isinstance(max_healing_count, int):
            logger.error("提交数据错误")
            return Response(data={"code": 1, "message": "提交数据错误"})
        try:
            obj, _ = SelfHealingSetting.objects.get_or_create(env_id=int(env_id))
            obj.alert_count = alert_count
            obj.max_healing_count = max_healing_count
            obj.used = used
            obj.save()
        except Exception as e:
            logger.error(e)
            Response(data={"code": 1, "message": "自愈策略配置失败"})
        return Response({})


class ListSelfHealingHistoryView(GenericViewSet, ListModelMixin):
    """自愈历史记录"""
    queryset = SelfHealingHistory.objects.all().order_by("-alert_time")
    serializer_class = ListSelfHealingHistorySerializer
    pagination_class = PageNumberPager
    filter_backends = (
        DjangoFilterBackend,
        OrderingFilter,
        SelfHealingTimeFilter,
    )
    filter_class = SelfHealingHistoryFilter
    ordering_fields = ("host_ip", "service_name", "state", "alert_time", "end_time")


class UpdateSelfHealingHistoryView(CreateModelMixin, GenericViewSet):
    """更新自愈历史记录试图"""
    serializer_class = UpdateSelfHealingHistorySerializer
    queryset = SelfHealingHistory.objects.all().order_by("id")
    post_description = "更新自愈历史记录（已读/未读）"
