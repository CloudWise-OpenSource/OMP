"""
应用商店相关视图
"""
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    ListModelMixin, CreateModelMixin
)
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from django_filters.rest_framework.backends import DjangoFilterBackend

from db_models.models import (
    Labels, ApplicationHub, ProductHub, UploadPackageHistory
)
from utils.common.paginations import PageNumberPager
from app_store.app_store_filters import (
    LabelFilter, ComponentFilter, ServiceFilter, UploadPackageHistoryFilter
)
from app_store.app_store_serializers import (
    ComponentListSerializer, ServiceListSerializer,
    UploadPackageSerializer, RemovePackageSerializer,
    UploadPackageHistorySerializer, ExecuteLocalPackageScanSerializer
)
from app_store.app_store_serializers import (
    ProductDetailSerializer, ApplicationDetailSerializer
)
from app_store import tmp_exec_back_task

from utils.common.exceptions import OperateError
from app_store.tasks import publish_entry
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


class ComponentDetailView(GenericViewSet, ListModelMixin):
    serializer_class = ApplicationDetailSerializer

    filter_class = ComponentFilter
    filter_backends = (DjangoFilterBackend,)

    # 操作信息描述
    get_description = "查询组件详情"

    def list(self, request, *args, **kwargs):
        arg_app_name = request.GET.get('app_name')

        queryset = ApplicationHub.objects.filter(
            app_name=arg_app_name).order_by("-created")
        serializer = self.get_serializer(queryset, many=True)
        result = dict()
        result.update(
            {
                "app_name": arg_app_name,
                "versions": list(serializer.data)
            }
        )
        return Response(result)


class ServiceDetailView(GenericViewSet, ListModelMixin):
    serializer_class = ProductDetailSerializer

    filter_class = ServiceFilter
    filter_backends = (DjangoFilterBackend,)

    # 操作信息描述
    get_description = "查询产品详情"

    def list(self, request, *args, **kwargs):
        arg_pro_name = request.GET.get('pro_name')

        queryset = ProductHub.objects.filter(
            pro_name=arg_pro_name).order_by("-created")
        serializer = self.get_serializer(queryset, many=True)
        result = dict()
        result.update(
            {
                "pro_name": arg_pro_name,
                "versions": list(serializer.data)
            }
        )
        return Response(result)


class ServicePackPageVerificationView(GenericViewSet, ListModelMixin):
    queryset = UploadPackageHistory.objects.filter(is_deleted=False)
    serializer_class = UploadPackageHistorySerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_class = UploadPackageHistoryFilter


class PublishViewSet(ListModelMixin, CreateModelMixin, GenericViewSet):
    """
        create:
        上传接口
    """

    queryset = UploadPackageHistory.objects.filter(is_deleted=False,
                                                   package_status__in=[3, 4, 5])
    serializer_class = UploadPackageHistorySerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_class = UploadPackageHistoryFilter

    def create(self, request, *args, **kwargs):
        params = request.data
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
            "package_names": _package_name_lst
        }

        return Response(ret_data)


class LocalPackageScanResultView(GenericViewSet, ListModelMixin):
    """
        list:
        扫描服务端执行结果查询接口
        参数:
            uuid: 操作唯一uuid
            package_names: 安装包名称组成的字符串，英文逗号分隔
    """

    @staticmethod
    def get_res_data(operation_uuid, package_names):
        """
        获取安装包扫描状态
        :param operation_uuid: 唯一操作uuid
        :param package_names: 安装包名称组成的字符串
        :return:
        """
        package_names_lst = package_names.split(",")
        # 确定当前安装包状态
        if UploadPackageHistory.objects.filter(
                operation_uuid=operation_uuid,
                package_name__in=package_names_lst,
                package_status=1
        ).count() == len(package_names_lst):
            # 当全部安装包的状态为 1 - 校验失败 时，整个流程结束
            stage_status = "check_all_failed"
        elif UploadPackageHistory.objects.filter(
                operation_uuid=operation_uuid,
                package_name__in=package_names_lst,
                package_status__gt=2
        ).exists():
            # 当有安装包进入到分布流程时，整个流程进入到发布流程
            if UploadPackageHistory.objects.filter(
                    operation_uuid=operation_uuid,
                    package_name__in=package_names_lst,
                    package_status=5
            ).exists():
                # 如果有安装包处于发布中装太，那么整个流程处于发布中状态
                stage_status = "publishing"
            else:
                stage_status = "published"
        else:
            # 校验中
            stage_status = "checking"
        package_info_dic = {
            el: {
                "status": 2, "message": ""
            } for el in package_names_lst
        }
        queryset = UploadPackageHistory.objects.filter(
            operation_uuid=operation_uuid,
            package_name__in=package_names_lst,
        )
        # 发布安装包状态及error信息提取
        for item in queryset:
            package_info_dic[item.package_name]["status"] = item.package_status
            package_info_dic[item.package_name]["message"] = item.error_msg
        if stage_status == "checking":
            message = f"共扫描到 {len(package_names_lst)} 个安装包，正在校验中..."
        elif stage_status == "check_all_failed":
            message = f"共计 {len(package_names_lst)} 个安装包校验失败!"
        elif stage_status == "publishing":
            _count = UploadPackageHistory.objects.filter(
                operation_uuid=operation_uuid,
                package_name__in=package_names_lst,
                package_status__gt=2
            ).count()
            message = f"本次共发布 {_count} 个安装包，正在发布中..."
        elif stage_status == "published":
            _count = UploadPackageHistory.objects.filter(
                operation_uuid=operation_uuid,
                package_name__in=package_names_lst,
                package_status=3
            ).count()
            message = \
                f"本次共发布成功 {_count} 个安装包，" \
                f"发布失败 {len(package_names_lst) - _count} 个安装包!"
        else:
            message = ""
        package_detail_lst = list()
        for item in package_names_lst:
            package_detail_lst.append(package_info_dic[item])
        ret_dic = {
            "uuid": operation_uuid,
            "package_names_lst": package_names_lst,
            "package_detail": package_detail_lst,
            "message": message,
            "stage_status": stage_status
        }
        return ret_dic

    @staticmethod
    def check_request_param(operation_uuid, package_names):
        """
        校验参数
        :param operation_uuid: 唯一uuid
        :param package_names: 安装包名称
        :return:
        """
        if not operation_uuid:
            raise ValidationError({"uuid": "请求参数中必须包含 [uuid] 字段"})
        if not package_names:
            raise ValidationError(
                {"package_names": "请求参数中必须包含 [package_names] 字段"})

    def list(self, request, *args, **kwargs):
        operation_uuid = request.query_params.get("uuid", "")
        package_names = request.query_params.get("package_names", "")
        self.check_request_param(operation_uuid, package_names)
        res = self.get_res_data(operation_uuid, package_names)
        return Response(res)
