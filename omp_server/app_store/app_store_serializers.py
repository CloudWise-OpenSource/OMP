"""
应用商店
"""
import logging
import os
from django.conf import settings

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import Serializer
from utils.common.exceptions import OperateError
from app_store.tasks import front_end_verified

from db_models.models import (
    ApplicationHub, ProductHub, UploadPackageHistory
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

    uuid = serializers.UUIDField(
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
        ma5 = validated_data.get("ma5")
        package_name = request_file.name
        if not request_file:
            raise OperateError("上传文件为空")
        destination_dir = os.path.join(
            settings.PROJECT_DIR, 'package_hub/front_end_verified')
        with open(os.path.join(destination_dir, request_file.name), 'wb+') as f:
            for chunk in request_file.chunks():
                try:
                    f.write(chunk)
                except Exception:
                    raise OperateError("文件写入过程失败")

        front_end_verified.delay(uuid, operation_user, package_name, ma5)
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


class ApplicationDetailSerializer(ModelSerializer):
    """ 组件详情序列化器 """
    versions = serializers.SerializerMethodField()

    class Meta:
        """ 元数据 """
        model = ApplicationHub
        fields = ("app_name", "versions",)

    def get_versions(self, obj):  # NOQA
        """ 获取组件版本数据 """
        application_queryset = ApplicationHub.objects.filter(
            app_name=obj.app_name)
        application_list = list()
        for item in application_queryset:
            application_list.append({
                "app_name": item.app_name,
                "app_version": item.app_version,
                "app_logo": item.app_logo,
                "app_description": item.app_description,
                "app_labels": list(item.app_labels.all().values_list('label_name', flat=True)),
                "created": item.created,
                "app_package_md5": item.app_package.package_md5,
                "app_operation_user": item.app_package.operation_user,
                "app_dependence": item.app_dependence,
                "app_instances_info": {}  # TODO 暂为空
            })
        return application_list


class ProductDetailSerializer(ModelSerializer):
    """ 产品详情序列化器 """
    versions = serializers.SerializerMethodField()

    class Meta:
        """ 元数据 """
        model = ProductHub
        fields = ("pro_name", "versions")

    def get_versions(self, obj):  # NOQA
        """ 获取组件版本数据 """
        product_queryset = ProductHub.objects.filter(pro_name=obj.pro_name)
        product_list = list()
        for ele in product_queryset:
            product_list.append({
                "pro_name": ele.pro_name,
                "pro_version": ele.pro_version,
                "pro_logo": ele.pro_logo,
                "pro_description": ele.pro_description,
                "pro_labels": list(ele.pro_labels.all().values_list('label_name', flat=True)),
                "created": ele.created,
                "pro_package_md5": ele.pro_package.package_md5,
                "pro_operation_user": ele.pro_package.operation_user,
                "pro_dependence": ele.pro_dependence,
                "pro_services": ele.pro_services,
                "pro_instances_info": {}  # TODO 暂无
            })
        return product_list


class app_store_Serializer(serializers.ModelSerializer):
    """ 操作记录序列化类 """

    class Meta:
        """ 元数据 """
        model = UploadPackageHistory
        fields = ["package_name", "package_status", "error_msg", "operation_uuid"]


class ExecuteLocalPackageScanSerializer(Serializer):
    """ 本地安装包扫描执行序列化类 """
    pass
