import datetime
import logging

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, ListSerializer, Serializer
from rest_framework.exceptions import ValidationError

from db_models.models import Host, MonitorUrl, Alert, Maintain
from promemonitor.tasks import monitor_agent_restart
from utils.exceptions import OperateError
from utils.public_serializer import HostIdsSerializer
from promemonitor.alertmanager import Alertmanager
from promemonitor.alert_util import AlertAnalysis

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


class AlertSerializer(ModelSerializer):
    """
    告警记录序列化
    """

    is_read = serializers.IntegerField(
        help_text="是否已读",
        required=True,
        error_messages={"required": "必须包含是否已读字段"}
    )

    alert_type = serializers.CharField(
        help_text="告警类型",
        required=True, max_length=1024,
        error_messages={"required": "必须包含告警类型字段"}
    )

    alert_host_ip = serializers.CharField(
        help_text="告警来源主机ip",
        required=True, max_length=1024,
        error_messages={"required": "必须包含告警来源主机ip字段"}
    )

    alert_host_instance_name = serializers.CharField(
        help_text="告警主机实例名称",
        required=True, max_length=1024,
        error_messages={"required": "必须包含告警主机实例名称字段"}
    )

    alert_service_name = serializers.CharField(
        help_text="告警服务名称",
        required=True, max_length=1024,
        error_messages={"required": "必须包含告警服务名称字段"}
    )

    alert_service_instance_name = serializers.CharField(
        help_text="告警服务实例名称",
        required=True, max_length=1024,
        error_messages={"required": "必须包含告告警服务实例名称字段"}
    )

    alert_service_type = serializers.CharField(
        help_text="告警服务类型",
        required=True, max_length=1024,
        error_messages={"required": "必须包含告警服务类型字段"}
    )

    alert_level = serializers.CharField(
        help_text="告警级别",
        required=True, max_length=1024,
        error_messages={"required": "必须包含告警级别字段"}
    )

    alert_describe = serializers.CharField(
        help_text="告警描述",
        required=True, max_length=1024,
        error_messages={"required": "必须包含告警描述字段"}
    )

    alert_receiver = serializers.CharField(
        help_text="告警接收人",
        required=True, max_length=1024,
        error_messages={"required": "必须包含告警接收人字段"}
    )

    alert_resolve = serializers.CharField(
        help_text="告警解决方案",
        required=True, max_length=1024,
        error_messages={"required": "必须包含告警解决方案字段"}
    )

    alert_time = serializers.CharField(
        help_text="告警发生时间",
        required=True, max_length=1024,
        error_messages={"required": "必须包含告警发生时间字段"}
    )

    create_time = serializers.CharField(
        help_text="告警信息入库时间",
        required=True, max_length=1024,
        error_messages={"required": "必须包含告警信息入库时间字段"}
    )

    monitor_path = serializers.CharField(
        help_text="跳转监控路径",
        required=True, max_length=1024,
        error_messages={"required": "必须包含跳转监控路径字段"}
    )

    monitor_log = serializers.CharField(
        help_text="跳转监控日志路径",
        required=True, max_length=1024,
        error_messages={"required": "必须包含跳转监控日志路径字段"}
    )

    fingerprint = serializers.CharField(
        help_text="告警的唯一标识",
        required=True, max_length=1024,
        error_messages={"required": "必须包含告警的唯一标识字段"}
    )

    env = serializers.CharField(
        help_text="环境",
        required=True, max_length=1024,
        error_messages={"required": "必须包含告环境字段"}
    )

    class Meta:
        model = Alert
        fields = "__all__"


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
        """ 校验env_name是否存在 """
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
    origin_alert = serializers.CharField(
        help_text="alertmanager 原生告警",
        required=True,
        error_messages={"required": "不可为空"},
    )

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        alerts = validated_data.get('origin_alert').get('alerts')
        alert_obj_list = []
        for ele in alerts:
            alert_analysis = AlertAnalysis(ele)
            alert_info = alert_analysis()
            if not alert_info:
                continue
            alert = Alert(
                is_read=0,
                alert_type=alert_info.get('alert_type'),
                alert_host_ip=alert_info.get('alert_host_ip'),
                alert_host_instance_name=alert_info.get(
                    'alert_host_instance_name'),
                alert_service_name=alert_info.get('alert_service_name'),
                alert_service_instance_name='',  # TODO 暂时拿不到值
                alert_service_type='',  # TODO 暂时拿不到值
                alert_level=alert_info.get('alert_level'),
                alert_describe=alert_info.get('alert_describe'),
                alert_receiver=alert_info.get('alert_receiver'),
                alert_resolve='',  # TODO 待后续
                alert_time=alert_info.get('alert_time'),
                create_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                monitor_path=alert_info.get('monitor'),
                monitor_log=alert_info.get('monitor_log'),
                fingerprint=alert_info.get('fingerprint'),
                # env='default'  # TODO 此版本默认不赋值
            )
            alert_obj_list.append(alert)
        Alert.objects.bulk_create(alert_obj_list)
        return validated_data


class MonitorAgentRestartSerializer(HostIdsSerializer):
    """ 监控Agent重启序列化类 """

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        """ 主机Agent重启 """
        for item in validated_data.get("host_ids", []):
            monitor_agent_restart.delay(item)
        # 下发任务后批量更新重启主机状态
        Host.objects.filter(
            id__in=validated_data.get("host_ids", [])
        ).update(monitor_agent=1)
        return validated_data
