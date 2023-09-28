"""
服务相关过滤器
"""
import django_filters
from django_filters.rest_framework import FilterSet

from db_models.models import Service


class ServiceFilter(FilterSet):
    """ 服务过滤类 """
    ip = django_filters.CharFilter(
        help_text="IP，模糊匹配", field_name="ip", lookup_expr="icontains")
    service_instance_name = django_filters.CharFilter(
        help_text="服务实例名称，模糊匹配", field_name="service_instance_name", lookup_expr="icontains")
    label_name = django_filters.CharFilter(
        help_text="功能模块", field_name="service__app_labels__label_name", lookup_expr="icontains")
    app_type = django_filters.CharFilter(
        help_text="服务类型: 0-组件 1-应用", field_name="service__app_type", lookup_expr="exact")

    class Meta:
        model = Service
        fields = ("ip",)
