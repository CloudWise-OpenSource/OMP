"""
主机相关过滤器
"""
import time

import django_filters
from django_filters.rest_framework import FilterSet

from db_models.models import (Alert)
from rest_framework.filters import BaseFilterBackend


class AlertFilter(FilterSet):
    """ 主机过滤类 """
    alert_host_ip = django_filters.CharFilter(
        help_text="ALERT_HOST_IP，模糊匹配", field_name="alert_host_ip", lookup_expr="icontains")
    alert_host_instance_name = django_filters.CharFilter(
        help_text="ALERT_HOST_INSTANCE_NAME，模糊匹配", field_name="alert_host_instance_name", lookup_expr="icontains")
    alert_service_instance_name = django_filters.CharFilter(
        help_text="ALERT_SERVICE_INSTANCE_NAME，模糊匹配", field_name="alert_service_instance_name", lookup_expr="icontains")
    alert_level = django_filters.CharFilter(
        help_text="ALERT_LEVEL，模糊匹配", field_name="alert_level", lookup_expr="icontains")
    alert_type = django_filters.CharFilter(
        help_text="ALERT_TYPE，模糊匹配", field_name="alert_type", lookup_expr="icontains")

    class Meta:
        model = Alert
        fields = (
            "alert_host_ip", "alert_host_instance_name", "alert_service_instance_name",
            "alert_level", "alert_type"
        )


class MyTimeFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        start_alert_time = request.GET.get('start_alert_time')
        end_alert_time = request.GET.get('end_alert_time')
        if (not start_alert_time) or (not end_alert_time):
            return queryset.all()
        try:
            time.strptime(start_alert_time, "%Y-%m-%d")
            time.strptime(end_alert_time, "%Y-%m-%d")
        except ValueError:
            return queryset.all()
        return queryset.filter(alert_time__range=(start_alert_time, end_alert_time))
