# Create your views here.
"""
监控相关视图
"""
import json
import logging

import requests
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    ListModelMixin, CreateModelMixin
)

from promemonitor.alert_util import utc_to_local, get_monitor_url, get_log_url
from utils.common.paginations import PageNumberPager

from db_models.models import (
    Host, MonitorUrl,
    Alert, Maintain, ApplicationHub, Service
)

from promemonitor import grafana_url
from promemonitor.promemonitor_filters import AlertFilter, MyTimeFilter
from promemonitor.promemonitor_serializers import (
    MonitorUrlSerializer, ListAlertSerializer, UpdateAlertSerializer,
    MaintainSerializer, MonitorAgentRestartSerializer,
    ReceiveAlertSerializer
)
from utils.common.exceptions import OperateError

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
            serializer = super().get_serializer(instance, data=item, partial=partial)
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
        try:
            prometheus_alerts_url = f"http://{prometheus_url}/api/v1/alerts"  # NOQA
            response = requests.get(prometheus_alerts_url, headers={}, data="")
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
        ignore_status_list = [Service.SERVICE_STATUS_NORMAL, Service.SERVICE_STATUS_STARTING,
                              Service.SERVICE_STATUS_STOPPING, Service.SERVICE_STATUS_RESTARTING,
                              Service.SERVICE_STATUS_STOP]
        database_list = Service.objects.filter(service__app_type=ApplicationHub.APP_TYPE_COMPONENT).filter(
            service__app_labels__label_name__contains="数据库").filter(service_status__in=ignore_status_list)
        service_list = Service.objects.filter(
            service__app_type=ApplicationHub.APP_TYPE_SERVICE).filter(service_status__in=ignore_status_list)
        component_list = Service.objects.filter(
            service__app_type=ApplicationHub.APP_TYPE_COMPONENT).filter(service_status__in=ignore_status_list)
        # third_info_all = None  # TODO 暂为空

        host_info_all_count = len(host_list)
        database_info_all_count = len(database_list)
        service_info_all_count = len(service_list)
        component_info_all_count = len(component_list)
        third_info_all_count = 0  # TODO 暂为空

        host_info_exc_count = 0
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
                if ele.get("status") == "resolved" or ele.get("state") == "resolved":
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
                if list(filter(lambda x: x.app_name == service_name_str, list(database_list))):
                    database_info_exc_count = database_info_exc_count + 1
                    database_info_list.append(ele_dict)
                    error_instance_list.append(
                        ele.get("labels").get("instance_name"))
                elif list(filter(lambda x: x.app_name == service_name_str, list(service_list))):
                    service_info_exc_count = service_info_exc_count + 1
                    service_info_list.append(ele_dict)
                    error_instance_list.append(
                        ele.get("labels").get("instance_name"))
                elif list(filter(lambda x: x.app_name == service_name_str, list(component_list))):
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
                    if hil.get("ip") == h.get("ip") and hil.get("alertname") == h.get("alertname") and h.get(
                            "severity") == "critical":
                        host_info_list.pop(index)
                        break
            elif hil.get("severity") == "critical":
                for i, h in enumerate(host_info_list):
                    if index == i:
                        continue
                    if hil.get("ip") == h.get("ip") and hil.get("alertname") == h.get("alertname") and h.get(
                            "severity") == "warning":
                        host_info_list.pop(i)
                        break

        for host in host_list:
            if host.ip in error_host_list:
                continue
            host_dict = {
                "ip": host.ip, "instance_name": host.instance_name, "severity": "normal"}
            host_info_list.append(host_dict)
        for database in database_list:
            if database.service_instance_name in error_instance_list:
                continue
            database_dict = {"ip": database.ip, "instance_name": database.service_instance_name,
                             "app_name": database.service.app_name, "severity": "normal"}
            database_info_list.append(database_dict)
        for service in service_list:
            if service.service_instance_name in error_instance_list:
                continue
            service_dict = {"ip": service.ip, "instance_name": service.service_instance_name,
                            "app_name": service.service.app_name, "severity": "normal"}
            service_info_list.append(service_dict)
        for component in component_list:
            if component.service_instance_name in error_instance_list:
                continue
            component_dict = {"ip": component.ip, "instance_name": component.service_instance_name,
                              "app_name": component.service.app_name, "severity": "normal"}
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
