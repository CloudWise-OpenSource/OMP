"""
主机相关过滤器
"""
import time

import django_filters
from django_filters.rest_framework import FilterSet

from db_models.models import (Alert,AlertRule)
from rest_framework.filters import BaseFilterBackend


class AlertFilter(FilterSet):
    """ Alert过滤类 """
    alert_host_ip = django_filters.CharFilter(
        help_text="ALERT_HOST_IP，模糊匹配", field_name="alert_host_ip", lookup_expr="icontains")
    alert_instance_name = django_filters.CharFilter(
        help_text="ALERT_INSTANCE_NAME，模糊匹配", field_name="alert_instance_name", lookup_expr="icontains")
    alert_level = django_filters.CharFilter(
        help_text="ALERT_LEVEL，模糊匹配", field_name="alert_level", lookup_expr="icontains")
    alert_type = django_filters.CharFilter(
        help_text="ALERT_TYPE，模糊匹配", field_name="alert_type", lookup_expr="icontains")

    class Meta:
        model = Alert
        fields = (
            "alert_host_ip", "alert_instance_name", "alert_instance_name",
            "alert_level", "alert_type"
        )

class QuotaFilter(FilterSet):
    """
    指标规则过滤类
    """
    alert = django_filters.CharFilter(
        help_text="alert，规则名称模糊匹配", field_name="alert",
        lookup_expr="icontains"
    )
    class Meta:
        model = AlertRule
        fields = (
            "alert",
        )


class MyTimeFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        start_alert_time = request.GET.get('start_alert_time')
        end_alert_time = request.GET.get('end_alert_time')
        if (not start_alert_time) or (not end_alert_time):
            return queryset.all()
        try:
            time.strptime(start_alert_time, "%Y-%m-%d %H:%M:%S")
            time.strptime(end_alert_time, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return queryset.all()
        return queryset.filter(alert_time__range=(start_alert_time, end_alert_time))
