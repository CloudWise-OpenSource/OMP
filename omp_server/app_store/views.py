"""
应用商店相关视图
"""
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.response import Response

from django_filters.rest_framework.backends import DjangoFilterBackend
from app_store.app_store_serializers import UploadPackageSerializer

from db_models.models import (
    Labels, ApplicationHub, ProductHub, UploadPackageHistory
)
from utils.common.paginations import PageNumberPager
from app_store.app_store_filters import (
    LabelFilter, ComponentFilter, ServiceFilter
)
from app_store.app_store_serializers import (
    ComponentListSerializer, ServiceListSerializer
)


class AppStoreListView(GenericViewSet, ListModelMixin):
    """ 应用商店 list 视图类 """

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        name_field = kwargs.get("name_field")
        # 根据名称进行去重
        result_ls, name_set = [], set()
        for obj in queryset:
            name = getattr(obj, name_field)
            if name not in name_set:
                name_set.add(name)
                result_ls.append(obj)

        serializer = self.get_serializer(
            self.paginate_queryset(result_ls), many=True)

        return self.get_paginated_response(serializer.data)


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
    get_description = "查询所有标签列表"

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return Response(list(queryset))


class ComponentListView(AppStoreListView):
    """
        list:
        查询所有基础组件列表
    """
    queryset = ApplicationHub.objects.filter(
        app_type=ApplicationHub.APP_TYPE_COMPONENT,
        is_release=True,
    ).order_by("-created")
    serializer_class = ComponentListSerializer
    pagination_class = PageNumberPager
    # 过滤，排序字段
    filter_backends = (DjangoFilterBackend,)
    filter_class = ComponentFilter
    # 操作信息描述
    get_description = "查询所有基础组件列表"

    def list(self, request, *args, **kwargs):
        return super(ComponentListView, self).list(
            request, name_field="app_name", *args, **kwargs)


class ServiceListView(AppStoreListView):
    """
        list:
        查询所有应用服务列表
    """
    queryset = ProductHub.objects.filter(
        is_release=True).order_by("-created")
    serializer_class = ServiceListSerializer
    pagination_class = PageNumberPager
    # 过滤，排序字段
    filter_backends = (DjangoFilterBackend,)
    filter_class = ServiceFilter
    # 操作信息描述
    get_description = "查询所有应用服务列表"

    def list(self, request, *args, **kwargs):
        return super(ServiceListView, self).list(
            request, name_field="pro_name", *args, **kwargs)


class UploadPackageView(GenericViewSet, CreateModelMixin):
    """
    create:
    上传安装包
    """
    queryset = UploadPackageHistory.objects.all()
    serializer_class = UploadPackageSerializer

    # 操作信息描述
    post_description = "上传安装包"
