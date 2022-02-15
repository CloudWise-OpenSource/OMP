from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from db_models.models import (
    ToolExecuteMainHistory,
    ToolExecuteDetailHistory,
    ToolInfo
)


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
    task_name = serializers.CharField(source="name")
    target_objs = serializers.SerializerMethodField()
    form_info = serializers.SerializerMethodField()

    def get_form_info(self, obj):
        default_form = obj.load_default_form()
        return default_form + obj.script_args

    def get_target_objs(self, obj):
        return []

    class Meta:
        """ 元数据 """
        model = ToolInfo
        fields = ("name", "task_name", "target_name", "target_objs",
                  "form_info")


class ToolListSerializer(ModelSerializer):
    """工具列表序列化"""
    used_number = serializers.SerializerMethodField()
    logo = serializers.SerializerMethodField()

    class Meta:
        model = ToolInfo
        fields = ("id", "logo", "name", "kind", "used_number", "description")

    def get_logo(self, obj):
        return obj.logo

    def get_used_number(self, obj):
        return ToolExecuteMainHistory.objects.filter(tool=obj).count()


class ToolInfoDetailSerializer(ModelSerializer):
    """工具详情序列化"""
    logo = serializers.SerializerMethodField()
    tar_url = serializers.SerializerMethodField()
    templates = serializers.SerializerMethodField()

    class Meta:
        model = ToolInfo
        fields = (
            "name", "description", "logo", "tar_url", "kind", "target_name", "script_path", "script_args", "templates",
            "readme_info")

    def get_logo(self, obj):
        return obj.logo

    def get_tar_url(self, obj):
        return obj.tar_url

    def get_templates(self, obj):
        return obj.templates
