"""
主机相关过滤器
"""
import django_filters
from django_filters.rest_framework import FilterSet

from db_models.models import Host


class HostFilter(FilterSet):
    """ 主机过滤类 """
    ip = django_filters.CharFilter(
        help_text="IP，模糊匹配", field_name="ip", lookup_expr="icontains")

    class Meta:
        model = Host
        fields = ("ip",)
