# Create your views here.
"""
监控相关视图
"""
from utils.pagination import PageNumberPager
import logging

from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (ListModelMixin, CreateModelMixin)
from promemonitor import grafana_url
import json
from db_models.models import (
    Host, MonitorUrl,
    Alert, Maintain
)
from promemonitor.promemonitor_serializers import (
    MonitorUrlSerializer, AlertSerializer,
    MaintainSerializer, MonitorAgentRestartSerializer,
    ReceiveAlertSerializer
)

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
        prometheus_info = sorted(
            current, key=lambda e: e.__getitem__(ordering), reverse=asc)
        prometheus_json = json.dumps(prometheus_info, ensure_ascii=False)
        return Response(prometheus_json)


class AlertViewSet(ListModelMixin, CreateModelMixin, GenericViewSet):
    """
    告警记录视图类
    """
    serializer_class = AlertSerializer
    queryset = Alert.objects.all()
    pagination_class = PageNumberPager

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        if self.request:
            if isinstance(self.request.data.get('data'), list):
                return serializer_class(many=True, *args, **kwargs)
            return serializer_class(*args, **kwargs)
        else:
            return serializer_class(*args, **kwargs)

    @action(methods=['patch'], detail=False)
    def multiple_update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instances = []
        for item in request.data.get('data'):
            instance = get_object_or_404(Alert, id=int(item['id']))
            serializer = super().get_serializer(instance, data=item, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            instances.append(serializer.data)
        return Response(instances)


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


class MonitorAgentRestartView(GenericViewSet, CreateModelMixin):
    """
        create:
        主机重启Agent接口
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
        instance_name_list = list()
        host_list = list(Host.objects.all().values_list(
            'instance_name', flat=True))
        print(host_list)
        service_list = []  # TODO 待应用模型完善
        instance_name_list.extend(host_list)
        instance_name_list.extend(service_list)
        return Response(instance_name_list)
