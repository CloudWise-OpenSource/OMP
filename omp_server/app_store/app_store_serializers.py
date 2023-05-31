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
from utils.plugin.public_utils import check_is_ip_address, timedelta_strftime
from app_store.tmp_exec_back_task import front_end_verified_init

from db_models.models import (
    ApplicationHub, ProductHub, UploadPackageHistory,
    Service, DetailInstallHistory, MainInstallHistory, Product,
    DeploymentPlan, ExecutionRecord)
from db_models import models

from app_store.install_utils import (
    make_lst_unique, ServiceArgsSerializer,
    SerDependenceParseUtils, ProDependenceParseUtils,
    ValidateExistService, ValidateInstallService,
    CreateInstallPlan
)
from utils.parse_config import HADOOP_ROLE

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
        # return Service.objects.filter(
        #     service__product__pro_name=obj.pro_name).count()
        return Product.objects.filter(product=obj).count()


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
        service_objs = Service.objects.filter(service__id=obj.id)
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
            service__product__id=obj.id)
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

    def parse_single_obj(self, obj):  # NOQA
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


class DeploymentPlanValidateSerializer(Serializer):
    """ 部署计划服务信息验证序列化类 """

    instance_name_ls = serializers.ListField(
        child=serializers.CharField(),
        help_text="主机实例名列表",
        required=True, allow_empty=False,
        error_messages={"required": "必须包含[instance_name_ls]字段"}
    )

    service_data_ls = serializers.ListField(
        child=serializers.DictField(),
        help_text="服务数据列表",
        required=True, allow_empty=False,
        error_messages={"required": "必须包含[host_list]字段"}
    )

    def validate(self, attrs):
        """ 校验主机数据列表 """
        instance_name_ls = attrs.get("instance_name_ls")
        service_data_ls = attrs.get("service_data_ls")
        result_dict = {
            "correct": [],
            "error": []
        }
        logger.info("deployment plan validate start")

        # 查询所有 application 信息
        service_name_ls = list(
            map(lambda x: x.get("service_name"), service_data_ls))
        _queryset = ApplicationHub.objects.filter(
            app_name__in=service_name_ls, is_release=True)
        # 所有 application 默认取最新
        new_app_id_list = []
        for app in _queryset:
            new_version = _queryset.filter(
                app_name=app.app_name
            ).order_by("-created").first().app_version
            if new_version == app.app_version:
                new_app_id_list.append(app.id)
        app_queryset = _queryset.filter(
            id__in=new_app_id_list, is_release=True
        ).select_related("product")

        # 获取 application 对应的 product 信息
        app_now = app_queryset.exclude(product__isnull=True)
        pro_id_list = app_now.values_list("product_id", flat=True).distinct()
        # 验证 product 的依赖项均已包含
        pro_queryset = ProductHub.objects.filter(id__in=pro_id_list)
        for pro in pro_queryset:
            # 无依赖项则跳过
            if not pro.pro_dependence:
                continue
            dependence_list = json.loads(pro.pro_dependence)
            # 校验依赖项的指定版本是否存在
            for dependence in dependence_list:
                name = dependence.get("name")
                # version = dependence.get("version")
                pro_obj = pro_queryset.filter(
                    pro_name=name).order_by("-created").first()
                # if not pro_obj or not pro_obj.pro_version.startswith(version):
                if not pro_obj:
                    result_dict["error"].append({
                        "row": -2,
                        "instance_name": "待补充",
                        "service_name": "待补充",
                        "validate_error": f"产品 {pro.pro_name}-{pro.pro_version} "
                                          f"缺失依赖产品 {name}"
                    })

        # 验证所有 product 下的 application 都已经包含
        app_target_all = ApplicationHub.objects.filter(
            product_id__in=pro_id_list)

        # 考虑到同产品下会有同名服务情况，做去重处理，按照时间版本号取最新
        app_target_id_ls = []
        for pro_id in pro_id_list:
            # 同产品的 app_name 集合
            app_name_set = set()
            app_ls = app_target_all.filter(product_id=pro_id)
            for app in app_ls:
                if app.app_name not in app_name_set:
                    new_version = app_ls.filter(
                        app_name=app.app_name
                    ).order_by("-created").first().app_version
                    if new_version == app.app_version:
                        app_name_set.add(app.app_name)
                        app_target_id_ls.append(app.id)

        # 获取目标 app
        app_target = app_target_all.filter(
            id__in=app_target_id_ls, is_release=True
        )

        # 所有 affinity 为 tengine 字段 (Web 服务)，不参与比较
        now_set = set(filter(
            lambda x: x.extend_fields.get("affinity") != "tengine", app_now))
        target_set = set(filter(
            lambda x: x.extend_fields.get("affinity") != "tengine", app_target))
        diff_set = target_set - now_set

        # 存在遗漏的 application
        if diff_set:
            for app in diff_set:
                result_dict["error"].append({
                    "row": -1,
                    "instance_name": "待补充",
                    "service_name": f"{app.app_name}",
                    "validate_error": f"产品 {app.product.pro_name} "
                                      f"缺失依赖服务 {app.app_name}"
                })

        # 验证所有 application 的依赖项均已包含
        base_env_queryset = ApplicationHub.objects.filter(is_base_env=True)
        for app in app_queryset:
            if not app.app_dependence:
                continue
            dependence_list = json.loads(app.app_dependence)
            # 校验依赖项的指定版本是否存在
            for dependence in dependence_list:
                name = dependence.get("name")
                # version = dependence.get("version")
                app_obj = app_queryset.filter(
                    app_name=name).order_by("-created").first()
                # if not app_obj or not app_obj.app_version.startswith(version):
                if not app_obj:
                    # 如果为 base_env 则跳过
                    # if base_env_queryset.filter(
                    #         app_name=name, app_version=version
                    # ).exists():
                    if base_env_queryset.filter(app_name=name).exists():
                        continue
                    result_dict["error"].append({
                        "row": -2,
                        "instance_name": "待补充",
                        "service_name": f"{name}",
                        "validate_error": f"服务 {app.app_name}-{app.app_version} "
                                          f"缺失依赖服务 {name}"
                    })

        # hadoop 实例列表、角色集合
        hadoop_instance_ls = []
        hadoop_role_set = set()

        for service_data in service_data_ls:
            # 校验主机数据是否已经存在
            if service_data.get("instance_name") not in instance_name_ls:
                service_data["validate_error"] = "主机不在表格中"
                result_dict["error"].append(service_data)
                continue
            # 校验服务是否存在
            app_name = service_data.get("service_name", "unKnow")
            if not app_queryset.filter(
                    app_name=app_name
            ).order_by("-created").exists():
                service_data["validate_error"] = f"{app_name}服务不在应用商店中"
                result_dict["error"].append(service_data)
                continue
            # 如果含 vip 字段，校验是否为 IP 格式
            if service_data.get("vip"):
                is_valid, _ = check_is_ip_address(
                    service_data.get("vip"))
                if not is_valid:
                    service_data["validate_error"] = "虚拟IP不合法"
                    result_dict["error"].append(service_data)
                    continue
            # 如果含 role 字段，校验是否含中文逗号
            if service_data.get("role") and \
                    "，" in service_data.get("role"):
                service_data["validate_error"] = "角色请用英文逗号分隔"
                result_dict["error"].append(service_data)
                continue
            # 当服务名为 hadoop 时，记录 hadoop 实例列表、角色集合
            if app_name == "hadoop":
                hadoop_instance_ls.append(service_data)
                if service_data.get("role"):
                    hadoop_role_set = hadoop_role_set | set(
                        service_data.get("role").split(","))
                continue
            result_dict["correct"].append(service_data)

        # 如果存在 hadoop 实例，则校验角色
        if hadoop_instance_ls:
            key_name = "single"
            if len(hadoop_instance_ls) > 1:
                key_name = "cluster"
            diff = set(HADOOP_ROLE.get(key_name)) - hadoop_role_set
            if diff:
                for hadoop_instance in hadoop_instance_ls:
                    hadoop_instance["validate_error"] = f"缺少角色{','.join(diff)}"
                    result_dict["error"].append(hadoop_instance)
            else:
                for hadoop_instance in hadoop_instance_ls:
                    result_dict["correct"].append(hadoop_instance)

        # 按照 row 行号对列表进行排序
        for v in result_dict.values():
            if len(v) > 0:
                v.sort(key=lambda x: x.get("row", 999))
        attrs["result_dict"] = result_dict
        logger.info("deployment plan validate end")
        return attrs


