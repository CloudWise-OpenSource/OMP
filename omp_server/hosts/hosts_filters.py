"""
主机相关过滤器
"""
import django_filters
from django_filters.rest_framework import FilterSet

from db_models.models import (Host, HostOperateLog)


class HostFilter(FilterSet):
    """ 主机过滤类 """
    ip = django_filters.CharFilter(
        help_text="IP，模糊匹配", field_name="ip", lookup_expr="icontains")

    class Meta:
        model = Host
        fields = ("ip",)


class HostOperateFilter(FilterSet):
    """ 主机日志过滤类 """

    host_id = django_filters.CharFilter(
        help_text="主机 ID", field_name="host_id", lookup_expr="exact")

    class Meta:
        model = HostOperateLog
        fields = ("host_id",)
