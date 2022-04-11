import time
import django_filters
from db_models.models import SelfHealingHistory
from django_filters.rest_framework import FilterSet
from rest_framework.filters import BaseFilterBackend


class SelfHealingHistoryFilter(FilterSet):
    """自愈历史记录过滤类"""
    host_ip = django_filters.CharFilter(
        help_text="HOST_IP,模糊匹配", field_name="host_ip", lookup_expr="icontains"
    )
    state = django_filters.CharFilter(help_text="STATE,模糊匹配", field_name="state", lookup_expr="icontains")
    instance_name = django_filters.CharFilter(help_text="INSTANCE_NAME,模糊匹配", field_name="instance_name", lookup_expr="icontains")

    class Meta:
        model = SelfHealingHistory
        fields = ("host_ip", "state", "instance_name")


class SelfHealingTimeFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        query_start_time = request.GET.get("query_start_time", "")
        query_end_time = request.GET.get("query_end_time", "")
        if query_start_time and query_end_time:
            try:
                time.strptime(query_start_time, "%Y-%m-%d %H:%M:%S")
                time.strptime(query_end_time, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return queryset.all()
            return queryset.filter(alert_time__range=(query_start_time, query_end_time))
        return queryset.all()