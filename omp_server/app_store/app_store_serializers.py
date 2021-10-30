"""
应用商店
"""
import json
import logging
import os
import time
from django.conf import settings

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import Serializer
from utils.common.exceptions import OperateError
from app_store.tmp_exec_back_task import front_end_verified_init

from db_models.models import (
    ApplicationHub, ProductHub, UploadPackageHistory,
    Service, DetailInstallHistory, MainInstallHistory
)

from app_store.install_utils import (
    make_lst_unique, ServiceArgsSerializer,
    SerDependenceParseUtils, ProDependenceParseUtils,
    ValidateExistService, ValidateInstallService,
    CreateInstallPlan
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
        return Service.objects.filter(
            service__app_name=obj.app_name).count()


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
        return Service.objects.filter(
            service__product__pro_name=obj.pro_name).count()


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
    md5 = serializers.CharField(
        help_text="文件包的md5值",
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

        front_end_verified_init(uuid, operation_user,
                                package_name, upload_obj.id, md5)
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
            package_parent__isnull=True,
            is_deleted=False
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
        service_objs = Service.objects.filter(service__app_name=obj.app_name)
        service_list = []
        for so in service_objs:
            service_dict = {
                "instance_name": so.service_instance_name,
                "host_ip": so.ip,
                "service_port": None if not so.service_port else json.loads(so.service_port),
                "app_version": so.service.app_version,
                "mode": "单实例",  # TODO  后续根据cluster字段是否为空来判断是单实例还是集群模式
                "created": so.created
            }
            service_list.append(service_dict)
        return service_list

    def get_app_labels(self, obj):  # NOQA
        return list(obj.app_labels.all().values_list('label_name', flat=True))

    def get_app_package_md5(self, obj):  # NOQA
        md5 = "-"
        if obj.app_package is not None:
            md5 = obj.app_package.package_md5
        return md5

    def get_app_operation_user(self, obj):  # NOQA
        return obj.app_package.operation_user


class ProductDetailSerializer(ModelSerializer):  # NOQA
    """ 产品详情序列化器 """

    pro_instances_info = serializers.SerializerMethodField()
    pro_labels = serializers.SerializerMethodField()
    pro_package_md5 = serializers.SerializerMethodField()
    pro_operation_user = serializers.SerializerMethodField()
    pro_services = serializers.SerializerMethodField()

    class Meta:
        """ 元数据 """
        model = ProductHub
        fields = ("pro_name", "pro_version", "pro_logo", "pro_description",
                  "created", "pro_dependence", "pro_services",
                  "pro_instances_info",
                  "pro_labels", "pro_package_md5", "pro_operation_user")

    def get_pro_instances_info(self, obj):  # NOQA
        """ 获取服务安装实例信息 """
        service_objs = Service.objects.filter(
            service__product__pro_name=obj.pro_name)
        service_list = []
        for so in service_objs:
            service_dict = {
                "instance_name": so.service_instance_name,
                "version": so.service.product.pro_version,
                "app_name": so.service.app_name,
                "app_version": so.service.app_version,
                "host_ip": so.ip,
                "service_port": None if not so.service_port else json.loads(so.service_port),
                "created": so.created
            }
            service_list.append(service_dict)
        return service_list

    def get_pro_labels(self, obj):  # NOQA
        return list(obj.pro_labels.all().values_list('label_name', flat=True))

    def get_pro_package_md5(self, obj):  # NOQA
        md5 = "-"
        if obj.pro_package is not None:
            md5 = obj.pro_package.package_md5
        return md5

    def get_pro_operation_user(self, obj):  # NOQA
        try:
            return obj.pro_package.operation_user
        except Exception as e:
            logger.error(e)
            logger.error("获取服务包user值失败！")

    def get_pro_services(self, obj):  # NOQA
        pro_services_list = []
        apps = ApplicationHub.objects.filter(product_id=obj.id)
        if not apps:
            if not obj.pro_services:
                return pro_services_list
            pro_services_list.extend(json.loads(obj.pro_services))
            return pro_services_list
        pro_app_name_list = []
        for app in apps:
            uph = UploadPackageHistory.objects.get(id=app.app_package_id)
            if not uph:
                continue
            app_dict = {
                "name": app.app_name,
                "version": app.app_version,
                "created": time.strftime("%Y-%m-%d %H:%M:%S", time.strptime(str(app.created), "%Y-%m-%d %H:%M:%S.%f")),
                "md5": uph.package_md5
            }
            pro_services_list.append(app_dict)
            pro_app_name_list.append(app.app_name)
        for ps in json.loads(obj.pro_services):
            if ps.get("name") in pro_app_name_list:
                continue
            pro_services_list.append(ps)
        return pro_services_list


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

    app_port = serializers.SerializerMethodField()
    app_dependence = serializers.SerializerMethodField()
    app_install_args = serializers.SerializerMethodField()
    deploy_mode = serializers.SerializerMethodField()
    process_continue = serializers.SerializerMethodField()
    process_message = serializers.SerializerMethodField()

    def get_app_port(self, obj):  # NOQA
        """ 获取服务端口 """
        return ServiceArgsSerializer().get_app_port(obj)

    def get_app_dependence(self, obj):  # NOQA
        """ 解析服务级别的依赖关系 """
        return ServiceArgsSerializer().get_app_dependence(obj)

    def get_app_install_args(self, obj):  # NOQA
        """ 解析服务安装过程中的参数 """
        return ServiceArgsSerializer().get_app_install_args(obj)

    def get_deploy_mode(self, obj):  # NOQA
        """ 解析服务的部署模式 """
        return ServiceArgsSerializer().get_deploy_mode(obj)

    def get_process_continue(self, obj):  # NOQA
        """ 服务能否安装的接口 """
        return ServiceArgsSerializer().get_process_continue(obj)

    def get_process_message(self, obj):  # NOQA
        return ServiceArgsSerializer().get_process_message(obj)

    class Meta:
        """ 元数据 """
        model = ApplicationHub
        fields = [
            "app_name", "app_version", "app_dependence", "app_port",
            "app_install_args", "deploy_mode", "process_continue",
            "process_message"
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
            item["app_port"] = ServiceArgsSerializer().get_app_port(ser_obj)
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


class ExecuteInstallSerializer(Serializer):
    """
        执行安装时需要解析前端上传的数据的准确性，服务间的关联依赖关系
        目标服务器上实际安装的数据信息等内容
    """

    INSTALL_COMPONENT = 0
    INSTALL_PRODUCT = 1
    INSTALL_TYPE_CHOICES = (
        (INSTALL_COMPONENT, "组件安装"),
        (INSTALL_PRODUCT, "产品安装")
    )
    install_type = serializers.ChoiceField(
        choices=INSTALL_TYPE_CHOICES,
        help_text="选择安装方式: 0-组件; 1-应用",
        required=True, allow_null=False, allow_blank=False,
        error_messages={"required": "必须包含[install_type]字段"}
    )
    use_exist_services = serializers.ListField(
        child=serializers.DictField(),
        help_text="复用已安装的服务列表，eg: [{'name': 'ser1', 'id': 1}]",
        required=True, allow_empty=True,
        error_messages={"required": "必须包含[use_exist_services]字段"}
    )
    install_services = serializers.ListField(
        child=serializers.DictField(),
        help_text="需要安装的服务列表，eg: [{'name': 'ser1', 'version': 1}]",
        required=True, allow_empty=False,
        error_messages={
            "required": "必须包含[install_services]字段",
            "empty": "必须包含将要安装的服务信息"
        }
    )
    is_valid_flag = serializers.BooleanField(
        read_only=True, required=False,
        help_text="数据准确性校验返回标志"
    )
    is_valid_msg = serializers.CharField(
        read_only=True, required=False, max_length=4096,
        help_text="数据准确性校验结果信息"
    )
    operation_uuid = serializers.CharField(
        read_only=True, required=False, max_length=128,
        help_text="成功下发部署计划后返回的uuid"
    )

    def validate_use_exist_services(self, data):  # NOQA
        """
        校验已经存在的服务是否准确
        :param data:
        :return:
        """
        if not data:
            return data
        return ValidateExistService(data=data).run()

    def validate_install_services(self, data):  # NOQA
        """
        校验即将安装的服务及参数
        :param data:
        :return:
        """
        return ValidateInstallService(data=data).run()

    def check_lst_valid(self, lst):  # NOQA
        """
        根据列表、字典格式确定安装参数是否符合要求
        :param lst:
        :return:
        """
        for el in lst:
            if not isinstance(el, dict):
                return False
            if "check_flag" in el and not el["check_flag"]:
                return False
        return True

    def validate(self, attrs):
        """
        安装校验最终要执行的方法，根据安装参数解析结果决定如下操作：
            安装参数解析成功：调用安装参数入库方法
            安装参数解析失败：直接返回相关安装参数
        :param attrs:
        :return:
        """
        valid_lst = list()
        use_exist_services = attrs.get("use_exist_services", [])
        valid_lst.append(self.check_lst_valid(use_exist_services))
        install_services = attrs.get("install_services", [])
        valid_lst.append(self.check_lst_valid(install_services))
        for item in install_services:
            app_install_args = item.get("app_install_args", [])
            valid_lst.append(self.check_lst_valid(app_install_args))
            app_port = item.get("app_port", [])
            valid_lst.append(self.check_lst_valid(app_port))
        logger.info(f"Check install info res: {valid_lst}")
        if len(set(valid_lst)) != 1 or valid_lst[0] is False:
            attrs["is_valid_flag"] = False
            attrs["is_valid_msg"] = "数据校验出错"
            return attrs
        # 数据入库逻辑
        _create_data_obj = CreateInstallPlan(install_data=attrs)
        flag, msg = _create_data_obj.run()
        if not flag:
            attrs["is_valid_flag"] = False
            attrs["is_valid_msg"] = msg
            return attrs
        attrs["is_valid_flag"] = True
        attrs["is_valid_msg"] = ""
        attrs["operation_uuid"] = msg
        return attrs


class InstallHistorySerializer(ModelSerializer):
    """ 安装历史记录序列化类 """
    install_status_msg = serializers.CharField(
        source="get_install_status_display")
    detail_lst = serializers.SerializerMethodField()

    def parse_single_obj(self, obj):    # NOQA
        """
        解析单个服务安装记录信息
        :param obj:
        :type obj: DetailInstallHistory
        :return:
        """
        _status = obj.install_step_status
        # 拼接日志
        _log = ""
        if obj.send_flag != 0 and obj.send_msg:
            _log += obj.send_msg
        if obj.unzip_flag != 0 and obj.unzip_msg:
            _log += obj.unzip_msg
        if obj.install_flag != 0 and obj.install_msg:
            _log += obj.install_msg
        if obj.init_flag != 0 and obj.init_msg:
            _log += obj.init_msg
        if obj.start_flag != 0 and obj.start_msg:
            _log += obj.start_msg
        return {
            "ip": obj.service.ip,
            "status": _status,
            "log": _log,
            "service_name": obj.service.service.app_name,
            "service_instance_name": obj.service.service_instance_name
        }

    def get_detail_lst(self, obj):  # NOQA
        """
        获取安装细节表
        :param obj:
        :return:
        """
        lst = DetailInstallHistory.objects.filter(
            main_install_history=obj
        )
        return [self.parse_single_obj(el) for el in lst]

    class Meta:
        """ 元数据 """
        model = MainInstallHistory
        fields = (
            "operation_uuid", "install_status", "install_status_msg",
            "install_args", "install_log", "detail_lst"
        )


class ServiceInstallHistorySerializer(ModelSerializer):
    """ 安装历史记录序列化类 """
    install_step_status = serializers.SerializerMethodField()
    log = serializers.SerializerMethodField()

    def get_install_step_status(self, obj):
        """
        获取服务安装状态
        :param obj:
        :return:
        """
        detail_obj = DetailInstallHistory.objects.filter(service=obj).last()
        return detail_obj.install_step_status

    def get_log(self, obj):
        """
        获取服务日志信息
        :param obj:
        :return:
        """
        detail_obj = DetailInstallHistory.objects.filter(service=obj).last()
        _log = ""
        if detail_obj.send_flag != 0 and detail_obj.send_msg:
            _log += detail_obj.send_msg
        if detail_obj.unzip_flag != 0 and detail_obj.unzip_msg:
            _log += detail_obj.unzip_msg
        if detail_obj.install_flag != 0 and detail_obj.install_msg:
            _log += detail_obj.install_msg
        if detail_obj.init_flag != 0 and detail_obj.init_msg:
            _log += detail_obj.init_msg
        if detail_obj.start_flag != 0 and detail_obj.start_msg:
            _log += detail_obj.start_msg
        return _log

    class Meta:
        """ 元数据 """
        model = Service
        fields = (
            "install_step_status", "log"
        )
