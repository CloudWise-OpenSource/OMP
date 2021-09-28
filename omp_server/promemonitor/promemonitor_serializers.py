from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from db_models.models import MonitorUrl, Alert


class MonitorUrlSerializer(ModelSerializer):
    """
    监控配置项序列化
    """
    name = serializers.CharField(
        max_length=32, required=True,
        error_messages={"invalid": "监控名字格式不正确"},
        help_text="监控名字")
    id = serializers.IntegerField(
        max_value=100, required=False,
        error_messages={"invalid": "id格式不正确"},
        help_text="id")
    # name = serializers.ListField(child=serializers.CharField(max_length=32, required=False,
    #    error_messages={"invalid": "监控名字格式不正确"},
    #    help_text="监控名字"))
    monitor_url = serializers.CharField(
        required=True,
        error_messages={"invalid": "监控地址格式不正确"},
        help_text="监控地址")

    # monitor_url = serializers.ListField(child=serializers.CharField(max_length=128, required=True,
    #    error_messages={"invalid": "监控地址格式不正确"},
    #    help_text="监控地址"))
    class Meta:
        model = MonitorUrl
        fields = "__all__"


class AlertSerializer(ModelSerializer):
    """
    告警记录序列化
    """

    is_read = serializers.IntegerField(
        help_text="是否已读",
        required=True,
        error_messages={"required": "必须包含是否已读字段"}
    )

    alert_type = serializers.CharField(
        help_text="告警类型",
        required=True, max_length=1024,
        error_messages={"required": "必须包含告警类型字段"}
    )

    alert_host_ip = serializers.CharField(
        help_text="告警来源主机ip",
        required=True, max_length=1024,
        error_messages={"required": "必须包含告警来源主机ip字段"}
    )

    alert_host_instance_name = serializers.CharField(
        help_text="告警主机实例名称",
        required=True, max_length=1024,
        error_messages={"required": "必须包含告警主机实例名称字段"}
    )

    alert_service_name = serializers.CharField(
        help_text="告警服务名称",
        required=True, max_length=1024,
        error_messages={"required": "必须包含告警服务名称字段"}
    )

    alert_service_instance_name = serializers.CharField(
        help_text="告警服务实例名称",
        required=True, max_length=1024,
        error_messages={"required": "必须包含告告警服务实例名称字段"}
    )

    alert_service_type = serializers.CharField(
        help_text="告警服务类型",
        required=True, max_length=1024,
        error_messages={"required": "必须包含告警服务类型字段"}
    )

    alert_level = serializers.CharField(
        help_text="告警级别",
        required=True, max_length=1024,
        error_messages={"required": "必须包含告警级别字段"}
    )

    alert_describe = serializers.CharField(
        help_text="告警描述",
        required=True, max_length=1024,
        error_messages={"required": "必须包含告警描述字段"}
    )

    alert_receiver = serializers.CharField(
        help_text="告警接收人",
        required=True, max_length=1024,
        error_messages={"required": "必须包含告警接收人字段"}
    )

    alert_resolve = serializers.CharField(
        help_text="告警解决方案",
        required=True, max_length=1024,
        error_messages={"required": "必须包含告警解决方案字段"}
    )

    alert_time = serializers.CharField(
        help_text="告警发生时间",
        required=True, max_length=1024,
        error_messages={"required": "必须包含告警发生时间字段"}
    )

    create_time = serializers.CharField(
        help_text="告警信息入库时间",
        required=True, max_length=1024,
        error_messages={"required": "必须包含告警信息入库时间字段"}
    )

    monitor_path = serializers.CharField(
        help_text="跳转监控路径",
        required=True, max_length=1024,
        error_messages={"required": "必须包含跳转监控路径字段"}
    )

    monitor_log = serializers.CharField(
        help_text="跳转监控日志路径",
        required=True, max_length=1024,
        error_messages={"required": "必须包含跳转监控日志路径字段"}
    )

    fingerprint = serializers.CharField(
        help_text="告警的唯一标识",
        required=True, max_length=1024,
        error_messages={"required": "必须包含告警的唯一标识字段"}
    )

    env = serializers.CharField(
        help_text="环境",
        required=True, max_length=1024,
        error_messages={"required": "必须包含告环境字段"}
    )

    class Meta:
        model = Alert
        fields = "__all__"
