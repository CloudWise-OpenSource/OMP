# Create your views here.
"""
监控相关视图
"""
import json
import logging
import traceback

import requests
from django.core.validators import EmailValidator
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.mixins import (
    ListModelMixin, CreateModelMixin,DestroyModelMixin,UpdateModelMixin
)
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import GenericViewSet

from db_models.models import (
    Host, MonitorUrl,
    Alert, Maintain, ApplicationHub, Service, EmailSMTPSetting,
    AlertSendWaySetting, HostThreshold, ServiceThreshold,
    ServiceCustomThreshold, Rule, AlertRule,Env
)
from omp_server.settings import CUSTOM_THRESHOLD_SERVICES
from promemonitor import grafana_url
from promemonitor.alert_util import utc_to_local, get_monitor_url, get_log_url
from promemonitor.promemonitor_filters import AlertFilter, MyTimeFilter, \
    QuotaFilter
from promemonitor.promemonitor_serializers import (
    MonitorUrlSerializer, ListAlertSerializer, UpdateAlertSerializer,
    MaintainSerializer, MonitorAgentRestartSerializer,
    ReceiveAlertSerializer, RuleSerializer, QuotaSerializer
)
from promemonitor.prometheus import Prometheus
from utils.common.exceptions import OperateError
from utils.common.paginations import PageNumberPager
from utils.parse_config import PROMETHEUS_AUTH
from promemonitor.prometheus_utils import PrometheusUtils

logger = logging.getLogger('server')


