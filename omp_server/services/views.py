import json
import logging
import os

from django.conf import settings
from django.http import Http404
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    ListModelMixin, RetrieveModelMixin,
    CreateModelMixin
)
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter

from db_models.models import Service, ApplicationHub, MainInstallHistory
from service_upgrade.update_data_json import DataJsonUpdate
from services.permission import GetDataJsonAuthenticated
from services.tasks import exec_action
from services.services_filters import ServiceFilter
from services.services_serializers import (
    ServiceSerializer, ServiceDetailSerializer,
    ServiceActionSerializer, ServiceDeleteSerializer,
    ServiceStatusSerializer
)
from promemonitor.prometheus import Prometheus
from promemonitor.grafana_url import explain_url
from utils.common.exceptions import OperateError
from utils.common.paginations import PageNumberPager

logger = logging.getLogger('server')


class ServiceListView(GenericViewSet, ListModelMixin):
    """
        list:
        查询服务列表
    """
    queryset = Service.objects.filter(
        service__is_base_env=False)
    serializer_class = ServiceSerializer
    pagination_class = PageNumberPager
    # 过滤，排序字段
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_class = ServiceFilter
    ordering_fields = ("ip", "service_instance_name")
    # 动态排序字段
    dynamic_fields = ("cpu_usage", "mem_usage")
    # 操作描述信息
    get_description = "查询服务列表"

    def list(self, request, *args, **kwargs):
        # 获取序列化数据列表
        queryset = self.filter_queryset(self.get_queryset())
        real_query = queryset

        # 实时获取服务动态git
        prometheus_obj = Prometheus()
        is_success, prometheus_dict = prometheus_obj.get_all_service_status()

        # 当未指定排序字段且查询成功时
        query_field = request.query_params.get("ordering", "")
        if is_success and query_field == "":
            stop_ls = []
            natural_ls = []
            no_monitor_ls = []
            ing_ls = []
            for service in queryset:
                # 当服务状态为 '正常' 和 '异常' 时
                if service.service_status in (Service.SERVICE_STATUS_NORMAL, Service.SERVICE_STATUS_STOP):
                    key_name = f"{service.ip}_{service.service_instance_name}"
                    status = prometheus_dict.get(key_name, None)
                    if status is None:
                        no_monitor_ls.append(service)
                    elif not status:
                        stop_ls.append(service)
                    else:
                        natural_ls.append(service)
                else:
                    ing_ls.append(service)
            real_query = stop_ls + ing_ls + natural_ls + no_monitor_ls

        serializer = self.get_serializer(
            self.paginate_queryset(real_query), many=True)
        serializer_data = serializer.data

        # 若获取成功，则动态覆盖服务状态
        if is_success:
            status_dict = {
                True: "正常",
                False: "停止",
                None: "未监控",
            }
            for service_obj in serializer_data:
                # 如果服务状态为 '正常' 和 '停止' 的服务，通过 Prometheus 动态更新
                if service_obj.get("service_status") in ("正常", "停止"):
                    # 如果是 web 服务，则状态直接置为正常
                    if service_obj.get("is_web"):
                        service_obj["service_status"] = "正常"
                        continue
                    key_name = f"{service_obj.get('ip')}_{service_obj.get('service_instance_name')}"
                    status = prometheus_dict.get(key_name, None)
                    service_obj["service_status"] = status_dict.get(status)

        # 获取监控及日志的url
        serializer_data = explain_url(
            serializer_data, is_service=True)

        serializer_data = prometheus_obj.get_service_info(serializer_data)
        reverse_flag = False
        if query_field.startswith("-"):
            reverse_flag = True
            query_field = query_field[1:]
        # 若排序字段在类视图 dynamic_fields 中，则对根据动态数据进行排序
        none_ls = list(filter(
            lambda x: x.get(query_field) is None,
            serializer_data))
        exists_ls = list(filter(
            lambda x: x.get(query_field) is not None,
            serializer_data))
        if query_field in self.dynamic_fields:
            exists_ls = sorted(
                exists_ls,
                key=lambda x: x.get(query_field),
                reverse=reverse_flag)
        exists_ls.extend(none_ls)
        return self.get_paginated_response(exists_ls)


class ServiceDetailView(GenericViewSet, RetrieveModelMixin):
    """
        read:
        查询服务详情
    """
    queryset = Service.objects.all()
    serializer_class = ServiceDetailSerializer
    # 操作描述信息
    get_description = "查询服务详情"


