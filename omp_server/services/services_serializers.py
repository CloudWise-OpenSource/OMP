"""
服务序列化器
"""
import json
from rest_framework import serializers

from db_models.models import Service


class ServiceSerializer(serializers.ModelSerializer):
    """ 服务序列化器 """

    port = serializers.SerializerMethodField()
    label_name = serializers.SerializerMethodField()
    cluster_type = serializers.SerializerMethodField()
    alert_count = serializers.SerializerMethodField()
    service_status = serializers.CharField(source="get_service_status_display")
    app_type = serializers.IntegerField(source="service.app_type")
    app_name = serializers.CharField(source="service.app_name")
    app_version = serializers.CharField(source="service.app_version")

    class Meta:
        """ 元数据 """
        model = Service
        fields = (
            "service_instance_name", "ip", "port", "label_name", "alert_count",
            "app_type", "app_name", "app_version", "cluster_type", "service_status",
        )

    def get_port(self, obj):
        """ 拼接返回端口 """
        service_port_ls = json.loads(obj.service_port)
        service_port = "-"
        for info in service_port_ls:
            if info.get("service_port", None) is not None:
                service_port = info.get("service_port")
        return service_port

    def get_label_name(self, obj):
        """ 拼接返回标签 """
        label_name = "-"
        if obj.service.app_labels.exists():
            label_name = ", ".join(
                obj.service.app_labels.values_list("label_name", flat=True))
        return label_name

    def get_cluster_type(self, obj):
        """ 获取集群类型 """
        cluster_type = "-"
        if obj.cluster is not None:
            cluster_type = obj.cluster.cluster_type
        return cluster_type

    def get_alert_count(self, obj):
        """ 获取告警数量 """
        alert_count = f"{obj.alert_count}次"
        # 服务状态为 '安装中'、'安装失败' 告警数量显示为 '-'
        if obj.service_status in (
                Service.SERVICE_STATUS_INSTALLING,
                Service.SERVICE_STATUS_INSTALL_FAILED):
            alert_count = "-"
        # '基础环境' 展示为 '-'
        if obj.service.extend_fields.get("base_env") in (True, "True"):
            alert_count = "-"
        return alert_count
