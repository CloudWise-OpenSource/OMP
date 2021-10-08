# Create your views here.
from promemonitor.promemonitor_serializers import MonitorUrlSerializer, AlertSerializer, MaintainSerializer
from db_models.models import MonitorUrl, Alert, Maintain

from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (ListModelMixin, CreateModelMixin)


# class MonitorUrlViewSet(ListModelMixin,CreateModelMixin,UpdateModelMixin,GenericViewSet):
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
            if isinstance(self.request.data, list):
                return serializer_class(many=True, *args, **kwargs)
            return serializer_class(*args, **kwargs)
        else:
            return serializer_class(*args, **kwargs)

    @action(methods=['patch'], detail=False)
    def multiple_update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instances = []
        for item in request.data:
            instance = get_object_or_404(MonitorUrl, id=int(item['id']))
            serializer = super().get_serializer(instance, data=item, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            instances.append(serializer.data)
        return Response(instances)


class AlertViewSet(ListModelMixin, CreateModelMixin, GenericViewSet):
    """
    告警记录视图类
    """
    serializer_class = AlertSerializer
    queryset = Alert.objects.all()

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        if self.request:
            if isinstance(self.request.data, list):
                return serializer_class(many=True, *args, **kwargs)
            return serializer_class(*args, **kwargs)
        else:
            return serializer_class(*args, **kwargs)

    @action(methods=['patch'], detail=False)
    def multiple_update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instances = []
        for item in request.data:
            instance = get_object_or_404(MonitorUrl, id=int(item['id']))
            serializer = super().get_serializer(instance, data=item, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            instances.append(serializer.data)
        return Response(instances)


class MaintainViewSet(GenericViewSet, CreateModelMixin):
    """
    create:
    全局进入 / 退出维护模式
    """
    queryset = Maintain.objects.all()
    serializer_class = MaintainSerializer
    # 操作信息描述
    post_description = "更新全局维护状态"
