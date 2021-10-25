"""
应用商店
"""
import json
import logging
import os
from django.conf import settings

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import Serializer
from utils.common.exceptions import OperateError
from app_store.tmp_exec_back_task import front_end_verified_init

from db_models.models import (
    ApplicationHub, ProductHub, UploadPackageHistory,
)

from app_store.install_utils import (
    make_lst_unique, ServiceArgsSerializer,
    SerDependenceParseUtils, ProDependenceParseUtils
)

logger = logging.getLogger("server")


class ComponentListSerializer(ModelSerializer):
    """ 组件列表序列化器 """
    instance_number = serializers.SerializerMethodField()

    class Meta:
        """ 元数据 """
        model = ApplicationHub
        fields = ("app_name", "app_version", "app_logo",
                  "app_description", "instance_number")

    def get_instance_number(self, obj):
        """ 获取组件已安装实例数量 """
        # TODO 计算组件的已安装实例数量
        return 1111


class ServiceListSerializer(ModelSerializer):
    """ 服务列表序列化器 """
    instance_number = serializers.SerializerMethodField()

    class Meta:
        """ 元数据 """
        model = ProductHub
        fields = ("pro_name", "pro_version", "pro_logo",
                  "pro_description", "instance_number")

    def get_instance_number(self, obj):
        """ 获取组件已安装实例数量 """
        # TODO 计算组件的已安装实例数量
        return 1111


class UploadPackageSerializer(Serializer):
    """上传安装包序列化类"""

    uuid = serializers.CharField(
        help_text="上传安装包uuid",
        required=True,
        error_messages={"required": "必须包含[uuid]字段"}
    )
    operation_user = serializers.CharField(
        help_text="操作用户",
        required=True,
        error_messages={"required": "必须包含[operation_user]字段"}
    )
    file = serializers.FileField(
        help_text="上传的文件",
        required=True,
        error_messages={"required": "必须包含[file]字段"}
    )
    md5 = serializers.CharField(help_text="文件包的md5值",
                                required=True,
                                error_messages={"required": "必须包含[md5]字段"}
                                )

    def validate(self, attrs):
        file = attrs.get("file")
        file_name = file.name
        file_size = file.size
        if not file_name.endswith('.tar') and not file_name.endswith('tar.gz'):
            raise ValidationError({
                "file_name": "上传文件名仅支持.tar或.tar.gz"
            })
        # 文件大小超过4G不支持
        if file_size > 4294967296:
            raise ValidationError({
                "file_size": "上传文件大小超过4G"
            })
        return attrs

    def create(self, validated_data):
        uuid = validated_data.get("uuid")
        operation_user = validated_data.get("operation_user")
        request_file = validated_data.get("file")
        md5 = validated_data.get("md5")
        package_name = request_file.name
        if not request_file:
            raise OperateError("上传文件为空")
        destination_dir = os.path.join(
            settings.PROJECT_DIR, 'package_hub/front_end_verified')
        upload_obj = UploadPackageHistory(
            operation_uuid=uuid,
            operation_user=operation_user,
            package_name=package_name,
            package_md5=md5,
            package_path="verified")
        upload_obj.save()
        with open(os.path.join(destination_dir, request_file.name),
                  'wb+') as f:
            for chunk in request_file.chunks():
                try:
                    f.write(chunk)
                except Exception:
                    upload_obj.delete()
                    raise OperateError("文件写入过程失败")

        front_end_verified_init(uuid, operation_user, package_name, upload_obj.id, md5)
        return validated_data


class RemovePackageSerializer(Serializer):
    """ 移除安装包序列化类 """

    uuid = serializers.CharField(
        help_text="上传安装包uuid",
        required=True,
        error_messages={"required": "必须包含[uuid]字段"}
    )

    package_names = serializers.ListField(
        child=serializers.CharField(),
        help_text="安装包名称列表",
        required=True, allow_empty=False,
        error_messages={"required": "必须包含[package_names]字段"}
    )

    def validate(self, attrs):
        """ 校验安装包名称 """
        operation_uuid = attrs.get("uuid")
        package_names = attrs.get("package_names")
        queryset = UploadPackageHistory.objects.filter(
            operation_uuid=operation_uuid,
            package_name__in=package_names,
        )
        if not queryset.exists() or \
                len(queryset) != len(package_names):
            logger.error(f"remove package error: uuid-{operation_uuid},"
                         f"package_names-{package_names}")
            raise ValidationError({"uuid": "该 uuid 未找到有效的操作记录"})
        attrs["queryset"] = queryset
        return attrs

    def create(self, validated_data):
        """ 上传安装包记录表软删除 """
        queryset = validated_data.pop("queryset", None)
        if queryset is not None:
            queryset.update(is_deleted=True)
        return validated_data


class ApplicationDetailSerializer(ModelSerializer):  # NOQA
    """ 组件详情序列化器 """
    app_instances_info = serializers.SerializerMethodField()
    app_labels = serializers.SerializerMethodField()
    app_package_md5 = serializers.SerializerMethodField()
    app_operation_user = serializers.SerializerMethodField()

    class Meta:
        """ 元数据 """
        model = ApplicationHub
        fields = ("app_name", "app_version", "app_logo", "app_description",
                  "created", "app_dependence", "app_instances_info",
                  "app_labels", "app_package_md5", "app_operation_user")

    def get_app_instances_info(self, obj):  # NOQA
        """ 获取服务安装实例信息 """
        # TODO 获取组件的已安装实例信息
        return {}

    def get_app_labels(self, obj):  # NOQA
        return list(obj.app_labels.all().values_list('label_name', flat=True))

    def get_app_package_md5(self, obj):  # NOQA
        return obj.app_package.package_md5

    def get_app_operation_user(self, obj):  # NOQA
        return obj.app_package.operation_user


