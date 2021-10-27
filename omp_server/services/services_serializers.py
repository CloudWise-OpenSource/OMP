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
    operable = serializers.SerializerMethodField()
    service_status = serializers.CharField(source="get_service_status_display")
    app_type = serializers.IntegerField(source="service.app_type")
    app_name = serializers.CharField(source="service.app_name")
    app_version = serializers.CharField(source="service.app_version")

    class Meta:
        """ 元数据 """
        model = Service
        fields = (
            "id", "service_instance_name", "ip", "port", "label_name", "alert_count",
            "operable", "app_type", "app_name", "app_version", "cluster_type",
            "service_status",
        )

    def get_port(self, obj):
        """ 返回服务 service_port """
        service_port = "-"
        if obj.service_port is not None:
            service_port_ls = json.loads(obj.service_port)
            for info in service_port_ls:
                if info.get("service_port", None) is not None:
                    service_port = info.get("service_port")
                    break
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

    def get_operable(self, obj):
        """ 服务可操作 (启动、停止、重启) """
        if obj.service_controllers is not None:
            service_controllers_dict = json.loads(obj.service_controllers)
            return service_controllers_dict.get("start", "") != ""
        return False


class ServiceDetailSerializer(serializers.ModelSerializer):
    """ 服务详情序列化器 """

    app_name = serializers.CharField(source="service.app_name")
    app_version = serializers.CharField(source="service.app_version")
    label_name = serializers.SerializerMethodField()
    cluster_type = serializers.SerializerMethodField()
    install_info = serializers.SerializerMethodField()
    history = serializers.SerializerMethodField()

    class Meta:
        """ 元数据 """
        model = Service
        fields = (
            "id", "service_instance_name", "app_name", "app_version", "label_name",
            "cluster_type", "ip", "install_info", "history",
        )

    def get_install_info(self, obj):
        """ 安装信息 """
        result = {
            "service_port": "-",
            "base_dir": "-",
            "log_dir": "-",
            "data_dir": "-",
            "username": "-",
            "password": "-",
        }
        # 端口号
        service_port_ls = json.loads(obj.service_port)
        for info in service_port_ls:
            if info.get("service_port", None) is not None:
                result["service_port"] = info.get("service_port", "-")
                break
        # 应用安装参数
        app_install_args = "[]"
        if obj.service.app_install_args is not None:
            app_install_args = obj.service.app_install_args
        app_install_args = json.loads(app_install_args)
        for app_install_info in app_install_args:
            key = app_install_info.get("key", "")
            if key in result.keys():
                result[key] = app_install_info.get("default", "-")
        return result

    def get_label_name(self, obj):
        """ 获取拼接后的标签 """
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

    def get_history(self, obj):
        """ 获取历史记录 """
        return list(obj.servicehistory_set.values(
            "username", "description", "result", "created"))

class ServiceActionSerializer(serializers.ModelSerializer):
    """ 服务动作序列化类 """

    class Meta:
        """ 元数据 """
        model = Service
        fields = '__all__'
