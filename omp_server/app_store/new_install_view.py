# -*- coding: utf-8 -*-
# Project: new_install_view
# Author: jon.liu@yunzhihui.com
# Create time: 2021-11-12 09:19
# IDE: PyCharm
# Version: 1.0
# Introduction:

import uuid
import logging
from collections import OrderedDict

from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    ListModelMixin, CreateModelMixin
)

from db_models.models import (
    ApplicationHub, ProductHub, Product, Service,
    MainInstallHistory, DetailInstallHistory, Host,
    PreInstallHistory, PostInstallHistory
)
from utils.common.exceptions import ValidationError
from utils.common.paginations import PageNumberPager
from app_store.install_utils import ServiceArgsSerializer
from app_store.new_install_utils import BaseRedisData

from app_store.new_install_serializers import (
    CreateInstallInfoSerializer,
    CheckInstallInfoSerializer,
    CreateServiceDistributionSerializer,
    CheckServiceDistributionSerializer,
    CreateInstallPlanSerializer,
    MainInstallHistorySerializer,
    CreateComponentInstallInfoSerializer,
    RetryInstallSerializer
)

logger = logging.getLogger("server")
UNIQUE_KEY_ERROR = "后台无法追踪此流程,请重新进行安装操作!"


class BatchInstallEntranceView(GenericViewSet, ListModelMixin):
    """
    批量安装入口
        List:
        获取批量安装参数范围
    """
    get_description = "获取批量安装数据"

    @staticmethod
    def check_product_instance(pro_name, pro_version_lst):
        """
        检查应用产品是否安装过
        :param pro_name: 应用名称
        :param pro_version_lst: 应用版本
        :return:
        """
        queryset = Product.objects.filter(
            product__pro_name=pro_name,
            product__pro_version__in=pro_version_lst
        )
        if queryset.exists():
            # 判断产品下是否还有服务，如果没有服务，那么
            if Service.objects.filter(
                service__product_id__in=queryset.values_list(
                    "product_id", flat=True
                )
            ).exists():
                return True
            queryset.delete()
        return False

    def list(self, request, *args, **kwargs):
        """
        获取批量安装参数范围
        :param request:
        :type request: Request
        :param args:
        :param kwargs:
        :return:
        """
        if Host.objects.all().count() == 0:
            raise ValidationError(
                "当前系统内无可用主机，请先纳管主机后再执行安装操作！")
        product_name = request.query_params.get("product_name")
        if not product_name:
            product_queryset = ProductHub.objects.filter(
                is_release=True).values(
                "pro_name", "pro_version"
            )
        else:
            product_queryset = ProductHub.objects.filter(
                is_release=True, pro_name=product_name).values(
                "pro_name", "pro_version"
            )
        tmp_dic = dict()
        for item in product_queryset:
            if item.get("pro_name") not in tmp_dic:
                tmp_dic[item["pro_name"]] = list()
            tmp_dic[item["pro_name"]].append(item["pro_version"])
        _data = [
            {
                "name": key,
                "version": value,
                "is_continue": not self.check_product_instance(key, value)
            }
            for key, value in tmp_dic.items()
        ]
        unique_key = str(uuid.uuid4())
        # unique_key = str("21e041a9-c9a5-4734-9673-7ed932625d21")
        data = {
            "data": _data,
            "unique_key": unique_key
        }
        # 添加安装唯一标识到redis内
        BaseRedisData(unique_key=unique_key).step_1_set_unique_key(data=data)
        return Response(data=data)


class CreateInstallInfoView(GenericViewSet, CreateModelMixin):
    serializer_class = CreateInstallInfoSerializer
    post_description = "创建基础安装数据"


class CheckInstallInfoView(GenericViewSet, CreateModelMixin):
    serializer_class = CheckInstallInfoSerializer
    post_description = "校验基础安装数据"


class CreateServiceDistributionView(GenericViewSet, CreateModelMixin):
    serializer_class = CreateServiceDistributionSerializer
    post_description = "生成部署服务分布源数据"


class CheckServiceDistributionView(GenericViewSet, CreateModelMixin):
    serializer_class = CheckServiceDistributionSerializer
    post_description = "校验服务分布"


