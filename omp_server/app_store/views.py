"""
应用商店相关视图
"""
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.response import Response

from django_filters.rest_framework.backends import DjangoFilterBackend

from db_models.models import Labels, UploadPackageHistory
from app_store.app_store_filters import LabelFilter
from app_store.app_store_serializers import UploadPackageSerializer


class LabelListView(GenericViewSet, ListModelMixin):
    """
        list:
        查询所有标签列表
    """
    queryset = Labels.objects.all().values_list(
        "label_name", flat=True)
    # 过滤，排序字段
    filter_backends = (DjangoFilterBackend,)
    filter_class = LabelFilter
    # 操作信息描述
    get_description = "查询所有标签"

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return Response(list(queryset))


class ComponentListView(GenericViewSet, ListModelMixin):
    """
        list:
        查询所有组件列表
    """
    pass


class ServiceListView(GenericViewSet, ListModelMixin):
    """
        list:
        查询所有服务
    """
    pass


class UploadPackageView(GenericViewSet, CreateModelMixin):
    """
    create
    上传安装包
    """
    queryset = UploadPackageHistory.objects.all()
    serializer_class = UploadPackageSerializer

    # 操作信息描述
    post_description = "上传安装包"
