"""
主机序列化器
"""

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from db_models.models import Host
from hosts.tasks import deploy_agent

from utils.validator import (
    ReValidator, NoEmojiValidator, NoChineseValidator
)
from utils.plugin.ssh import SSH
from utils.plugin.crypto import AESCryptor


class HostSerializer(ModelSerializer):
    """ 用户序列化类 """

    instance_name = serializers.CharField(
        help_text="实例名",
        required=True, max_length=16,
        error_messages={"required": "必须包含[instance_name]字段"},
        validators=[
            NoEmojiValidator(),
            NoChineseValidator(),
            ReValidator(regex=r"^[-a-z0-9].*$"),
        ])
    ip = serializers.IPAddressField(
        help_text="IP地址",
        required=True,
        error_messages={"required": "必须包含[ip]字段"})
    port = serializers.IntegerField(
        help_text="SSH端口，范围1~65535",
        required=True,
        min_value=1, max_value=65535,
        error_messages={"required": "必须包含[port]字段"})
    username = serializers.CharField(
        help_text="SSH登录用户名",
        required=True, max_length=16,
        error_messages={"required": "必须包含[username]字段"},
        validators=[
            ReValidator(regex=r"^[_a-zA-Z0-9][-_a-zA-Z0-9]+$"),
        ])
    password = serializers.CharField(
        help_text="SSH登录密码",
        required=True, max_length=16,
        write_only=True,
        error_messages={"required": "必须包含[password]字段"},
        validators=[
            NoEmojiValidator(),
            NoChineseValidator(),
        ])
    data_folder = serializers.CharField(
        help_text="数据分区，需要以 / 开头",
        required=True, max_length=255,
        error_messages={"required": "必须包含[data_folder]字段"},
        validators=[
            ReValidator(regex=r"^/[/-_a-zA-Z0-9]+$"),
        ])
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

    def validate_instance_name(self, instance_name):
        """ 校验实例名是否重复 """
        if Host.objects.filter(instance_name=instance_name).exists():
            raise ValidationError("实例名已经存在")
        return instance_name

    def validate_ip(self, ip):
        """ 校验IP是否重复 """
        if Host.objects.filter(ip=ip).exists():
            raise ValidationError("IP已经存在")
        return ip

    def validate(self, attrs):
        """ 主机信息验证 """
        # 校验主机 SSH 连通性
        ssh = SSH(
            hostname=attrs.get("ip"),
            port=attrs.get("port"),
            username=attrs.get("username"),
            password=attrs.get("password")
        )
        is_connect, _ = ssh.check()
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
        aes_crypto = AESCryptor()
        validated_data["password"] = aes_crypto.encode(validated_data.get("password"))
        instance = super(HostSerializer, self).create(validated_data)
        # 异步下发 Agent
        deploy_agent.delay(instance.id)
        return instance
