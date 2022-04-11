# -*- coding:utf-8 -*-
# Project: tool_filters
# Create time: 2022/2/10 3:23 下午
import django_filters
from django_filters.rest_framework import FilterSet
from rest_framework.filters import BaseFilterBackend

from db_models.models import ToolInfo


class ToolFilter(FilterSet):
    name = django_filters.CharFilter(
        help_text="实用工具名称", field_name="name", lookup_expr="icontains")
    kind = django_filters.NumberFilter(
        help_text="实用工具分类：0-管理工具；2-安全工具",
        field_name="kind",
        lookup_expr="exact"
    )

    class Meta:
        model = ToolInfo
        fields = ("name", "kind")


class ToolInfoKindFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        param = request.query_params.get("kind", "")
        param = param.replace('\x00', '').replace('null', '')
        if not param:
            return queryset
        queryset = queryset.filter(tool__kind=int(param))
        return queryset