class DeploymentImportSerializer(Serializer):
    """ 部署计划导入序列化类 """

    instance_info_ls = serializers.ListField(
        child=serializers.DictField(),
        help_text="主机信息列表",
        required=True, allow_empty=False,
        error_messages={"required": "必须包含[instance_info_ls]字段"}
    )

    service_data_ls = serializers.ListField(
        child=serializers.DictField(),
        help_text="服务数据列表",
        required=True, allow_empty=False,
        error_messages={"required": "必须包含[host_list]字段"}
    )

    operation_uuid = serializers.CharField(
        max_length=64,
        help_text="唯一操作id",
        required=False
    )


class DeploymentPlanListSerializer(ModelSerializer):
    """ 部署计划列表序列化类 """

    class Meta:
        """ 元数据 """
        model = DeploymentPlan
        fields = "__all__"


class ExecutionRecordSerializer(ModelSerializer):
    state_display = serializers.CharField(source="get_state_display")
    can_rollback = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()

    def get_can_rollback(self, obj):
        if obj.module != "UpgradeHistory":
            return False
        module_obj = getattr(models, obj.module).objects.get(
            id=int(obj.module_id)
        )
        return module_obj.can_roll_back

    def get_duration(self, obj):
        if not obj.end_time:
            return "-"
        return timedelta_strftime(obj.end_time - obj.created)

    class Meta:
        model = ExecutionRecord
        fields = ("id", "operator", "count", "state", "state_display",
                  "can_rollback", "duration", "created", "end_time",
                  "module", "module_id")


class DeleteComponentSerializer(ModelSerializer):
    """
    基础组件序列化
    """
    name = serializers.SerializerMethodField()
    versions = serializers.SerializerMethodField()

    class Meta:
        """ 元数据 """
        model = ApplicationHub
        fields = ("name", "versions")

    def get_name(self, obj):
        return obj.app_name

    def get_versions(self, obj):
        return [obj.app_version]


class DeleteProDuctSerializer(ModelSerializer):
    """
    产品序列化
    """
    name = serializers.SerializerMethodField()
    versions = serializers.SerializerMethodField()

    class Meta:
        """ 元数据 """
        model = ProductHub
        fields = ("name", "versions")

    def get_name(self, obj):
        return f"{obj.pro_name}|{obj.pro_version}"

    def get_versions(self, obj):
        app_ls = []
        app_values = ApplicationHub.objects.filter(
            product=obj).values_list("app_name", "app_version")
        for app in app_values:
            app_ls.append(f"{app[0]}|{app[1]}")
        return app_ls
