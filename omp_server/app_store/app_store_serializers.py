"""
应用商店
"""
import logging

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from db_models.models import ApplicationHub

logger = logging.getLogger("server")


class ComponentListSerializer(ModelSerializer):
    """ 组件列表序列化器 """
    instance_number = serializers.SerializerMethodField()

    class Meta:
        """ 元数据 """
        model = ApplicationHub
        fields = ("app_name", "app_version",
                  "app_description", "instance_number")

    def get_instance_number(self, obj):
        """ 获取组件已安装实例数量 """
        # TODO 计算组件的已安装实例数量
        return 1111
