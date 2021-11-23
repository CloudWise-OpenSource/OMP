# -*- coding: utf-8 -*-
# Project: new_install_view
# Author: jon.liu@yunzhihui.com
# Create time: 2021-11-12 09:19
# IDE: PyCharm
# Version: 1.0
# Introduction:

import logging
from collections import OrderedDict

from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    ListModelMixin, CreateModelMixin
)

from db_models.models import (
    ApplicationHub, ProductHub, Product, Service,
    MainInstallHistory, DetailInstallHistory
)
from utils.common.exceptions import ValidationError
from app_store.install_utils import ServiceArgsSerializer
from app_store.new_install_utils import BaseRedisData

from app_store.new_install_serializers import (
    CreateInstallInfoSerializer,
    CheckInstallInfoSerializer,
    CreateServiceDistributionSerializer,
    CheckServiceDistributionSerializer,
    CreateInstallPlanSerializer
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
        :param pro_version: 应用版本
        :return:
        """
        if Product.objects.filter(
                product__pro_name=pro_name,
                product__pro_version__in=pro_version_lst
        ).exists():
            return True
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
        # unique_key = str(uuid.uuid4())
        unique_key = str("21e041a9-c9a5-4734-9673-7ed932625d21")
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
        print(_data)
        check_data = BaseRedisData(unique_key).get_step_2_origin_data()
        print(check_data)
        install_ser = check_data.get("install")
        services_lst = _data.get(ip, [])
        app_lst = ApplicationHub.objects.filter(app_name__in=services_lst)
        _ret_data = list()
        for item in app_lst:
            if item.app_name not in install_ser or \
                    item.app_version == install_ser[item.app_name]:
                continue
            _app = {
                "name": item.app_name,
                "install_args":
                    ServiceArgsSerializer().get_app_install_args(item),
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
        ip = request.query_params.get("ip")
        _data = Service.objects.filter(ip=ip).values(
            "service__app_name", "service_instance_name"
        )
        return Response(data=list(_data))


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
        ).values(
            "service__service__app_name",
            "service__ip",
            "install_step_status"
        )
        detail_dic = OrderedDict()
        for item in install_detail_queryset:
            app_name = item["service__service__app_name"]
            if app_name not in detail_dic:
                detail_dic[app_name] = list()
            detail_dic[app_name].append({
                "ip": item["service__ip"],
                "status": item["install_step_status"]
            })
        data = {
            "status": main_status,
            "detail": detail_dic
        }
        return Response(data=data)


class ShowSingleServiceInstallLogView(GenericViewSet, ListModelMixin):
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
