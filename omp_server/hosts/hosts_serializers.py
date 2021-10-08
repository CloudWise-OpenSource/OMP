"""
主机序列化器
"""
import logging
from concurrent.futures import (
    ThreadPoolExecutor, as_completed
)

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import (
    ModelSerializer, Serializer
)

from db_models.models import (
    Host, Env, HostOperateLog
)
from hosts.tasks import (
    deploy_agent, host_agent_restart
)

from utils.validator import (
    ReValidator, NoEmojiValidator, NoChineseValidator
)
from utils.plugin.ssh import SSH
from utils.plugin.crypto import AESCryptor
from utils.exceptions import OperateError
from utils.parse_config import THREAD_POOL_MAX_WORKERS
from promemonitor.alertmanager import Alertmanager

logger = logging.getLogger('server')


class HostSerializer(ModelSerializer):
    """ 主机序列化类 """

    instance_name = serializers.CharField(
        help_text="实例名",
        required=True, max_length=16,
        error_messages={"required": "必须包含[instance_name]字段"},
        validators=[
            NoEmojiValidator(),
            NoChineseValidator(),
            ReValidator(regex=r"^[-a-zA-Z0-9].*$"),
        ])
    ip = serializers.IPAddressField(
        help_text="IP地址",
        required=True,
        error_messages={"required": "必须包含[ip]字段"})
    port = serializers.IntegerField(
        help_text="端口",
        required=True,
        min_value=1, max_value=65535,
        error_messages={"required": "必须包含[port]字段"})
    username = serializers.CharField(
        help_text="用户名",
        required=True, max_length=16,
        error_messages={"required": "必须包含[username]字段"},
        validators=[
            ReValidator(regex=r"^[_a-zA-Z0-9][-_a-zA-Z0-9]+$"),
        ])
    password = serializers.CharField(
        help_text="密码",
        required=True, min_length=8, max_length=16,
        error_messages={
            "required": "必须包含[password]字段",
            "min_length": "密码长度需大于{min_length}",
            "max_length": "密码长度需小于{max_length}"},
        validators=[
            NoEmojiValidator(),
            NoChineseValidator(),
        ])
    data_folder = serializers.CharField(
        help_text="数据分区",
        required=True, max_length=255,
        error_messages={"required": "必须包含[data_folder]字段"},
        validators=[
            ReValidator(regex=r"^/[-_/a-zA-Z0-9]+$"),
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
        exclude = ("is_deleted", "agent_dir",)
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
                raise ValidationError("IP不可修改")
            return ip
        if Host.objects.filter(ip=ip).exists():
            raise ValidationError("IP已经存在")
        return ip

    def validate_data_folder(self, data_folder):
        """ 校验数据分区是否合理 """
        dir_ls = data_folder.split("/")
        for dir_name in dir_ls:
            if dir_name != "" and dir_name.startswith("-"):
                raise ValidationError("数据分区目录不能以'-'开头")
        return data_folder

    def validate(self, attrs):
        """ 主机信息验证 """
        ip = attrs.get("ip")
        port = attrs.get("port")
        username = attrs.get("username")
        password = attrs.get("password")
        data_folder = attrs.get('data_folder')

        # 校验主机 SSH 连通性
        ssh = SSH(ip, port, username, password)
        is_connect, _ = ssh.check()
        if not is_connect:
            logger.info(f"主机SSH连通性校验未通过: ip-{ip},port-{port},"
                        f"username-{username},password-{password}")
            raise ValidationError({"ip": "SSH登录失败"})
        # 校验用户是否具有 sudo 权限
        is_sudo, _ = ssh.is_sudo()
        if not is_sudo:
            logger.info(f"用户权限校验未通过: ip-{ip},port-{port},"
                        f"username-{username},password-{password}")
            raise ValidationError({
                "username": "用户权限错误，请使用root或具备sudo免密用户"})

        # 如果数据分区不存在，则创建数据分区
        success, _ = ssh.cmd(
            f"test -d {data_folder} || mkdir -p {data_folder}")
        if not success:
            logger.info(f"数据分区创建失败: ip-{ip},port-{port},"
                        f"username-{username},password-{password}"
                        f"data_folder-{data_folder}")
            ValidationError({"data_folder": "创建数据分区操作失败"})

        # 如果未传递 env，则指定默认环境
        if not attrs.get("env") and not self.instance:
            attrs["env"] = Env.objects.get(id=1)
        # 主机密码加密处理
        if attrs.get("password"):
            attrs["password"] = AESCryptor().encode(attrs.get("password"))
        return attrs

    def create(self, validated_data):
        """ 创建主机 """
        ip = validated_data.get('ip')
        # 指定 Agent 安装目录为 data_folder
        validated_data['agent_dir'] = validated_data.get("data_folder")
        instance = super(HostSerializer, self).create(validated_data)
        logger.info(f"主机{ip}-创建成功")
        # 写入操作记录
        HostOperateLog.objects.create(
            username=self.context["request"].user.username,
            description="创建主机",
            host=instance,
        )
        # 异步下发 Agent
        logger.info(f"主机{ip}-异步下发Agent任务")
        deploy_agent.delay(instance.id)
        return instance

    def update(self, instance, validated_data):
        """ 更新主机 """
        log_ls = []
        username = self.context["request"].user.username

        # 获取所有发生修改字段
        for key, new_value in validated_data.items():
            old_value = getattr(instance, key)
            if old_value != new_value:
                description = f"修改[{getattr(Host, key).field.help_text}]"
                if key != "password":
                    description += f": 由[{getattr(instance, key)}]修改为[{new_value}]"
                log_ls.append(HostOperateLog(
                    username=username,
                    description=description,
                    host=instance))

        # 写入主机操作记录表中
        HostOperateLog.objects.bulk_create(log_ls)

        return super(HostSerializer, self).update(instance, validated_data)


class HostFieldCheckSerializer(ModelSerializer):
    """ 主机字段重复性校验序列化器 """

    id = serializers.IntegerField(
        help_text="主机ID，更新时需要此字段",
        required=False)
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

    def write_host_log(self, host_queryset, status):
        """ 写入主机日志 """
        log_ls = []
        for host in host_queryset:
            log_ls.append(HostOperateLog(
                username=self.context["request"].user.username,
                description=f"{status}[维护模式]",
                result="failed",
                host=host))
        HostOperateLog.objects.bulk_create(log_ls)

    def validate_host_ids(self, host_ids):
        """ 校验主机 ID 列表中主机是否都存在 """
        exists_ids = Host.objects.filter(
            id__in=host_ids).values_list("id", flat=True)
        diff = set(host_ids) - set(exists_ids)
        if diff:
            raise ValidationError(
                f"主机列表中有不存在的ID ["
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
                "host_ids": f"主机列表中存在已 '{status}' 维护模式的主机"
            })
        return attrs

    def create(self, validated_data):
        """ 进入 / 退出维护模式 """
        host_ids = validated_data.get("host_ids")
        is_maintenance = validated_data.get("is_maintenance")
        status = "开启" if is_maintenance else "关闭"
        host_queryset = Host.objects.filter(id__in=host_ids)
        host_ls = list(host_queryset.values("ip"))

        # 根据 is_maintenance 判断主机进入 / 退出维护模式
        alert_manager = Alertmanager()
        if is_maintenance:
            res_ls = alert_manager.set_maintain_by_host_list(host_ls)
        else:
            res_ls = alert_manager.revoke_maintain_by_host_list(host_ls)

        # 操作失败
        if not res_ls:
            logger.error(f"主机'{status}'维护模式失败: {host_ids}")
            # 操作失败记录写入
            self.write_host_log(host_queryset, status)
            raise OperateError(f"主机'{status}'维护模式失败")

        # 操作成功
        host_queryset.update(is_maintenance=is_maintenance)
        logger.info(f"主机{status}维护模式成功: {host_ids}")
        # 操作成功记录写入
        self.write_host_log(host_queryset, status)
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
        exists_ids = Host.objects.filter(
            id__in=host_ids).values_list("id", flat=True)
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
        # 下发任务后批量更新重启主机状态
        Host.objects.filter(
            id__in=validated_data.get("host_ids", [])
        ).update(host_agent=1)
        return validated_data


class HostOperateLogSerializer(ModelSerializer):
    """ 主机操作记录序列化器类 """

    class Meta:
        """ 元数据 """
        model = HostOperateLog
        fields = '__all__'


class HostBatchValidateSerializer(Serializer):
    """ 主机数据批量验证 """

    host_list = serializers.ListSerializer(
        child=serializers.DictField(),
        help_text="主机数据列表",
        required=True,
        error_messages={"required": "必须包含[host_list]字段"},
        allow_empty=False)

    def host_info_validate(self, host_data):
        """ 单个主机信息验证 """

        return "correct", host_data

    def validate(self, attrs):
        host_list = attrs.get("host_list")
        """ 校验主机数据列表 """
        # 多线程校验主机数据正确性
        with ThreadPoolExecutor(THREAD_POOL_MAX_WORKERS) as executor:
            future_list = []
            for host_data in host_list:
                future_obj = executor.submit(
                    self.host_info_validate, host_data)
                future_list.append(future_obj)
            result_dict = {
                "correct": [],
                "error": []
            }
            for future in as_completed(future_list):
                flag, host_data = future.result()
                result_dict[flag].append(host_data)
        attrs["result_dict"] = result_dict
        # TODO 待补充
        return attrs

    def create(self, validated_data):
        return validated_data

    def update(self, instance, validated_data):
        pass
