# -*- coding: utf-8 -*-
# Project: new_install_view
# Author: jon.liu@yunzhihui.com
# Create time: 2021-11-12 09:19
# IDE: PyCharm
# Version: 1.0
# Introduction:

import logging

from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    ListModelMixin, CreateModelMixin
)

from db_models.models import (
    ApplicationHub, ProductHub,
)

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
            {"name": key, "version": value} for key, value in tmp_dic.items()
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