class GetInstallHostRangeView(GenericViewSet, ListModelMixin):
    get_description = "获取安装主机范围"

    def list(self, request, *args, **kwargs):
        """
        获取某次安装涉及到的主机范围接口
        :param request: 请求
        :type request: Request
        :param args:
        :param kwargs:
        :return:
        """
        unique_key = request.query_params.get("unique_key")
        if not unique_key:
            return Response(
                data={"error_msg": "请求参数必须包含[unique_key]字段"})
        _data = BaseRedisData(unique_key).get_step_5_host_list()
        return Response(data={
            "unique_key": unique_key,
            "data": _data
        })


class GetInstallArgsByIpView(GenericViewSet, ListModelMixin):
    get_description = "获取某主机上的服务的安装参数"

    def list(self, request, *args, **kwargs):
        """
        获取某次安装涉及到的主机范围接口
        :param request: 请求
        :type request: Request
        :param args:
        :param kwargs:
        :return:
        """
        unique_key = request.query_params.get("unique_key")
        ip = request.query_params.get("ip")
        if not unique_key or not ip:
            return Response(
                data={"error_msg": "请求参数必须包含[unique_key]和[ip]"})
        _data = BaseRedisData(unique_key).get_step_5_host_service_map()
        check_data = BaseRedisData(unique_key).get_step_2_origin_data()
        install_ser = check_data.get("install")
        services_lst = _data.get(ip, [])
        app_lst = ApplicationHub.objects.filter(app_name__in=services_lst)
        _ret_data = list()
        for item in app_lst:
            if item.app_name not in install_ser or \
                    item.app_version != install_ser[item.app_name].get("version"):
                continue
            install_args = ServiceArgsSerializer().get_app_install_args(item)
            install_args.insert(
                0, {
                    "key": "instance_name",
                    "name": "实例名称",
                    "default":
                        item.app_name + "-" + "-".join(ip.split(".")[-2:]),
                    "editable": True
                }
            )
            _app = {
                "name": item.app_name,
                "instance_name":
                    item.app_name + "-" + "-".join(ip.split(".")[-2:]),
                "install_args": install_args,
                "ports": ServiceArgsSerializer().get_app_port(item)
            }
            _ret_data.append(_app)
        if len(_ret_data) != len(services_lst):
            logger.info(f"GetInstallArgsByIpView ERROR: \n"
                        f"ip: {ip}\n"
                        f"services_lst: {services_lst}\n"
                        f"_ret_data: {_ret_data}")
            return Response(
                data={
                    "error_msg": "存储数据出现错误，"
                                 "请检查应用商店内已纳管服务是否有变化！"
                }
            )
        return Response(data={
            "unique_key": unique_key,
            "data": _ret_data
        })


class CreateInstallPlanView(GenericViewSet, CreateModelMixin):
    serializer_class = CreateInstallPlanSerializer
    post_description = "校验并生成部署计划"


