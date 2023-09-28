import datetime
import logging

from django.db.models import F
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer, ListSerializer, \
    Serializer

from db_models.models import Host, MonitorUrl, Alert, Maintain, Service, Rule, AlertRule, WaitSelfHealing
from promemonitor.alert_util import AlertAnalysis
from promemonitor.alertmanager import Alertmanager
from promemonitor.tasks import monitor_agent_restart
from utils.common.exceptions import OperateError
from utils.common.serializers import HostIdsSerializer
from utils.common.validators import (
    NoEmojiValidator, NoChineseValidator
)

logger = logging.getLogger('server')


class MonitorUrlListSerializer(ListSerializer):

    def update(self, instance, validated_data):
        pass

    def to_internal_value(self, data):
        return data.get('data')

    def validate(self, data):
        queryset = MonitorUrl.objects.all()
        method = self.context["request"].method
        for i in data:
            if method in ('PATCH', 'PUT', 'DELETE'):
                if not i.get("id"):
                    raise serializers.ValidationError("id是必须字段")
            monitor_url = i.get("monitor_url")
            if method != 'GET':
                if not monitor_url:
                    raise serializers.ValidationError("monitor_url是必须字段")
                if len(monitor_url) > 128:
                    raise serializers.ValidationError(
                        f"monitor_url字段超过128,detail:{monitor_url}")
                name = i.get("name")
                if name:
                    if queryset.filter(name=name).exists():
                        raise serializers.ValidationError(
                            f"name字段已经存在,detail:{name}")
                    if len(name) > 32:
                        raise serializers.ValidationError(
                            f"name字段长度超过32,detail:{name}")
                else:
                    raise serializers.ValidationError("name字段不为空")
        return data

    def create(self, validated_data):
        monitor = [MonitorUrl(**item) for item in validated_data]
        return MonitorUrl.objects.bulk_create(monitor)


class MonitorUrlSerializer(ModelSerializer):
    """
    监控配置项序列化
    """
    name = serializers.CharField(
        max_length=32, required=True,
        error_messages={"invalid": "监控名字重复"},
        help_text="监控名字")
    id = serializers.IntegerField(
        max_value=100, required=False,
        error_messages={"invalid": "id格式不正确"},
        help_text="id")

    monitor_url = serializers.CharField(
        required=True,
        error_messages={"invalid": "监控地址格式不正确"},
        validators=[
            NoEmojiValidator(message="url地址存在非法字符"),
            NoChineseValidator(message="url地址存在非法字符"),
        ],
        help_text="监控地址")

    class Meta:
        model = MonitorUrl
        fields = "__all__"
        list_serializer_class = MonitorUrlListSerializer

    def validate_name(self, name):
        """ 校验name是否重复 """
        queryset = MonitorUrl.objects.all()
        if self.instance is not None:
            queryset = queryset.exclude(id=self.instance.id)
        if queryset.filter(name=name).exists():
            raise ValidationError("name已经存在")
        return name

    def validate_monitor_url(self, monitor_url):
        if len(monitor_url.split(" ")) > 1:
            raise ValidationError("url地址存在非法字符")
        return monitor_url


class ListAlertSerializer(ModelSerializer):
    class Meta:
        model = Alert
        fields = "__all__"


class UpdateAlertSerializer(Serializer):
    """
    告警记录序列化
    """

    ids = serializers.ListField(
        help_text="告警记录ID列表",
        required=True,
        error_messages={"required": "必须包含ID列表字段"}
    )

    is_read = serializers.IntegerField(
        help_text="是否已读",
        required=True,
        error_messages={"required": "必须包含是否已读字段"}
    )

    # def validate(self, attrs):
    #     # TODO 做校验
    #     return attrs

    def create(self, validated_data):
        Alert.objects.filter(id__in=validated_data.get('ids')).update(
            is_read=validated_data.get('is_read'))
        return validated_data

    def update(self, instance, validated_data):
        pass


