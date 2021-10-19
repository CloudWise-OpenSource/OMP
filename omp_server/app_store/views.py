"""
应用商店相关视图
"""
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    ListModelMixin, CreateModelMixin, RetrieveModelMixin
)
from rest_framework.response import Response

from django_filters.rest_framework.backends import DjangoFilterBackend

from db_models.models import (
    Labels, ApplicationHub, ProductHub, UploadPackageHistory
)
from utils.common.paginations import PageNumberPager
from app_store.app_store_filters import (
    LabelFilter, ComponentFilter, ServiceFilter
)
from app_store.app_store_serializers import (
    ComponentListSerializer, ServiceListSerializer,
    UploadPackageSerializer, RemovePackageSerializer,
    app_store_Serializer, ExecuteLocalPackageScanSerializer
)
from app_store.app_store_serializers import (
    ProductDetailSerializer, ApplicationDetailSerializer
)
from app_store import tmp_exec_back_task

from utils.common.exceptions import OperateError
from app_store.tasks import publish_entry
from django_filters.rest_framework import FilterSet
import django_filters
from rest_framework.filters import OrderingFilter


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


class RemovePackageView(GenericViewSet, CreateModelMixin):
    """
        post:
        批量移除安装包
    """
    queryset = UploadPackageHistory.objects.all()
    serializer_class = RemovePackageSerializer
    # 操作信息描述
    post_description = "移除安装包"


class ComponentDetailView(GenericViewSet, RetrieveModelMixin):
    queryset = ApplicationHub.objects.all()
    serializer_class = ApplicationDetailSerializer

    # 操作信息描述
    get_description = "查询组件详情"


class ServiceDetailView(GenericViewSet, RetrieveModelMixin):
    queryset = ProductHub.objects.all()
    serializer_class = ProductDetailSerializer

    # 操作信息描述
    get_description = "查询产品详情"


class UploadPackageHistoryFilter(FilterSet):
    """ 发布-安装包校验结果接口 """
    operation_uuid = django_filters.CharFilter(
        help_text="operation_uuid，查询", field_name="operation_uuid", lookup_expr="exact")

    class Meta:
        model = UploadPackageHistory
        fields = ("operation_uuid",)


class ServicePackPageVerificationView(GenericViewSet, ListModelMixin):
    queryset = UploadPackageHistory.objects.all()
    serializer_class = app_store_Serializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_class = UploadPackageHistoryFilter


class PublishViewSet(ListModelMixin, CreateModelMixin, GenericViewSet):
    """
        create:
        上传接口
    """

    queryset = UploadPackageHistory.objects.filter(package_status__in=[3, 4, 5])
    serializer_class = app_store_Serializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_class = UploadPackageHistoryFilter

    def create(self, request, *args, **kwargs):
        params = request.query_params.dict()
        uuid = params.pop('uuid', None)
        if not uuid:
            raise OperateError("请传入uuid")
        publish_entry.delay(uuid)
        return Response({"status": "发布任务下发成功"})

class ExecuteLocalPackageScanView(GenericViewSet, CreateModelMixin):
    """
        post:
        扫描服务端执行按钮
    """
    serializer_class = ExecuteLocalPackageScanSerializer
    # 操作信息描述
    post_description = "扫描本地安装包"

    def create(self, request, *args, **kwargs):
        """
            post:
            扫描服务端执行按钮
        """
        _uuid, _package_name_lst = tmp_exec_back_task.back_end_verified_init(
            operation_user=request.user.username
        )
        ret_data = {
            "uuid": _uuid,
            "package_name_lst": _package_name_lst
        }

        return Response(ret_data)
