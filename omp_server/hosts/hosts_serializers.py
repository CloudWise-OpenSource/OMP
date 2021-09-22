"""
主机序列化器
"""
import re
import emoji
from django.contrib.auth.hashers import make_password

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer
from rest_framework.validators import UniqueValidator

from db_models.models import Host
from utils.plugin.ssh import SSH


class ReValidator:
    """ 正则表达式验证器 """

    def __init__(self, regex, message):
        self.regex = regex
        self.message = message

    def __call__(self, value):
        if re.match(self.regex, value) is None:
            raise ValidationError(self.message)


class EmojiValidator:
    """ 表情验证器 """

    def __init__(self, message):
        self.message = message

    def __call__(self, value):
        # TODO 逻辑待完善
        pass


class HostSerializer(ModelSerializer):
    """ 用户序列化类 """

    instance_name = serializers.CharField(
        help_text="实例名",
        required=True, max_length=16,
        error_messages={"required": "必须包含[instance_name]字段"},
        validators=[
            ReValidator(
                regex=r"^[-a-z0-9][-_a-zA-Z0-9]+$",
                message="[instance_name]字段不符合规范"),
            # UniqueValidator(
            #     queryset=Host.objects.all(),
            #     message="[instance_name]已经存在"),
        ])
    ip = serializers.IPAddressField(
        help_text="IP地址",
        required=True,
        error_messages={"required": "必须包含[ip]字段"},
        validators=[UniqueValidator(
            queryset=Host.objects.all(),
            message="[ip]已经存在")])
    port = serializers.IntegerField(
        help_text="SSH端口，范围1~65535",
        required=True, max_value=65535,
        error_messages={"required": "必须包含[port]字段"})
    username = serializers.CharField(
        help_text="SSH登录用户名",
        required=True, max_length=16,
        error_messages={"required": "必须包含[username]字段"})
    password = serializers.CharField(
        help_text="SSH登录密码",
        required=True, max_length=16,
        write_only=True,
        error_messages={"required": "必须包含[password]字段"})
    data_folder = serializers.CharField(
        help_text="数据分区，需要以 / 开头",
        required=True, max_length=255,
        error_messages={"required": "必须包含[data_folder]字段"})
    operate_system = serializers.CharField(
        help_text="操作系统",
        required=True, max_length=128,
        error_messages={"required": "必须包含[operate_system]字段"})

    class Meta:
        """ 元数据 """
        model = Host
        exclude = ("is_deleted", "env")
        read_only_fields = (
            "service_num", "alert_num", "host_name", "operate_system",
            "memory", "cpu", "disk", "is_maintenance", "host_agent",
            "monitor_agent", "host_agent_error", "monitor_agent_error"
        )

    def validate_data_folder(self, data_folder):
        """ 校验数据分区，是否以 '/' 开头 """
        if not data_folder.startswith("/"):
            raise ValidationError("数据分区需以 '/' 开头")
        return data_folder

    def validate(self, attrs):
        """
        主机信息验证：
            1. ssh 连接性
            2. 不允许修改 ip
        """
        ssh = SSH(
            hostname=attrs.get("ip"),
            port=attrs.get("port"),
            username=attrs.get("username"),
            password=attrs.get("password")
        )
        is_connect, message = ssh.check()
        if not is_connect:
            raise ValidationError({"ip": "主机SSH连通性校验失败"})

        # 当请求方式为 PUT/PATCH，且存在对于 IP 值的修改，则抛出验证错误
        request_method = self.context["request"].method
        if request_method in ("PUT", "PATCH") and \
                attrs.get("ip") and \
                attrs.get("ip") != self.instance.ip:
            raise ValidationError({"ip": "该字段不可修改"})
        return attrs

    def create(self, validated_data):
        """ 创建主机 """
        # 密码加密处理
        validated_data["password"] = make_password(validated_data.get("password"))
        instance = super(HostSerializer, self).create(validated_data)
        # TODO 异步下发 Agent
        return instance
