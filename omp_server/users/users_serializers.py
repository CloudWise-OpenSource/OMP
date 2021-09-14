# -*- coding: utf-8 -*-
# Project: users_serializers
# Author: jon.liu@yunzhihui.com
# Create time: 2021-09-10 17:16
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
用户序列化使用方法
"""

from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from db_models.models import UserProfile
from db_models.models import OperateLog


class UserSerializer(ModelSerializer):
    """用户序列化类"""
    re_password = serializers.CharField(
        max_length=32, required=True,
        write_only=True, error_messages={"required": "必须包含re_password字段"})
    email = serializers.EmailField(
        required=True,
        error_messages={"required": "必须包含email字段", "invalid": "邮箱格式不正确"})
    password = serializers.CharField(
        max_length=32, required=True,
        error_messages={"required": "必须包含password字段"})
    username = serializers.CharField(
        max_length=32, required=True,
        error_messages={"required": "必须包含名字"})

    class Meta:
        """元数据"""
        model = UserProfile
        fields = ["id", "username", "password", "email", "re_password"]

    def validate_username(self, username):
        """
        校验用户名是否唯一
        :param username: 用户名
        :return:
        """
        request = self.context["request"]
        if request.method != "PUT" and \
                UserProfile.objects.filter(username=username).count() != 0:
            raise ValidationError("用户名已存在")
        return username

    def validate(self, attrs):
        """
        校验
        :param attrs:
        :return:
        """
        password = attrs.get('password')
        re_password = attrs.pop('re_password')
        if password != re_password:
            raise ValidationError({'re_password': '两次密码不一致'})
        attrs["password"] = make_password(password)
        return attrs


class OperateLogSerializer(ModelSerializer):
    """用户操作记录序列化"""
    class Meta:
        """元数据"""
        model = OperateLog
        fields = "__all__"
