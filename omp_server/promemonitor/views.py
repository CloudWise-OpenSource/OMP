# Create your views here.
"""
监控相关视图
"""
import logging
import json

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    ListModelMixin, CreateModelMixin
)

from utils.common.paginations import PageNumberPager

from db_models.models import (
    Host, MonitorUrl,
    Alert, Maintain
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
        asc = params.pop('asc', False)
        asc = True if asc == '0' else False
        ordering = params.pop('ordering', 'date')
        current = grafana_url.explain_prometheus(params)
        if not current:
            raise OperateError("prometheus获取数据失败，请检查prometheus状态")
        prometheus_info = sorted(
            current, key=lambda e: e.__getitem__(ordering), reverse=asc)
        #prometheus_json = json.dumps(prometheus_info, ensure_ascii=False)
        return Response(prometheus_info)


class ListAlertViewSet(ListModelMixin, GenericViewSet):
    """
    获取告警记录列表视图类
    """
    serializer_class = ListAlertSerializer
    queryset = Alert.objects.all().order_by('id')
    # 分页，过滤，排序
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
        matcher_name='env_name', matcher_value='default')
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