class ProductDetailSerializer(ModelSerializer):  # NOQA
    """ 产品详情序列化器 """

    pro_instances_info = serializers.SerializerMethodField()
    pro_labels = serializers.SerializerMethodField()
    pro_package_md5 = serializers.SerializerMethodField()
    pro_operation_user = serializers.SerializerMethodField()

    class Meta:
        """ 元数据 """
        model = ProductHub
        fields = ("pro_name", "pro_version", "pro_logo", "pro_description",
                  "created", "pro_dependence", "pro_services",
                  "pro_instances_info",
                  "pro_labels", "pro_package_md5", "pro_operation_user")

    def get_pro_instances_info(self, obj):  # NOQA
        """ 获取服务安装实例信息 """
        # TODO 获取服务的已安装实例信息
        return {}

    def get_pro_labels(self, obj):  # NOQA
        return list(obj.pro_labels.all().values_list('label_name', flat=True))

    def get_pro_package_md5(self, obj):  # NOQA
        return obj.pro_package.package_md5

    def get_pro_operation_user(self, obj):  # NOQA
        return obj.pro_package.operation_user


class UploadPackageHistorySerializer(serializers.ModelSerializer):
    """ 操作记录序列化类 """

    class Meta:
        """ 元数据 """
        model = UploadPackageHistory
        fields = ["package_name", "package_status",
                  "error_msg", "operation_uuid"]


class PublishPackageHistorySerializer(serializers.ModelSerializer):
    """ 操作记录序列化类 """

    class Meta:
        """ 元数据 """
        model = UploadPackageHistory
        fields = ["package_name", "package_status",
                  "error_msg", "operation_uuid"]


class ExecuteLocalPackageScanSerializer(Serializer):
    """ 本地安装包扫描执行序列化类 """
    pass


class ComponentEntranceSerializer(serializers.ModelSerializer):
    """ 组件安装入口数据序列化 """

    app_dependence = serializers.SerializerMethodField()
    app_install_args = serializers.SerializerMethodField()
    deploy_mode = serializers.SerializerMethodField()

    def get_app_dependence(self, obj):  # NOQA
        """ 解析服务级别的依赖关系 """
        return ServiceArgsSerializer().get_app_dependence(obj)

    def get_app_install_args(self, obj):  # NOQA
        """ 解析服务安装过程中的参数 """
        return ServiceArgsSerializer().get_app_install_args(obj)

    def get_deploy_mode(self, obj):  # NOQA
        """ 解析服务的部署模式 """
        return ServiceArgsSerializer().get_deploy_mode(obj)

    class Meta:
        """ 元数据 """
        model = ApplicationHub
        fields = [
            "app_name", "app_version", "app_dependence",
            "app_install_args", "deploy_mode"
        ]


class ProductEntranceSerializer(serializers.ModelSerializer):
    """ 产品、应用安装序列化类 """

    pro_services = serializers.SerializerMethodField()
    pro_dependence = serializers.SerializerMethodField()
    dependence_services_info = serializers.SerializerMethodField()

    def get_pro_services(self, obj):  # NOQA
        """ 获取服务列表 """
        if not obj.pro_services:
            return list()
        ser_lst = json.loads(obj.pro_services)
        for item in ser_lst:
            ser_obj = ApplicationHub.objects.filter(
                app_name=item.get("name"),
                app_version=item.get("version")
            ).last()
            if not ser_obj:
                item["process_continue"] = False
                item["process_message"] = f"服务{item.get('name')}未发布"
                continue
            item["process_continue"] = True
            item["app_install_args"] = \
                ServiceArgsSerializer().get_app_install_args(ser_obj)
            item["deploy_mode"] = \
                ServiceArgsSerializer().get_deploy_mode(ser_obj)
            item["app_dependence"] = \
                ServiceArgsSerializer().get_app_dependence(ser_obj)
        return ser_lst

    def get_pro_dependence(self, obj):  # NOQA
        """ 获取产品依赖关系 """
        _pro = ProDependenceParseUtils(obj.pro_name, obj.pro_version)
        _dep = _pro.run_pro()
        return _dep

    def get_dependence_services_info(self, obj):  # NOQA
        """ 获取服务所依赖的信息 """
        _service_lst = self.get_pro_services(obj=obj)
        if not _service_lst:
            return []
        _all_dependence_ser_info = list()
        for item in _service_lst:
            _ser = SerDependenceParseUtils(
                item.get("name"), item.get("version"))
            _el_lst = _ser.run_ser()
            _all_dependence_ser_info.extend(_el_lst)
        _all_dependence_ser_info = make_lst_unique(
            _all_dependence_ser_info, "name", "version")
        return _all_dependence_ser_info

    class Meta:
        """ 元数据 """
        model = ProductHub
        fields = [
            "pro_name", "pro_version", "pro_dependence",
            "pro_services", "dependence_services_info"
        ]
