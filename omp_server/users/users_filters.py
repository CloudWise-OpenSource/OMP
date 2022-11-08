"""
用户相关过滤器
"""
import django_filters
from django_filters.rest_framework import FilterSet

from db_models.models import (
    UserProfile, OperateLog,
    UserLoginLog
)


class UserFilter(FilterSet):
    """ 主机过滤类 """
    username = django_filters.CharFilter(
        help_text="用户名，模糊匹配", field_name="username", lookup_expr="icontains")

    class Meta:
        model = UserProfile
        fields = ("username",)


class UserOperateFilter(FilterSet):
    """ 用户操作过滤类 """

    username = django_filters.CharFilter(
        help_text="操作用户", field_name="username", lookup_expr="icontains")

    class Meta:
        model = OperateLog
        fields = ("username",)


class UserLoginOperateFilter(FilterSet):
    """ 用户登陆日志过滤类 """

    username = django_filters.CharFilter(
        help_text="操作用户", field_name="username", lookup_expr="icontains")

    class Meta:
        model = UserLoginLog
        fields = ("username",)
