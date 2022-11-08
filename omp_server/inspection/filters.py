# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/10/13 9:02 下午
# Description: 巡检查询
import django_filters
from django_filters.rest_framework import FilterSet
from db_models.models import (
    InspectionHistory, InspectionCrontab, InspectionReport)


class InspectionHistoryFilter(FilterSet):
    """ 巡检历史记录过滤类 """
    inspection_name = django_filters.CharFilter(
        help_text="报告名称：模糊搜索", field_name="inspection_name",
        lookup_expr="icontains")
    inspection_type = django_filters.CharFilter(
        help_text="报告类型:service、host、deep", field_name="inspection_type",
        lookup_expr="icontains")
    execute_type = django_filters.CharFilter(
        help_text="执行方式:手动-man；定时：auto", field_name="execute_type",
        lookup_expr="icontains")
    inspection_status = django_filters.NumberFilter(
        help_text="执行结果:1-进行中；2-成功；3-失败", field_name="inspection_status",
        lookup_expr="icontains")

    class Meta:
        model = InspectionHistory
        fields = ("inspection_type", "execute_type", "inspection_status")


class InspectionCrontabFilter(FilterSet):
    """ 巡检任务配置过滤类 """
    job_type = django_filters.CharFilter(
        help_text="任务类型：0-深度分析 1-主机巡检 2-组建巡检", field_name="job_type",
        lookup_expr="icontains")

    class Meta:
        model = InspectionCrontab
        fields = ("job_type",)


class InspectionReportFilter(FilterSet):
    """ 巡检报告过滤类 """
    inst_id = django_filters.CharFilter(
        help_text="巡检记录历史表id", field_name="inst_id", lookup_expr="icontains")

    class Meta:
        model = InspectionReport
        fields = ("inst_id",)
