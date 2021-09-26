"""
主机序列化器
"""

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import (
    ModelSerializer, Serializer
)

from db_models.models import (Host, Env)
from hosts.tasks import deploy_agent
from hosts.tasks import host_agent_restart

from utils.validator import (
    ReValidator, NoEmojiValidator, NoChineseValidator
)
from utils.plugin.ssh import SSH
from utils.plugin.crypto import AESCryptor


class HostSerializer(ModelSerializer):
    """ 主机序列化类 """

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
    env = serializers.PrimaryKeyRelatedField(
        help_text="环境",
        required=False,
        queryset=Env.objects.all(),
        error_messages={"does_not_exist": "未找到对应环境"})

    class Meta:
        """ 元数据 """
        model = Host
        exclude = ("is_deleted",)
        read_only_fields = (
            "service_num", "alert_num", "host_name", "operate_system",
            "memory", "cpu", "disk", "is_maintenance", "host_agent",
            "monitor_agent", "host_agent_error", "monitor_agent_error",
        )

    def validate_instance_name(self, instance_name):
        """ 校验实例名是否重复 """
        queryset = Host.objects.all()
        if self.instance is not None:
            queryset = queryset.exclude(id=self.instance.id)
        if queryset.filter(instance_name=instance_name).exists():
            raise ValidationError("实例名已经存在")
        return instance_name

    def validate_ip(self, ip):
        """ 校验IP是否重复 """
        if self.instance is not None:
            if ip != self.instance.ip:
                raise ValidationError("该字段不可修改")
            return ip
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

        # 如果未传递 env，则指定默认环境
        if not attrs.get("") and not self.instance:
            attrs["env"] = Env.objects.get(id=1)
        return attrs

    def create(self, validated_data):
        """ 创建主机 """
        # 密码加密处理
        aes_crypto = AESCryptor()
        validated_data["password"] = aes_crypto.encode(
            validated_data.get("password"))
        instance = super(HostSerializer, self).create(validated_data)
        # 异步下发 Agent
        deploy_agent.delay(instance.id)
        return instance


class HostFieldCheckSerializer(ModelSerializer):
    """ 主机字段重复性校验序列化器 """

    id = serializers.IntegerField(
        help_text="主机ID，更新时需要此字段",
        required=False
    )

    instance_name = serializers.CharField(
        help_text="实例名",
        max_length=16, required=False,
        validators=[
            NoEmojiValidator(),
            NoChineseValidator(),
            ReValidator(regex=r"^[-a-z0-9].*$"),
        ])

    ip = serializers.IPAddressField(
        help_text="IP地址", required=False)

    class Meta:
        """ 元数据 """
        model = Host
        fields = ("id", "instance_name", "ip",)

    def validate(self, attrs):
        """ 校验 instance_name / ip 是否重复 """
        host_id = attrs.get("id")
        instance_name = attrs.get("instance_name")
        ip = attrs.get("ip")
        queryset = Host.objects.all()
        if host_id is not None:
            queryset = queryset.exclude(id=host_id)
        if instance_name and \
                queryset.filter(instance_name=instance_name).exists():
            raise ValidationError({"instance_name": "实例名已经存在"})
        if ip and queryset.filter(ip=ip).exists():
            raise ValidationError({"ip": "IP已经存在"})
        return attrs


class HostMaintenanceSerializer(Serializer):
    """ 主机维护模式序列化类 """

    is_maintenance = serializers.BooleanField(
        help_text="开启/关闭维护模式",
        required=True,
        error_messages={"required": "必须包含[is_maintenance]字段"})
    host_ids = serializers.ListSerializer(
        child=serializers.IntegerField(),
        help_text="主机 ID 列表",
        required=True,
        error_messages={"required": "必须包含[host_ids]字段"},
        allow_empty=False)

    def validate_host_ids(self, host_ids):
        """ 校验主机 ID 列表中主机是否都存在 """
        exists_ids = set(Host.objects.filter(
            id__in=host_ids
        ).values_list("id", flat=True))
        diff = set(host_ids) - set(exists_ids)
        if diff:
            raise ValidationError(
                f"有不存在的ID ["
                f"{','.join(map(lambda x: str(x), diff))}"
                f"]")
        return host_ids

    def validate(self, attrs):
        """ 校验列表中主机 '维护模式' 字段值是否正确 """
        queryset = Host.objects.filter(
            id__in=attrs.get("host_ids"),
            is_maintenance=attrs.get("is_maintenance"))
        if queryset.exists():
            status = "开启" if attrs.get("is_maintenance") else "关闭"
            raise ValidationError({
                "host_ids": f"存在已 '{status}' 维护模式的主机"
            })
        return attrs

    def create(self, validated_data):
        """ 进入 / 退出维护 """
        # TODO 调用进入维护模式函数
        # 如果操作成功，则更新数据库配置
        if True:
            Host.objects.filter(
                id__in=validated_data.get("host_ids")
            ).update(is_maintenance=validated_data.get("is_maintenance"))
        return validated_data

    def update(self, instance, validated_data):
        pass


class HostAgentRestartSerializer(Serializer):
    """ 主机Agent重启序列化类 """

    host_ids = serializers.ListField(
        help_text="主机 ID 列表",
        required=True,
        error_messages={"required": "必须包含[host_ids]字段"},
        allow_empty=False)

    def validate_host_ids(self, host_ids):
        """ 校验主机 ID 列表中主机是否都存在 """
        exists_ids = set(Host.objects.filter(
            id__in=host_ids
        ).values_list("id", flat=True))
        diff = set(host_ids) - set(exists_ids)
        if diff:
            raise ValidationError(
                f"有不存在的ID ["
                f"{','.join(map(lambda x: str(x), diff))}"
                f"]")
        return host_ids

    def create(self, validated_data):
        """ 主机Agent重启 """
        for item in validated_data.get("host_ids", []):
            host_agent_restart.delay(item)
        return validated_data
