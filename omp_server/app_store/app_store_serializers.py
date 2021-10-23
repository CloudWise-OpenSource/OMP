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
    Service
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
        with open(os.path.join(destination_dir, request_file.name), 'wb+') as f:
            for chunk in request_file.chunks():
                try:
                    f.write(chunk)
                except Exception:
                    raise OperateError("文件写入过程失败")

        front_end_verified_init(uuid, operation_user, package_name, md5)
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
                  "created", "pro_dependence", "pro_services", "pro_instances_info",
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


def get_app_dependence(obj):  # NOQA
    """
    解析获取依赖信息
    :param obj: 数据库实例化对象
    :type obj: db_models.models.ApplicationHub
    :return:
    """
    if not obj.app_dependence:
        return []
    dependence_resolve_lst = list()

    def _get_dependence(inner_ret_lst, app_dependence):
        """
        获取内部基础依赖关系方法
        :param inner_ret_lst: 依赖关系结果列表
        :param app_dependence: 应用的依赖项
        :return:
        """
        for inner_item in app_dependence:
            # 定义服务&版本唯一标准，防止递归错误
            unique_key = \
                inner_item.get("name", "") + inner_item.get("version")
            # 排除服务自身依赖，避免因环形依赖而导致的服务自己依赖自己的问题
            self_unique_key = obj.app_name + obj.app_version
            if unique_key in dependence_resolve_lst or \
                    self_unique_key in dependence_resolve_lst or \
                    self_unique_key == unique_key:
                continue
            # 被依赖服务获取到的主机实例信息
            # TODO 解决单实例与集群之间的关系问题
            dependence_app_instance_info = Service.objects.filter(
                service__app_name=inner_item.get("name"),
                service__app_version=inner_item.get("version")
            ).values("ip", "service_instance_name")
            inner_item["dependence_app_instance_ips"] = list(
                dependence_app_instance_info)

            # 判断当前应用商店内是否具备此依赖服务，是否可进行安装
            if ApplicationHub.objects.filter(
                    app_name=inner_item.get("name"),
                    app_version=inner_item.get("version"),
                    is_release=True
            ).exists():
                inner_item["can_install"] = True
            else:
                inner_item["can_install"] = False
            # 判断整体安装流程是否能够继续进行
            # 判断依据如下：
            #   如果没有已经安装的实例，并且应用商店内未发布过该服务，则不可安装
            # TODO 服务间具备强依赖关系时需要考虑到其中的安装逻辑
            if not inner_item["dependence_app_instance_ips"] and \
                    not inner_item["can_install"]:
                inner_item["process_continue"] = False
            else:
                inner_item["process_continue"] = True

            inner_ret_lst.append(inner_item)
            dependence_resolve_lst.append(unique_key)
            # 判断 inner_item 服务是否有依赖信息
            _app = ApplicationHub.objects.filter(
                app_name=inner_item.get("name"),
                app_version=inner_item.get("version"),
                is_release=True
            ).order_by("created").last()
            if not _app or not _app.app_dependence:
                continue
            _app_dependence = json.loads(_app.app_dependence)
            _get_dependence(
                inner_ret_lst, app_dependence=_app_dependence
            )

    ret_lst = list()
    # 解决依赖关系
    _get_dependence(
        inner_ret_lst=ret_lst,
        app_dependence=json.loads(obj.app_dependence)
    )
    return ret_lst


class ComponentEntranceSerializer(serializers.ModelSerializer):
    """ 组件安装入口数据序列化 """

    app_dependence = serializers.SerializerMethodField()
    app_install_args = serializers.SerializerMethodField()
    deploy_mode = serializers.SerializerMethodField()

    def get_app_dependence(self, obj):  # NOQA
        """ 获取服务级别的数据依赖关系
        [
          {
            "name": "t_app_1",
            "version": "1.0",
            "dependence_app_instance_ips": [],
            "can_install": false,
            "process_continue": false
          },
          {
            "name": "t_app_2",
            "version": "2.0",
            "dependence_app_instance_ips": [],
            "can_install": false,
            "process_continue": false
          }
        ]
        """
        return get_app_dependence(obj)

    def get_app_install_args(self, obj):  # NOQA
        """ 解析安装参数信息
        [
          {
            "default": 18080,
            "key": "http_port",
            "name": "服务端口"
          }
        ]
        """
        ret_lst = list()
        # 标记安装过程中涉及到的数据目录，通过此标记给前端
        # 给与前端提示信息，此标记对应于主机中的数据目录 data_folder
        # 在后续前端提供出安装参数后，我们应该检查其准确性
        DIR_KEY = "{data_path}"
        # 拼接服务端口配置信息
        if obj.app_port:
            ret_lst.extend(json.loads(obj.app_port))
        if obj.app_install_args:
            ret_lst.extend(json.loads(obj.app_install_args))
        for item in ret_lst:
            if isinstance(item.get("default"), str) and \
                    DIR_KEY in item.get("default"):
                item["default"] = item["default"].replace(DIR_KEY, "")
                item["dir_key"] = DIR_KEY
        return ret_lst

    def get_deploy_mode(self, obj):     # NOQA
        """ 解析部署模式信息
        [
          {
            "key": "single",
            "name": "单实例"
          }
        ]
        """
        # 如果服务未配置部署模式相关信息，那么默认为单实例模式
        if not obj.extend_fields or not obj.extend_fields.get("deploy", {}):
            return [{"key": "single", "name": "单实例"}]
        deploy_info = obj.extend_fields.get("deploy", {})
        ret_lst = list()
        if "single" in deploy_info:
            ret_lst.extend(deploy_info["single"])
        if "complex" in deploy_info:
            ret_lst.extend(deploy_info["complex"])
        return ret_lst

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

    def get_pro_services(self, obj):    # NOQA
        """ 获取服务列表 """
        if not obj.pro_services:
            return list()
        return json.loads(obj.pro_services)

    def get_pro_dependence(self, obj):  # NOQA
        """ 获取产品依赖关系 """
        # TODO 解决产品间的依赖关系问题
        if not obj.pro_dependence:
            return list()
        return json.loads(obj.pro_dependence)

    def get_dependence_services_info(self, obj):    # NOQA
        """ 获取服务所依赖的信息 """
        _service_lst = self.get_pro_services(obj=obj)
        if not _service_lst:
            return []
        _all_dependence_ser_info = list()
        for item in _service_lst:
            _ser_obj_lst = ApplicationHub.objects.filter(
                app_name=item.get("name"),
                app_version=item.get("version"),
                is_release=1
            )
            for el in _ser_obj_lst:
                _el_lst = get_app_dependence(obj=el)
                _all_dependence_ser_info.extend(_el_lst)
        unique_key_lst = list()
        real_dependence_lst = list()
        for each in _all_dependence_ser_info:
            unique_key = each.get("name") + each.get("version")
            if unique_key in unique_key_lst:
                continue
            real_dependence_lst.append(each)
            unique_key_lst.append(unique_key)
        return real_dependence_lst

    class Meta:
        """ 元数据 """
        model = ProductHub
        fields = [
            "pro_name", "pro_version", "pro_dependence",
            "pro_services", "dependence_services_info"
        ]
