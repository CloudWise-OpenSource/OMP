import logging

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer
from db_models.models import Env, SelfHealingSetting, SelfHealingHistory

logger = logging.getLogger("server")


class SelfHealingSettingSerializer(ModelSerializer):

    class Meta:
        model = SelfHealingSetting
        fields = ("used", "alert_count", "max_healing_count")

class ListSelfHealingHistorySerializer(ModelSerializer):
    class Meta:
        model = SelfHealingHistory
        fields = "__all__"


class UpdateSelfHealingHistorySerializer(Serializer):
    """自愈历史记录批量更新"""
    ids = serializers.ListField(help_text="自愈历史记录ID列表", required=True, error_messages={"required": "必须包含ID列表字段"})
    is_read = serializers.IntegerField(help_text="是否已读", required=True, error_messages={"required": "必须包含是否已读字段"})

    def create(self, validated_data):
        SelfHealingHistory.objects.filter(id__in=validated_data.get("ids")).update(
            is_read=validated_data.get("is_read"))
        return validated_data
