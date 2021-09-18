"""
主机序列化器
"""
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer
from rest_framework.validators import UniqueValidator

from db_models.models import Host
from utils.plugin.ssh import SSH


class HostSerializer(ModelSerializer):
    """ 用户序列化类 """

    instance_name = serializers.CharField(
        help_text="实例名",
        required=True, max_length=16,
        error_messages={"required": "必须包含[instance_name]字段"},
        validators=[UniqueValidator(
            queryset=Host.objects.all(),
            message='[instance_name]已经存在')])
    ip = serializers.IPAddressField(
        help_text="IP地址",
        required=True,
        error_messages={"required": "必须包含[IP]字段"},
        validators=[UniqueValidator(
            queryset=Host.objects.all(),
            message='[instance_name]已经存在')])
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

    def validate_data_folder(self, data_folder):
        """ 校验数据分区，是否以 '/' 开头 """
        if not data_folder.startswith("/"):
            raise ValidationError("数据分区需以 '/' 开头")
        return data_folder

    def validate(self, attrs):
        """
        校验主机SSH连通性
        """
        ssh = SSH(
            hostname=attrs.get("ip"),
            port=attrs.get("port"),
            username=attrs.get("username"),
            password=attrs.get("password")
        )
        is_connect, message = ssh.check()
        if not is_connect:
            raise ValidationError({'ip': '主机SSH连通性校验失败'})
        return attrs

    def create(self, validated_data):
        """ 创建主机 """
        instance = super(HostSerializer, self).create(validated_data)
        # TODO 异步下发 Agent
        return instance

