# -*- coding:utf-8 -*-
# Project: tool_serializers
# Create time: 2022/2/10 11:41 上午
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from db_models.models import (ToolInfo, ToolExecuteMainHistory)


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


class ToolDetailSerializer(ModelSerializer):
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
