from rest_framework import serializers
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
