"""
应用商店相关过滤器
"""
import django_filters
from django_filters.rest_framework import FilterSet

from db_models.models import Labels


class LabelFilter(FilterSet):
    """ 标签过滤类 """
    label_type = django_filters.CharFilter(
        help_text="标签类型: 0-组件 1-应用", field_name="label_type", lookup_expr="exact")

    class Meta:
        model = Labels
        fields = ("label_type",)
