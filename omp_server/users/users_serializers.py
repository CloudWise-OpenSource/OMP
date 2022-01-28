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
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import (
    ModelSerializer, Serializer
)
from rest_framework_jwt.serializers import JSONWebTokenSerializer

from db_models.models import (
    UserProfile, OperateLog,
    UserLoginLog
)
from utils.common.validators import UserPasswordValidator


class UserSerializer(ModelSerializer):
    """ 用户序列化类 """
    re_password = serializers.CharField(
        max_length=32, required=True,
        write_only=True,
        error_messages={"required": "必须包含re_password字段"},
        help_text="二次确认密码")
    email = serializers.EmailField(
        required=True,
        error_messages={"required": "必须包含email字段", "invalid": "邮箱格式不正确"},
        help_text="电子邮件")
    password = serializers.CharField(
        max_length=32, required=True,
        write_only=True,
        error_messages={"required": "必须包含password字段"},
        help_text="密码")
    username = serializers.CharField(
        max_length=32, required=True,
        error_messages={"required": "必须包含名字"},
        help_text="用户名")

    class Meta:
        """ 元数据 """
        model = UserProfile
        fields = ("id", "username", "password", "email", "re_password",
                  "date_joined", "is_active", "is_superuser")
        read_only_fields = ("date_joined", "is_active", "is_superuser")

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
    """ 用户操作记录序列化 """

    create_time = serializers.SerializerMethodField()

    class Meta:
        """ 元数据 """
        model = OperateLog
        fields = (
            "id", "username", "request_ip", "request_method",
            "description", "create_time"
        )

    def get_create_time(self, obj):
        if obj.create_time:
            return str(obj.create_time).split(".")[0]
        return obj.create_time


class UserLoginOperateSerializer(ModelSerializer):
    """登录记录序列化"""

    login_time = serializers.SerializerMethodField()

    class Meta:
        """ 元数据 """
        model = UserLoginLog
        fields = "__all__"

    def get_login_time(self, obj):
        if obj.login_time:
            return str(obj.login_time).split(".")[0]
        return obj.login_time


class JwtSerializer(JSONWebTokenSerializer):
    """ Jwt序列化类 """

    remember = serializers.BooleanField(
        required=False, default=False,
        help_text="Boolean类型，缺省值为False")

    def validate(self, attrs):
        validate_dict = super(JwtSerializer, self).validate(attrs)
        validate_dict["remember"] = attrs.get("remember")
        return validate_dict


class UserUpdatePasswordSerializer(Serializer):
    """ 用户更新密码序列化器 """

    username = serializers.CharField(
        help_text="用户名",
        max_length=32, required=True,
        error_messages={"required": "必须包含名字"})
    old_password = serializers.CharField(
        help_text="原密码", required=True,
        min_length=8, max_length=16,
        error_messages={"required": "必须包含password字段"},
        validators=[
            UserPasswordValidator(),
        ])
    new_password = serializers.CharField(
        help_text="新密码", required=True,
        min_length=8, max_length=16,
        error_messages={"required": "必须包含password字段"},
        validators=[
            UserPasswordValidator(),
        ])

    def validate(self, attrs):
        """ 校验，用户的原密码是否正确 """
        credentials = {
            "username": attrs.get("username"),
            "password": attrs.get("old_password")
        }
        user = authenticate(**credentials)
        if not user:
            raise ValidationError({"old_password": "当前密码不正确"})
        attrs["user_obj"] = user
        return attrs

    def create(self, validated_data):
        """ 用户密码加密入库 """
        user = validated_data["user_obj"]
        user.set_password(
            validated_data.get("new_password"))
        user.save()
        return validated_data
