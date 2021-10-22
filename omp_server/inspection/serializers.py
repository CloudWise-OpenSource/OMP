# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/10/13 8:36 下午
# Description: 巡检序列化
from rest_framework.serializers import (ModelSerializer,)
from db_models.models import (
    InspectionHistory, InspectionCrontab, InspectionReport)


class InspectionHistorySerializer(ModelSerializer):
    """ 巡检记录历史表 """

    class Meta:
        """ 元数据 """
        model = InspectionHistory
        fields = "__all__"


class InspectionCrontabSerializer(ModelSerializer):
    """ 巡检任务 配置表 """

    class Meta:
        """ 元数据 """
        model = InspectionCrontab
        fields = "__all__"


class InspectionReportSerializer(ModelSerializer):
    """ 巡检报告表 """

    class Meta:
        """ 元数据 """
        model = InspectionReport
        fields = "__all__"