class MaintainSerializer(ModelSerializer):
    maintain_id = serializers.CharField(
        help_text="维护唯一标识",
        required=False, max_length=1024,
        error_messages={"required": "maintain_id不可重复"}
    )
    matcher_name = serializers.CharField(
        help_text="匹配标签",
        required=True, max_length=1024,
        error_messages={"required": "必须包含匹配标签"}
    )
    matcher_value = serializers.CharField(
        help_text="维护唯一标识",
        required=True, max_length=1024,
        error_messages={"required": "必须包含匹配标签值"}
    )

    def validate(self, attrs):
        """ 校验env是否存在 """
        return attrs

    def create(self, validated_data):
        """ 进入 / 退出维护模式 """
        matcher_name = validated_data.get("matcher_name")
        matcher_value = validated_data.get("matcher_value")
        maintain_queryset = Maintain.objects.filter(
            matcher_name=matcher_name, matcher_value=matcher_value)

        status = "开启" if not maintain_queryset.exists() else "关闭"

        # 根据 maintain_id 判断主机进入 / 退出维护模式
        alert_manager = Alertmanager()
        if not maintain_queryset.exists():
            res_ls = alert_manager.set_maintain_by_env_name(matcher_value)
        else:
            res_ls = alert_manager.revoke_maintain_by_env_name(matcher_value)

        # 操作失败
        if not res_ls:
            logger.error(f"全局{status}维护模式失败")
            # 操作失败记录写入
            raise OperateError(f"全局{status}维护模式失败")

        # 操作成功
        logger.info(f"全局{status}维护模式成功")
        return validated_data

    class Meta:
        model = Maintain
        fields = "__all__"


class ReceiveAlertSerializer(Serializer):
    receiver = serializers.CharField(
        help_text="接收者",
        required=True,
        error_messages={"required": "不可为空"},
    )
    status = serializers.CharField(
        help_text="状态",
        required=True,
        error_messages={"required": "不可为空"},
    )
    alerts = serializers.ListField(
        help_text="告警内容",
        required=True,
        error_messages={"required": "不可为空"},
    )

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        alerts = validated_data.get('alerts')
        for ele in alerts:
            alert_analysis = AlertAnalysis(ele)
            alert_info = alert_analysis()
            if not alert_info:
                continue
            if alert_info.get('status') != 'firing':
                continue
            alert = Alert(
                is_read=0,
                alert_type=alert_info.get('alert_type'),
                alert_host_ip=alert_info.get('alert_host_ip'),
                alert_service_name=alert_info.get('alert_service_name'),
                alert_instance_name=alert_info.get('alert_instance_name'),
                alert_service_type='',  # TODO 暂时拿不到值
                alert_level=alert_info.get('alert_level'),
                alert_describe=alert_info.get('alert_describe'),
                alert_receiver=alert_info.get('alert_receiver'),
                alert_resolve='',  # TODO 待后续
                alert_time=alert_info.get('alert_time'),
                create_time=datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"),
                monitor_path=alert_info.get('monitor'),
                monitor_log=alert_info.get('monitor_log'),
                fingerprint=alert_info.get('fingerprint'),
                # env='default'  # TODO 此版本默认不赋值
            )
            alert.save()
            # TODO service_name暂时为告警类型
            service_name = alert_info.get('alert_type')
            WaitSelfHealing.objects.create(repair_ser=alert_info, service_name=service_name)
            if alert_info.get('alert_type') == 'host':
                Host.objects.filter(ip=alert_info.get('alert_host_ip')).update(
                    alert_num=F("alert_num") + 1)
            if alert_info.get('alert_type') == 'service':
                Service.objects.filter(service_instance_name=alert_info.get(
                    'alert_instance_name')).filter(
                    ip=alert_info.get('alert_host_ip')).update(
                    service_status=Service.SERVICE_STATUS_STOP,
                    alert_count=F("alert_count") + 1)  # TODO 后续在模型中增加异常字段
        return validated_data


class MonitorAgentRestartSerializer(HostIdsSerializer):
    """ 监控Agent重启序列化类 """

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        """ 监控Agent重启 """
        host_ids = validated_data.get("host_ids", [])
        filter_host_ids = list(
            Host.objects.filter(
                id__in=host_ids,
                monitor_agent__in=[
                    str(Host.AGENT_RUNNING),
                    str(Host.AGENT_RESTART),
                    str(Host.AGENT_START_ERROR)
                ]
            ).values_list("id", flat=True)
        )
        for item in filter_host_ids:
            monitor_agent_restart.delay(item)
        # 下发任务后批量更新重启主机状态
        Host.objects.filter(
            id__in=filter_host_ids
        ).update(monitor_agent=Host.AGENT_RESTART)
        return validated_data


class RuleSerializer(ModelSerializer):
    """
    内置规则序列化类
    """

    class Meta:
        """
        元数据
        """
        model = Rule
        fields = '__all__'


class QuotaSerializer(ModelSerializer):
    """
    告警规则序列化类
    """

    class Meta:
        """
        元数据
        """
        model = AlertRule
        fields = '__all__'