class ServiceActionView(GenericViewSet, CreateModelMixin):
    """
        create:
        服务启停删除
    """
    queryset = Service.objects.all()
    serializer_class = ServiceActionSerializer
    post_description = "执行启动停止或卸载操作"

    def create(self, request, *args, **kwargs):
        many_data = self.request.data.get('data')
        for data in many_data:
            action = data.get("action")
            instance = data.get("id")
            operation_user = data.get("operation_user")
            del_file = data.get("del_file", True)
            service_obj = Service.objects.filter(id=instance).first()
            need_split = ["hadoop"]
            if service_obj and service_obj.service.app_name in need_split and action == 4:
                delete_objs = Service.objects.filter(ip=service_obj.ip, service__app_name="hadoop")
                status = service_obj.service_status
                delete_objs.update(service_status=Service.SERVICE_STATUS_DELETING)
                if status != Service.SERVICE_STATUS_DELETING \
                        and delete_objs.first().id == service_obj.id:
                    del_file = True
                else:
                    del_file = False
            if action and instance and operation_user:
                if action == 4:
                    try:
                        service_obj.service_status = Service.SERVICE_STATUS_DELETING
                        service_obj.save()
                    except Exception as e:
                        logger.error(f"service实例id，不存在{instance}:{e}")
                        return Response("执行异常")
                exec_action.delay(action, instance, operation_user, del_file)
            else:
                raise OperateError("请输入action或id")
        return Response("执行成功")


class ServiceDeleteView(GenericViewSet, CreateModelMixin):
    """
        create:
        服务删除校验
    """
    queryset = Service.objects.all()
    serializer_class = ServiceDeleteSerializer
    post_description = "查看服务删除校验依赖"

    def create(self, request, *args, **kwargs):
        """
        检查被依赖关系，包含多服务匹配
        例如 jdk-1.8和 test-app被同时标记删除
        test-app依赖jdk-1.8，同时标记则不显示依赖。单选jdk1.8则会显示。
        """
        many_data = self.request.data.get('data')
        service_objs = Service.objects.all()
        app_objs = ApplicationHub.objects.all()
        service_json = {}
        dependence_dict = []
        # 存在的service key
        for i in service_objs:
            service_key = f"{i.service.app_name}-{i.service.app_version}"
            service_json[i.id] = service_key
        # 全量app的dependence反向
        for app in app_objs:
            if app.app_dependence:
                for i in json.loads(app.app_dependence):
                    dependence_dict.append(
                        {f"{i.get('name')}-{i.get('version')}": f"{app.app_name}-{app.app_version}"}
                    )
        exist_service = set()
        # 过滤存在的实例所属app的key
        for data in many_data:
            instance = int(data.get("id"))
            filter_list = service_json.get(instance)
            exist_service.add(filter_list)
        # 查看存在的服务有没有被依赖的，做set去重
        res = set()
        for i in exist_service:
            for j in dependence_dict:
                if j.get(i):
                    res.add(j.get(i))
        res = res - exist_service
        # 查看是否需要被依赖的是否已不存在
        res = res & set(service_json.values())
        res = "存在依赖信息:" + ",".join(res) if res else "无依赖信息"
        return Response(res)


class ServiceStatusView(GenericViewSet, ListModelMixin):
    """
        list:
        查询服务列表
    """
    queryset = Service.objects.filter(
        service__is_base_env=False)
    serializer_class = ServiceStatusSerializer
    authentication_classes = ()
    permission_classes = ()
    # 操作描述信息
    get_description = "查询服务状态"

    def list(self, request, *args, **kwargs):
        # 获取序列化数据列表
        queryset = self.get_queryset()
        real_query = queryset
        # 实时获取服务动态git
        prometheus_obj = Prometheus()
        is_success, prometheus_dict = prometheus_obj.get_all_service_status()
        if is_success:
            stop_ls = []
            natural_ls = []
            no_monitor_ls = []
            ing_ls = []
            for service in queryset:
                # 当服务状态为 '正常' 和 '异常' 时
                if service.service_status in (Service.SERVICE_STATUS_NORMAL, Service.SERVICE_STATUS_STOP):
                    key_name = f"{service.ip}_{service.service_instance_name}"
                    status = prometheus_dict.get(key_name, None)
                    if status is None:
                        no_monitor_ls.append(service)
                    elif not status:
                        stop_ls.append(service)
                    else:
                        natural_ls.append(service)
                else:
                    ing_ls.append(service)
            real_query = stop_ls + ing_ls + natural_ls + no_monitor_ls

        serializer = self.get_serializer(real_query, many=True)
        serializer_data = serializer.data

        # 若获取成功，则动态覆盖服务状态
        if is_success:
            for service_obj in serializer_data:
                # 如果服务状态为 '正常' 和 '停止' 的服务，通过 Prometheus 动态更新
                if service_obj.get("service_status") in ("正常", "停止"):
                    # 如果是 web 服务，则状态直接置为正常
                    if service_obj.get("is_web"):
                        service_obj["service_status"] = True
                        continue
                    key_name = f"{service_obj.get('ip')}_{service_obj.get('service_instance_name')}"
                    status = prometheus_dict.get(key_name, None)
                    service_obj["service_status"] = status
        return Response(serializer_data)


class ServiceDataJsonView(APIView):
    # for automated testing
    permission_classes = (GetDataJsonAuthenticated, )

    def get(self, request):
        main_install = MainInstallHistory.objects.order_by("-id").first()
        if not main_install:
            raise Http404('No install history matches the given query.')
        json_path = os.path.join(
            settings.PROJECT_DIR,
            f"package_hub/data_files/{main_install.operation_uuid}.json"
        )
        if not os.path.exists(json_path):
            DataJsonUpdate(main_install.operation_uuid).create_json_file()
        with open(json_path, "r") as f:
            json_data = json.load(f)
        return Response({"json_data": json_data})