class ListServiceByIpView(GenericViewSet, ListModelMixin):
    def list(self, request, *args, **kwargs):
        """
        根据ip显示主机上安装的服务
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        # ip = request.query_params.get("ip")
        _data = Service.objects.filter().exclude(
            service__is_base_env=True
        ).values(
            "ip", "service__app_name", "service_instance_name"
        )
        data = dict()
        for item in _data:
            if item["ip"] not in data:
                data[item["ip"]] = list()
            data[item["ip"]].append(item)
        return Response(data=data)


class ShowInstallProcessView(GenericViewSet, ListModelMixin):
    def list(self, request, *args, **kwargs):
        """
        显示安装的进度信息
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        unique_key = request.query_params.get("unique_key")
        main_obj = MainInstallHistory.objects.filter(
            operation_uuid=unique_key).last()
        if not main_obj:
            raise ValidationError(f"{unique_key}不存在!")
        main_status = main_obj.install_status
        install_detail_queryset = DetailInstallHistory.objects.filter(
            main_install_history=main_obj
        ).exclude(service=None).values(
            "service__service__app_name",
            "service__ip",
            "install_step_status"
        )
        pre_queryset = PreInstallHistory.objects.filter(
            main_install_history=main_obj
        ).values("ip", "install_flag", "install_log", "name")
        detail_dic = OrderedDict()
        install_success_num = total_num = 0
        for item in pre_queryset:
            app_name = item.get("name")
            if app_name not in detail_dic:
                detail_dic[app_name] = list()
            detail_dic[app_name].append({
                "ip": item["ip"],
                "status": item["install_flag"]
            })
            if item["install_flag"] == 2:
                install_success_num += 1
            total_num += 1
        for item in install_detail_queryset:
            app_name = item["service__service__app_name"]
            if app_name not in detail_dic:
                detail_dic[app_name] = list()
            detail_dic[app_name].append({
                "ip": item["service__ip"],
                "status": item["install_step_status"]
            })
            if item["install_step_status"] == \
                    DetailInstallHistory.INSTALL_STATUS_SUCCESS:
                install_success_num += 1
            total_num += 1
        post_queryset = PostInstallHistory.objects.filter(
            main_install_history=main_obj
        ).values("ip", "install_flag", "install_log", "name")
        for item in post_queryset:
            app_name = item.get("name")
            if app_name not in detail_dic:
                detail_dic[app_name] = list()
            detail_dic[app_name].append({
                "ip": item["ip"],
                "status": item["install_flag"]
            })
            if item["install_flag"] == 2:
                install_success_num += 1
            total_num += 1
        if total_num != 0:
            percentage = int((install_success_num / total_num) * 100)
            if main_status != MainInstallHistory.INSTALL_STATUS_SUCCESS and \
                    percentage == 100:
                percentage = 95
        else:
            if main_status == MainInstallHistory.INSTALL_STATUS_SUCCESS:
                percentage = 100
            else:
                percentage = 5
        data = {
            "status": main_status,
            "detail": detail_dic,
            "percentage": percentage
        }
        return Response(data=data)


class ShowSingleServiceInstallLogView(GenericViewSet, ListModelMixin):

    def get_pre_install_log(self, main_obj, ip):
        """
        获取日志
        :param main_obj:
        :param ip:
        :return:
        """
        _pre_obj = PreInstallHistory.objects.filter(
            main_install_history=main_obj, ip=ip).last()
        return _pre_obj.install_log

    def get_post_install_log(self, main_obj, ip):
        """
        获取日志
        :param main_obj:
        :param ip:
        :return:
        """
        _post_obj = PostInstallHistory.objects.filter(
            main_install_history=main_obj, ip=ip).last()
        return _post_obj.install_log

    def list(self, request, *args, **kwargs):
        """
        查找某服务的安装日志
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        ip = request.query_params.get("ip")
        app_name = request.query_params.get("app_name")
        unique_key = request.query_params.get("unique_key")
        lst = [
            "send_msg", "unzip_msg", "install_msg",
            "init_msg", "start_msg", "post_action_msg"
        ]
        main_obj = MainInstallHistory.objects.filter(
            operation_uuid=unique_key
        ).last()
        if app_name == "初始化安装流程":
            log = self.get_pre_install_log(main_obj=main_obj, ip=ip)
            return Response(data={"log": log})
        if app_name == "安装后续任务":
            log = self.get_post_install_log(main_obj=main_obj, ip=ip)
            return Response(data={"log": log})
        detail = DetailInstallHistory.objects.filter(
            main_install_history=main_obj,
            service__service__app_name=app_name,
            service__ip=ip
        ).last()

        def get_log(detail):
            _log = ""
            for item in lst:
                _log += getattr(detail, item, "")
            return _log

        log = get_log(detail)
        return Response(data={"log": log})


class MainInstallHistoryView(GenericViewSet, ListModelMixin):
    queryset = MainInstallHistory.objects.all().order_by("-id")
    serializer_class = MainInstallHistorySerializer
    pagination_class = PageNumberPager


class CreateComponentInstallInfoView(GenericViewSet, CreateModelMixin):
    serializer_class = CreateComponentInstallInfoSerializer
    post_description = "创建基础组件安装数据"


class RetryInstallView(GenericViewSet, CreateModelMixin):
    serializer_class = RetryInstallSerializer
    post_description = "重试安装"
