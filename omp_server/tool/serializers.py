import json

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from db_models.models import ToolExecuteMainHistory, ToolInfo, Host, Service, \
    ToolExecuteDetailHistory


class ToolInfoSerializer(serializers.ModelSerializer):
    class Meta:
        """ 元数据 """
        model = ToolInfo
        fields = ("target_name",)


class ToolDetailSerializer(serializers.ModelSerializer):
    tool = ToolInfoSerializer()
    duration = serializers.SerializerMethodField()
    tool_detail = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()

    class Meta:
        """ 元数据 """
        model = ToolExecuteMainHistory
        fields = "__all__"

    def get_duration(self, obj):
        return obj.duration

    def get_count(self, obj):
        return ToolExecuteDetailHistory.objects.filter(main_history=obj).count()

    def get_tool_detail(self, obj):
        """
        获取detail详情
        """
        tool_list = []
        tool_obj = ToolExecuteDetailHistory.objects.filter(main_history=obj)
        for obj in tool_obj:
            tool_list.append(
                {
                    "ip": obj.target_ip,
                    "status": obj.status,
                    "log": obj.execute_log
                }
            )
        return tool_list


class ToolFormDetailSerializer(serializers.ModelSerializer):
    default_form = serializers.SerializerMethodField()

    def get_default_form(self, obj):
        return obj.load_default_form()

    class Meta:
        """ 元数据 """
        model = ToolInfo
        fields = ("id", "name", "default_form", "script_args")


class ToolListSerializer(ModelSerializer):
    """工具列表序列化"""
    used_number = serializers.SerializerMethodField()

    def get_used_number(self, obj):
        return ToolExecuteMainHistory.objects.filter(tool=obj).count()

    class Meta:
        model = ToolInfo
        fields = ("id", "logo", "name", "kind", "used_number", "description")


class ToolInfoDetailSerializer(ModelSerializer):
    """工具详情序列化"""

    class Meta:
        model = ToolInfo
        fields = ("name", "description", "logo", "tar_url", "kind",
                  "target_name", "script_path", "script_args", "templates",
                  "readme_info")


class ToolTargetObjectHostSerializer(serializers.ModelSerializer):
    host_agent_state = serializers.SerializerMethodField()

    def get_host_agent_state(self, obj):
        if obj.host_agent == str(obj.AGENT_RUNNING):
            return "正常"
        return "异常"

    class Meta:
        """ 元数据 """
        model = Host
        fields = ("id", "instance_name", "ip", "host_agent_state")


class ToolTargetObjectServiceSerializer(serializers.ModelSerializer):
    instance_name = serializers.CharField(source="service_instance_name")
    host_agent_state = serializers.SerializerMethodField()
    modifiable_kwargs = serializers.SerializerMethodField()

    def get_host_agent_state(self, obj):
        host = Host.objects.filter(ip=obj.ip).first()
        if host and host.host_agent == str(host.AGENT_RUNNING):
            return "正常"
        return "异常"

    def get_modifiable_kwargs(self, obj):
        modifiable_kwargs = {}
        tool = self.context.get("view").kwargs["tool"]
        connection_args = tool.obj_connection_args
        connect_obj = obj.service_connect_info
        port_infos = json.loads(obj.service_port)
        port_dict = {}
        for port_info in port_infos:
            port_dict.update({port_info.get("key"): port_info.get("default")})
        for arg_key in connection_args:
            if arg_key in port_dict:
                modifiable_kwargs[arg_key] = port_dict[arg_key]
            elif connect_obj and hasattr(connect_obj, arg_key):
                modifiable_kwargs[arg_key] = getattr(connect_obj, arg_key)
            else:
                modifiable_kwargs[arg_key] = ""
        return modifiable_kwargs

    class Meta:
        """ 元数据 """
        model = Service
        fields = ("id", "instance_name", "ip", "host_agent_state",
                  "modifiable_kwargs")
