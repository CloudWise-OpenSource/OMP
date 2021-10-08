from promemonitor.promemonitor_serializers import MonitorUrlSerializer
from db_models.models import MonitorUrl
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    ListModelMixin, CreateModelMixin
)


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
        '''批量添加。校验为单个校验,出现异常直接抛出'''
        partial = kwargs.pop('partial', True)
        instances = []
        for item in request.data.get('data'):
            instance = get_object_or_404(MonitorUrl, id=int(item['id']))
            serializer = super().get_serializer(instance, data=item, partial=partial)
            serializer.is_valid(raise_exception=True)
            instances.append(serializer)
        for i in instances:
            i.save()
        data = [i.data for i in instances]
        return Response(data)
