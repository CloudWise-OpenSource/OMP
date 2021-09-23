from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from db_models.models import MonitorUrl


class MonitorUrlSerializer(ModelSerializer):
    """ 监控配置项序列化 """
    name = serializers.CharField(
        max_length=32, required=True,
        error_messages={"invalid": "监控名字格式不正确"},
        help_text="监控名字")
    id = serializers.IntegerField(
        max_value=100, required=False,
        error_messages={"invalid": "id格式不正确"},
        help_text="id")
    #name = serializers.ListField(child=serializers.CharField(max_length=32, required=False,
    #    error_messages={"invalid": "监控名字格式不正确"},
    #    help_text="监控名字"))
    monitor_url = serializers.CharField(
        required=True,
        error_messages={"invalid": "监控地址格式不正确"},
        help_text="监控地址")
    #monitor_url = serializers.ListField(child=serializers.CharField(max_length=128, required=True,
    #    error_messages={"invalid": "监控地址格式不正确"},
    #    help_text="监控地址"))
    class Meta:
        model = MonitorUrl
        fields = "__all__"