class MonitorUrlViewSet(ListModelMixin, CreateModelMixin, GenericViewSet):
    """
        list:
        查询监控地址列表

        create:
        创建一批监控配置

        multiple_update:
        更新一个或多个监控配置一个或多个字段
    """
    serializer_class = MonitorUrlSerializer
    queryset = MonitorUrl.objects.all()
    get_description = "查询监控地址配置"
    patch_description = "修改监控地址配置"

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        if self.request:
            if isinstance(self.request.data.get("data"), list):
                return serializer_class(many=True, *args, **kwargs)
            return serializer_class(*args, **kwargs)
        else:
            return serializer_class(*args, **kwargs)

    @action(methods=['patch'], detail=False)
    def multiple_update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instances = []
        for item in request.data.get('data'):
            instance = get_object_or_404(MonitorUrl, id=int(item['id']))
            serializer = super().get_serializer(instance, data=item,
                                                partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            instances.append(serializer.data)
        return Response(instances)


class GrafanaUrlViewSet(ListModelMixin, GenericViewSet):
    """
        list:
        查询异常清单列表
    """
    queryset = MonitorUrl.objects.all()

    def list(self, request, *args, **kwargs):
        params = request.query_params.dict()
        asc = params.pop('asc', '0')
        asc = True if asc == '0' else False
        ordering = params.pop('ordering', 'date')
        current = grafana_url.explain_prometheus(params)
        if current == "error":
            raise OperateError("prometheus获取数据失败，请检查prometheus状态")
        prometheus_info = sorted(
            current, key=lambda e: e.__getitem__(ordering), reverse=asc)
        # prometheus_json = json.dumps(prometheus_info, ensure_ascii=False)
        return Response(prometheus_info)


class ListAlertViewSet(ListModelMixin, GenericViewSet):
    """
    获取告警记录列表视图类
    """
    serializer_class = ListAlertSerializer
    queryset = Alert.objects.all().order_by("-create_time")  # 分页，过滤，排序
    pagination_class = PageNumberPager
    filter_backends = (
        DjangoFilterBackend,
        OrderingFilter,
        MyTimeFilter,
    )
    filter_class = AlertFilter
    ordering_fields = ("alert_host_ip", "alert_instance_name", "alert_time")


class UpdateAlertViewSet(CreateModelMixin, GenericViewSet):
    """
    更新告警记录视图类
    """
    serializer_class = UpdateAlertSerializer
    queryset = Alert.objects.all().order_by('id')
    post_description = "更新告警记录（已读/未读）"


class MaintainViewSet(GenericViewSet, CreateModelMixin, ListModelMixin):
    """
    create:
    全局进入 / 退出维护模式
    """
    queryset = Maintain.objects.filter(
        matcher_name='env', matcher_value='default')
    serializer_class = MaintainSerializer
    # 操作信息描述
    post_description = "更新全局维护状态"


class ReceiveAlertViewSet(GenericViewSet, CreateModelMixin):
    """
    接收alertmanager发送过来的告警消息后解析入库
    """
    queryset = None
    serializer_class = ReceiveAlertSerializer
    # 操作信息描述
    post_description = "接收alertmanager告警信息"
    # 关闭权限、认证设置
    authentication_classes = ()
    permission_classes = ()


class MonitorAgentRestartView(GenericViewSet, CreateModelMixin):
    """
        create:
        重启监控Agent接口
    """
    queryset = Host.objects.filter(is_deleted=False)
    serializer_class = MonitorAgentRestartSerializer
    # 操作信息描述
    post_description = "重启监控Agent"


class InstanceNameListView(GenericViewSet, ListModelMixin):
    """
    返回主机和服务实例名列表
    """
    # 操作信息描述
    post_description = "返回主机和服务实例名列表"

    def list(self, request, *args, **kwargs):
        alert_instance_name_list = list()
        host_instance_name_list = list(Host.objects.all().values_list(
            'instance_name', flat=True))
        service_instance_name_list = []  # TODO 待应用模型完善
        alert_instance_name_list.append(host_instance_name_list)
        alert_instance_name_list.append(service_instance_name_list)
        return Response(alert_instance_name_list)


class InstrumentPanelView(GenericViewSet, ListModelMixin):
    """
    返回仪表盘所需数据
    """
    # 操作信息描述
    get_description = "查询仪表盘数据"

    @staticmethod
    def get_prometheus_alerts():
        """
        请求prometheus alerts接口返回告警内容
        """
        mu = MonitorUrl.objects.filter(name="prometheus").first()
        prometheus_url = mu.monitor_url if mu else "127.0.0.1:19011"
        prometheus_auth = (PROMETHEUS_AUTH.get(
            "username", "omp"), PROMETHEUS_AUTH.get("plaintext_password", ""))
        try:
            prometheus_alerts_url = f"http://{prometheus_url}/api/v1/alerts"
            # NOQA
            response = requests.get(prometheus_alerts_url, headers={
            }, data="", auth=prometheus_auth)
            return True, json.loads(response.text)
        except Exception as e:
            logger.error("prometheus请求alerts失败：" + str(e))
            return False, "Failed"

    def get_exc_serializer_info(self):
        host_info_dict = {}
        database_info_dict = {}
        service_info_dict = {}
        component_info_dict = {}
        third_info_dict = {}

        host_info_list = []
        database_info_list = []
        service_info_list = []
        component_info_list = []
        third_info_list = []

        host_list = Host.objects.all()
        ignore_status_list = [Service.SERVICE_STATUS_NORMAL,
                              Service.SERVICE_STATUS_STARTING,
                              Service.SERVICE_STATUS_STOPPING,
                              Service.SERVICE_STATUS_RESTARTING,
                              Service.SERVICE_STATUS_STOP]
        database_list = Service.objects.filter(
            service__app_type=ApplicationHub.APP_TYPE_COMPONENT).filter(
            service__app_labels__label_name__contains="数据库").filter(
            service_status__in=ignore_status_list).filter(
            service__is_base_env=False)
        service_list = Service.objects.filter(
            service__app_type=ApplicationHub.APP_TYPE_SERVICE).filter(
            service_status__in=ignore_status_list).filter(
            service__is_base_env=False).filter(
            service_controllers__start__isnull=False)
        component_list = Service.objects.filter(
            service__app_type=ApplicationHub.APP_TYPE_COMPONENT).filter(
            service_status__in=ignore_status_list).filter(
            service__is_base_env=False)
        # third_info_all = None  # TODO 暂为空

        host_info_all_count = len(host_list)
        database_info_all_count = len(database_list)
        service_info_all_count = len(service_list)
        component_info_all_count = len(component_list)
        third_info_all_count = 0  # TODO 暂为空

        # host_info_exc_count = 0
        database_info_exc_count = 0
        service_info_exc_count = 0
        component_info_exc_count = 0
        third_info_exc_count = 0

        host_info_no_monitor_count = 0
        database_info_no_monitor_count = 0
        service_info_no_monitor_count = 0
        component_info_no_monitor_count = 0
        third_info_no_monitor_count = 0

        flag, alert_data = self.get_prometheus_alerts()
        error_instance_list = []
        error_host_list = []
        if flag:
            alerts = alert_data.get('data').get('alerts')
            for ele in alerts:
                if not isinstance(ele, dict):
                    continue
                if ele.get("status") == "resolved" or ele.get(
                        "state") == "resolved":
                    continue
                ele_dict = {
                    "ip": ele.get("labels").get("instance"),
                    "instance_name": ele.get("labels").get("instance_name"),
                    "alertname": ele.get("labels").get("alertname"),
                    "severity": ele.get("labels").get("severity"),
                    "date": utc_to_local(ele.get("activeAt")),
                    "describe": ele.get("annotations").get("description"),
                    "monitor_url": get_monitor_url([{
                        "ip": ele.get("labels").get("instance"),
                        "type": "service",
                        "instance_name": ele.get("labels").get("service_name")
                    }]),
                    "log_url": get_log_url([{
                        "ip": ele.get("labels").get("instance"),
                        "type": "service",
                        "instance_name": ele.get("labels").get("service_name")
                    }])
                }
                if ele.get("labels").get("job") == "nodeExporter":
                    ele_dict["monitor_url"] = get_monitor_url([{
                        "ip": ele.get("labels").get("instance"),
                        "type": "host",
                        "instance_name": "node"
                    }])
                    ele_dict["log_url"] = get_log_url([{
                        "ip": ele.get("labels").get("instance"),
                        "type": "host",
                        "instance_name": "node"
                    }])
                    # host_info_exc_count = host_info_exc_count + 1
                    host_info_list.append(ele_dict)
                    error_host_list.append(ele.get("labels").get("instance"))
                service_name_str = ele.get("labels").get("app")
                if not service_name_str:
                    continue
                if list(filter(
                        lambda x: x.service.app_name == service_name_str,
                        list(database_list))):
                    database_info_exc_count = database_info_exc_count + 1
                    database_info_list.append(ele_dict)
                    error_instance_list.append(
                        ele.get("labels").get("instance_name"))
                elif list(
                        filter(lambda x: x.service.app_name ==
                                         service_name_str,
                               list(service_list))):
                    service_info_exc_count = service_info_exc_count + 1
                    service_info_list.append(ele_dict)
                    error_instance_list.append(
                        ele.get("labels").get("instance_name"))
                elif list(
                        filter(lambda x: x.service.app_name ==
                                         service_name_str,
                               list(component_list))):
                    component_info_exc_count = component_info_exc_count + 1
                    component_info_list.append(ele_dict)
                    error_instance_list.append(
                        ele.get("labels").get("instance_name"))
                else:
                    continue

        for index, hil in enumerate(host_info_list):
            if hil.get("severity") == "warning":
                for i, h in enumerate(host_info_list):
                    if index == i:
                        continue
                    if hil.get("ip") == h.get("ip") and hil.get(
                            "alertname") == h.get("alertname") and h.get(
                        "severity") == "critical":
                        host_info_list.pop(index)
                        break
            elif hil.get("severity") == "critical":
                for i, h in enumerate(host_info_list):
                    if index == i:
                        continue
                    if hil.get("ip") == h.get("ip") and hil.get(
                            "alertname") == h.get("alertname") and h.get(
                        "severity") == "warning":
                        host_info_list.pop(i)
                        break

        _, host_targets = Prometheus().get_all_host_targets()
        for host in host_list:
            if host.ip in error_host_list:
                continue
            host_dict = {
                "ip": host.ip, "instance_name": host.instance_name,
                "severity": "normal"}
            if host.ip not in host_targets:
                host_dict = {
                    "ip": host.ip, "instance_name": host.instance_name,
                    "severity": "unmonitored"}
            host_info_list.append(host_dict)

        _, service_targets = Prometheus().get_all_service_targets()
        for database in database_list:
            if database.service_instance_name in error_instance_list:
                continue
            database_dict = {"ip": database.ip,
                             "instance_name": database.service_instance_name,
                             "app_name": database.service.app_name,
                             "severity": "normal"}
            database_ip_instance_name_str = \
                f"{database.ip}_{database.service_instance_name}"
            if database_ip_instance_name_str not in service_targets:
                database_dict = {"ip": database.ip,
                                 "instance_name":
                                     database.service_instance_name,
                                 "app_name": database.service.app_name,
                                 "severity": "unmonitored"}
            database_info_list.append(database_dict)
        for service in service_list:
            if service.service_instance_name in error_instance_list:
                continue
            service_dict = {"ip": service.ip,
                            "instance_name": service.service_instance_name,
                            "app_name": service.service.app_name,
                            "severity": "normal"}
            service_ip_instance_name_str = f"{service.ip}_" \
                                           f"{service.service_instance_name}"
            if service_ip_instance_name_str not in service_targets:
                service_dict = {"ip": service.ip,
                                "instance_name": service.service_instance_name,
                                "app_name": service.service.app_name,
                                "severity": "unmonitored"}
            service_info_list.append(service_dict)
        for component in component_list:
            if component.service_instance_name in error_instance_list:
                continue
            component_dict = {"ip": component.ip,
                              "instance_name": component.service_instance_name,
                              "app_name": component.service.app_name,
                              "severity": "normal"}
            component_ip_instance_name_str = f"{component.ip}_" \
                                             f"{component.service_instance_name}"
            if component_ip_instance_name_str not in service_targets:
                component_dict = {"ip": component.ip,
                                  "instance_name":
                                      component.service_instance_name,
                                  "app_name": component.service.app_name,
                                  "severity": "unmonitored"}
            component_info_list.append(component_dict)

        host_info_exc_count = len(set(error_host_list))

        host_info_dict.update({
            "host_info_all_count": host_info_all_count,
            "host_info_exc_count": host_info_exc_count,
            "host_info_no_monitor_count": host_info_no_monitor_count,
            "host_info_list": host_info_list
        })
        database_info_dict.update({
            "database_info_all_count": database_info_all_count,
            "database_info_exc_count": database_info_exc_count,
            "database_info_no_monitor_count": database_info_no_monitor_count,
            "database_info_list": database_info_list
        })
        service_info_dict.update({
            "service_info_all_count": service_info_all_count,
            "service_info_exc_count": service_info_exc_count,
            "service_info_no_monitor_count": service_info_no_monitor_count,
            "service_info_list": service_info_list
        })
        component_info_dict.update({
            "component_info_all_count": component_info_all_count,
            "component_info_exc_count": component_info_exc_count,
            "component_info_no_monitor_count": component_info_no_monitor_count,
            "component_info_list": component_info_list
        })
        third_info_dict.update({
            "third_info_all_count": third_info_all_count,
            "third_info_exc_count": third_info_exc_count,
            "third_info_no_monitor_count": third_info_no_monitor_count,
            "third_info_list": third_info_list
        })
        serializer_info = {
            "host": host_info_dict,
            "database": database_info_dict,
            "service": service_info_dict,
            "component": component_info_dict,
            "third": third_info_dict,
        }
        return serializer_info

    def list(self, request, *args, **kwargs):
        result = self.get_exc_serializer_info()
        return Response(result)


class GetSendEmailConfig(GenericViewSet, ListModelMixin):
    """
    获取邮件发送配置
    """
    get_description = "获取邮件发送配置"

    def list(self, request, *args, **kwargs):
        email_setting = EmailSMTPSetting.objects.first()
        if email_setting:
            return Response(data=email_setting.get_dict())
        return Response({})


class UpdateSendEmailConfig(GenericViewSet, CreateModelMixin):
    """
    更新邮件发送配置
    """
    post_description = "更新邮件发送配置"

    serializer_class = Serializer

    def create(self, request, *args, **kwargs):
        email_host = request.data.get("host")
        if not email_host:
            return Response(data={"code": 1, "message": "请填写SMTP邮件服务器地址！"})
        email_port = request.data.get("port")
        if not email_port or not isinstance(email_port, int):
            return Response(
                data={"code": 1, "message": "请检查所填的SMTP邮件服务器端口是否正确！"})
        email_host_user = request.data.get("username")
        if not email_host_user:
            return Response(data={"code": 1, "message": "请填写SMTP邮件服务器发件箱！"})
        try:
            EmailValidator()(email_host_user)
        except Exception as e:
            message = "SMTP邮件服务器发件箱格式错误！"
            logger.error(f"{message} 错误信息：{str(e)}")
            return Response(data={"code": 1, "message": message})
        email_host_password = request.data.get("password")
        if not email_host_password:
            return Response(data={"code": 1, "message": "填写SMTP邮件服务器发件箱格式错误！"})
        try:
            EmailSMTPSetting.objects.all().delete()
            email_setting = EmailSMTPSetting.objects.create(
                email_host=email_host,
                email_port=email_port,
                email_host_user=email_host_user,
                email_host_password=email_host_password
            )
        except Exception as e:
            message = "修改email邮箱服务器信息出错！"
            logger.error(f"{message} 详细信息：{str(e)}")
            return Response(data={"code": 1, "message": message})
        state, email_url = email_setting.update_setting_config()
        if not state:
            return Response(data={"code": 1, "message": "同步到Alert Manage失败！"})
        return Response({})


class GetSendAlertSettingView(GenericViewSet, ListModelMixin):
    """
    获取监控邮箱收件配置
    """
    get_description = "获取监控邮箱收件配置"

    def list(self, request, *args, **kwargs):
        env_id = request.GET.get("env_id", 0)
        filter_kwargs = dict(env_id=env_id)
        way_name = request.GET.get("way_name")
        if way_name:
            filter_kwargs["way_name"] = way_name
        objs = AlertSendWaySetting.objects.filter(**filter_kwargs)
        data = dict()
        for obj in objs:
            data.update({obj.way_name: obj.get_self_dict()})
        if "email" not in data:
            data["email"] = AlertSendWaySetting.get_v1_5_email_dict(env_id)
        return Response(data=data)


class UpdateSendAlertSettingView(GenericViewSet, CreateModelMixin):
    """更新监控邮箱收件配置"""
    post_description = "更新监控邮箱收件配置"

    serializer_class = Serializer

    def create(self, request, *args, **kwargs):
        env_id = request.data.get("env_id")
        alert_setting, _ = AlertSendWaySetting.objects.get_or_create(
            env_id=env_id, way_name="email"
        )
        used = request.data.get("used", False)
        emails = request.data.get("server_url", "")
        if emails:
            for email in emails.split(","):
                try:
                    EmailValidator()(email)
                except Exception as e:
                    message = f"收件箱{email}格式错误！"
                    logger.error(f"{message} 错误信息：{str(e)}")
                    return Response(data={"code": 1, "message": message})
        AlertSendWaySetting.update_email_config(bool(used), emails)
        email_setting = EmailSMTPSetting.objects.first()
        if not email_setting:
            return Response(
                data={"code": 1, "message": "邮箱SMTP服务器未配置，配置后才可发送告警邮件！"})
        state, email_url = email_setting.update_setting_config()
        if not state:
            return Response(data={"code": 1,
                                  "message": "同步到Alert Manage失败！请确保Alert "
                                             "Manage可用"})
        return Response({})


class HostThresholdView(GenericViewSet, ListModelMixin, CreateModelMixin):
    """
    读写主机阈值
    """

    get_description = "读取主机阈值设置"
    post_description = "更新主机阈值设置"

    serializer_class = Serializer

    def list(self, request, *args, **kwargs):
        """
        获取主机监控指标项设置
        """
        env_id = request.GET.get('env_id')
        if not env_id:
            return Response(data={"code": 1, "message": "请确认请求参数中包含env_id"})
        if not HostThreshold.objects.filter(env_id=env_id).exists():
            return Response(data={"code": 1, "message": f"env {env_id}错误"})
        host_thresholds = HostThreshold.objects.filter(
            env_id=env_id,
            index_type__in=["cpu_used", "memory_used", "disk_root_used",
                            "disk_data_used"]
        ).annotate(
            value=F("condition_value"), level=F("alert_level")
        ).order_by("index_type", "level").values(
            "index_type", "condition", "value", "level")
        data = {
            "cpu_used": [],
            "memory_used": [],
            "disk_root_used": [],
            "disk_data_used": []
        }
        for host_threshold in host_thresholds:
            data[host_threshold.get("index_type")].append(host_threshold)
        return Response(data=data)

    def create(self, request, *args, **kwargs):
        """
        更新主机指标项到自监控平台
        """
        try:
            logger.info(f"主机监控指标更新接口获取到的参数为: {request.data}")
            update_data = request.data.get("update_data", {})
            env_id = request.data.get("env_id")
            if not update_data:
                return Response(data={"code": 1, "message": "无法正确解析到要更新的数据!"})
            if env_id is None:
                return Response(
                    data={"code": 1, "message": "请确认请求参数中包含env_id"})
            # 同步阈值至prometheus主机告警规则文件中，并做配置检查
            # if not check_prometheus():
            #     return Response(1, "无法连接到prometheus，更改阈值失败！")
            _obj_lst = list()
            hosts_list = list()
            for key, value in update_data.items():
                for item in value:
                    if not item["condition"] or not item["value"] or not item[
                        "level"]:
                        continue
                    _obj = HostThreshold()
                    _obj.index_type = key
                    _obj.condition = item["condition"]
                    _obj.condition_value = item["value"]
                    _obj.alert_level = item["level"]
                    _obj.env_id = env_id
                    _obj_lst.append(_obj)
                    hosts_list.append({
                        'index_type': key,
                        'condition': item["condition"],
                        'condition_value': item["value"],
                        'alert_level': item["level"]
                    })
            with transaction.atomic():
                HostThreshold.objects.filter(env_id=env_id).delete()
                HostThreshold.objects.bulk_create(_obj_lst)

            from promemonitor.prometheus_utils import PrometheusUtils
            prometheus_util = PrometheusUtils()
            prometheus_util.update_host_threshold(env_id=env_id)
            data_disk_dir_list = list(Host.objects.all().values_list(
                "data_folder", flat=True).distinct())
            for ele in data_disk_dir_list:
                prometheus_util.update_node_data_rule(ele)

            return Response({})
        except Exception as e:
            logger.error(f"更新主机相关阈值过程中出错: {traceback.format_exc()}")
            return Response(
                data={"code": 1, "message": f"更新主机相关阈值过程中出错: {str(e)}!"})


class ServiceThresholdView(GenericViewSet, ListModelMixin, CreateModelMixin):
    """
    读写服务阈值
    """

    get_description = "读取服务阈值设置"
    post_description = "更新服务阈值设置"

    serializer_class = Serializer

    def list(self, request, *args, **kwargs):
        """
        获取服务阈值监控指标项设置
        """
        env_id = request.GET.get('env_id')
        if not env_id:
            return Response(data={"code": 1, "message": "请确认请求参数中包含env_id"})
        if not ServiceThreshold.objects.filter(env_id=env_id).exists():
            return Response(data={"code": 1, "message": f"env {env_id}错误"})
        service_thresholds = ServiceThreshold.objects.filter(
            env_id=env_id,
            index_type__in=["service_active", "service_cpu_used",
                            "service_memory_used"]
        ).annotate(
            value=F("condition_value"), level=F("alert_level")
        ).order_by("index_type", "level").values(
            "index_type", "condition", "value", "level")
        data = {
            "service_active": [],
            "service_cpu_used": [],
            "service_memory_used": [],
        }
        for service_threshold in service_thresholds:
            data[service_threshold.get("index_type")].append(service_threshold)
        return Response(data=data)

    def create(self, request, *args, **kwargs):
        """
        更新服务阈值监控指标项设置
        """
        try:
            logger.info(f"服务监控指标更新接口获取到的参数为: {request.data}")
            update_data = request.data.get("update_data", {})
            env_id = request.data.get("env_id")
            if not update_data:
                return Response(data={"code": 1, "message": "无法正确解析到要更新的数据!"})
            if env_id is None:
                return Response(
                    data={"code": 1, "message": "请确认请求参数中包含env_id"})
            _obj_lst = list()
            services_list = list()
            for key, value in update_data.items():
                for item in value:
                    if not item["condition"] or not item["value"] or not item[
                        "level"]:
                        continue
                    _obj = ServiceThreshold()
                    _obj.index_type = key
                    _obj.condition = item["condition"]
                    _obj.condition_value = item["value"]
                    _obj.alert_level = item["level"]
                    _obj.env_id = env_id
                    _obj_lst.append(_obj)
                    services_list.append({
                        'index_type': key,
                        'condition': item["condition"],
                        'condition_value': item["value"],
                        'alert_level': item["level"]
                    })
            with transaction.atomic():
                ServiceThreshold.objects.filter(env_id=env_id).delete()
                ServiceThreshold.objects.bulk_create(_obj_lst)
            return Response({})
        except Exception as e:
            logger.error(f"更新服务相关阈值过程中出错: {traceback.format_exc()}")
            return Response(
                data={"code": 1, "message": f"更新服务相关阈值过程中出错: {str(e)}!"})


class CustomThresholdView(GenericViewSet, ListModelMixin, CreateModelMixin):
    """
    读写自定义服务指标阈值
    """

    get_description = "读取自定义服务指标阈值设置"
    post_description = "更新自定义服务指标阈值设置"

    serializer_class = Serializer

    def list(self, request, *args, **kwargs):
        """
        暂时只有kafka_consumergroup_lag
        """
        env_id = request.GET.get('env_id')
        if not env_id:
            return Response(data={"code": 1, "message": "请确认请求参数中包含env_id"})
        service_thresholds = list(
            ServiceCustomThreshold.objects.filter(
                env_id=env_id
            ).annotate(
                value=F("condition_value"), level=F("alert_level")
            ).order_by("service_name", "index_type", "level").values(
                "service_name", "index_type", "condition", "value", "level")
        )
        data = dict()
        for service_threshold in service_thresholds:
            service_name = service_threshold.get("service_name", "")
            index_type = service_threshold.get("index_type", "")
            if not service_name or not index_type:
                continue
            index_type_info = {
                "condition": service_threshold.get("condition"),
                "index_type": index_type,
                "level": service_threshold.get("level"),
                "value": service_threshold.get("value")
            }
            threshold_info = data.get(service_name, {})
            if not threshold_info:
                data[service_name] = {index_type: [index_type_info]}
            else:
                index_type_infos = threshold_info.get(index_type)
                if not index_type_infos:
                    threshold_info[index_type] = [index_type_info]
                else:
                    threshold_info[index_type].append(index_type_info)
        return Response(data=data)

    def valid_kafka_kafka_consumergroup_lag(self, value):  # NOQA
        if isinstance(value, int):
            return value > 0
        return value.isdigit() and int(value) > 0

    def create(self, request, *args, **kwargs):
        """
        更新服务阈值监控指标项设置
        """
        try:
            logger.info(f"自定义服务监控指标更新接口获取到的参数为: {request.data}")
            service_name = request.data.get("service_name", "")
            index_types = CUSTOM_THRESHOLD_SERVICES.get(service_name)
            if not index_types:
                return Response(data={"code": 1, "message": "暂不支持该服务定制化阈值!"})
            index_type = request.data.get("index_type", "")
            if not index_type or index_type not in index_types:
                return Response(data={"code": 1, "message": "暂不支持该指标项!"})
            index_type_info = request.data.get("index_type_info", [])
            if not index_type_info:
                return Response(data={"code": 1, "message": "无法正确解析到要更新的数据!"})
            env_id = request.data.get("env_id")
            if not ServiceCustomThreshold.objects.filter(
                    env_id=env_id).exists():
                return Response(
                    data={"code": 1, "message": f"env {env_id}不存在"})
            # 后续需要增加对环境是否存在的判断

            # 后续可能需要同步阈值至prometheus的rules文件中
            # if not check_prometheus():
            #     return Response(1, "无法连接到prometheus，更改阈值失败！")
            _obj_lst = list()
            # 创建阈值
            for index_type_value in index_type_info:
                condition = index_type_value.get("condition")
                level = index_type_value.get("level")
                value = index_type_value.get("value")
                valid = getattr(
                    self, f"valid_{service_name}_{index_type}"
                )(value)
                if not valid:
                    return Response(
                        data={"code": 1, "message": "阈值更新的值不符合要求！"})
                _obj = ServiceCustomThreshold(
                    env_id=env_id,
                    service_name=service_name,
                    index_type=index_type,
                    condition=condition,
                    condition_value=value,
                    alert_level=level
                )
                _obj_lst.append(_obj)
            with transaction.atomic():
                ServiceCustomThreshold.objects.filter(
                    env_id=env_id,
                    service_name=service_name,
                    index_type=index_type
                ).delete()
                ServiceCustomThreshold.objects.bulk_create(_obj_lst)
            return Response({})
        except Exception as e:
            logger.error(f"更新服务相关阈值过程中出错: {traceback.format_exc()}")
            return Response(
                data={"code": 1, "message": f"更新服务相关阈值过程中出错: {str(e)}!"})


class QuotaView(ListModelMixin, GenericViewSet, CreateModelMixin,DestroyModelMixin):
    """
    读写自定义服务指标阈值
    """

    get_description = "读取指标规则"
    post_description = "更新指标规则"
    delete_description = "删除指标规则"
    serializer_class = QuotaSerializer
    queryset = AlertRule.objects.all().order_by("-create_time")
    pagination_class = PageNumberPager
    filter_backends = (
        DjangoFilterBackend,
        OrderingFilter,
    )
    filter_class = QuotaFilter

    def create(self, request, *args, **kwargs):
        """
        添加监控指标项
        env_id = models.IntegerField("环境id", default=1)
        expr = models.TextField("监控指标表达式，报警语法", null=False, blank=False)
        threshold_value = models.FloatField("阈值的数值", null=False, blank=False)
        compare_str = models.CharField("比较符", max_length=64)
        for_time = models.CharField("持续一段时间获取不到信息就触发告警", max_length=64)
        severity = models.CharField("告警级别", max_length=64)
        alert = models.TextField("标题，自定义摘要")
        service = models.CharField("指标所属服务名称", max_length=255)
        status = models.IntegerField("启用状态", default=0)
        quota_type = models.IntegerField("指标的类型", choices=TYPE, default=0)
        labels = models.JSONField("额外指定标签")
        description = models.TextField("描述, 告警指标描述", null=True)
        create_time = models.DateTimeField("告警规则入库时间", auto_now_add=True)
        update_time = models.DateTimeField("告警规则更新时间", auto_now_add=True)
        """
        p = PrometheusUtils()
        compare_str_dict = {
            ">=": "大于或等于",
            ">": "大于",
            "==": "等于",
            "!=": "不等于",
            "<=": "小于或等于",
            "<": "小于"
        }
        try:
            env_id = request.data.get("env_id")
            if not env_id:
                return Response(
                    data={"code": 1, "message": "请确认请求参数中包含env_id"})
            env_name = Env.objects.filter(id=env_id).first().name
            logger.info(f"创建指标规则接口获取到的参数为: {request.data}")
            quota_type = request.data.get("quota_type")
            compare_str = request.data.get("compare_str")
            severity = request.data.get("severity")
            threshold_value = request.data.get("threshold_value")
            id = request.data.pop("id", 0)
            expr = request.data.get("expr")
            if quota_type == 0:
                """
                内置指标
                """
                builtins_quota = request.data.pop("builtins_quota", None)
                name = builtins_quota.get("name")
                expr = builtins_quota.get("expr")
                description = builtins_quota.get("description")
                cn_compare = compare_str_dict.get(compare_str)
                request.data["service"] = builtins_quota.get("service")
                request.data["description"] = description.replace("$compare_str$", cn_compare).replace(
                    "$threshold_value$", str(threshold_value)).replace("$env$", env_name)
                request.data["expr"] = expr
                severity = request.data.get("severity")
            elif quota_type == 1:
                """
                自定义promsql
                """
                pass
            elif quota_type == 2:
                """
                日志监控
                """
                pass
            else:
                return Response(
                    data={"code": 1, "message": f"创建指标规则过程中出错: 未识别的规则类型"})
            request.data["labels"] = {
                "job":'{}Exporter'.format(request.data["service"]),
                "severity":severity
            }
            if id != 0:
                if AlertRule.objects.filter(expr=expr,
                                            severity=severity).exclude(id=id).exists():
                    return Response(data={"code": 1,
                                          "message": f"更新指标规则过程中出错: "
                                                     f"同一指标规则级别重复添加"})
                if not p.update_rule_file(add_data=request.data,update=True, rule_id=id):
                    return Response(data={"code": 1,
                                          "message": f"更新指标规则错误"})
                AlertRule.objects.filter(id=id).update(**request.data)
                ok = p.reload_prometheus()
                if not ok:
                    return Response(data={"code":1,"message":"prometheus 重载规则失败，请手动重启prometheus进行重载"})
                return Response()
            if AlertRule.objects.filter(expr=expr, severity=severity).exists():
                return Response(data={"code": 1,
                                      "message": f"创建指标规则过程中出错: "
                                                 f"同一指标规则级别重复添加"})
            if not p.update_rule_file(add_data=request.data,add=True):
                return Response(data={"code": 1,
                                      "message": f"创建指标规则错误"})
            AlertRule(**request.data).save()
            ok = p.reload_prometheus()
            if not ok:
                return Response(data={"code": 1,
                                      "message": "prometheus 重载规则失败，请手动重启prometheus进行重载"})
            return Response()
        except Exception as e:
            logger.error(f"创建指标规则过程中出错: {traceback.format_exc()}")
            return Response(
                data={"code": 1, "message": f"创建指标规则过程中出错: {str(e)}!"})

    def delete(self,request, *args, **kwargs):
        """
        删除规则
        """
        id = request.data.get("id")
        p = PrometheusUtils()
        if not p.update_rule_file(delete=True, rule_id=id):
            return Response(data={"code": 1,
                                  "message": f"删除指标规则时，更新配置文件失败"})
        num, _ = AlertRule.objects.filter(id=id).delete()
        if num == 0:
            return Response(data={"code": 1, "message": "删除失败"})
        return Response()

class BuiltinsRuleView(GenericViewSet, ListModelMixin):
    post_description = "获取内置指标列表"
    serializer_class = RuleSerializer
    queryset = Rule.objects.all()

    def list(self, request, *args, **kwargs):
        data = self.get_serializer(self.queryset, many=True).data
        services = set([i.get("service") for i in data])
        r_data = {}
        for service in services:
            r_data[service] = []
            for i in data:
                if service == i.get("service"):
                    r_data[service].append(i)
        return Response(data=r_data)


class PromSqlTestView(GenericViewSet,CreateModelMixin):
    post_description = "测试指标"
    serializer_class = Serializer

    def create(self,request, *args, **kwargs):
        expr = request.data.get("expr")
        ok, res = Prometheus().get_quota_res(quota=expr)
        if ok:
            return Response(data=res)
        return Response(data={"code": 1, "message": res})