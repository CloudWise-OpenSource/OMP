"""
主机相关视图
"""
import logging
from django.db import transaction

from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    ListModelMixin, CreateModelMixin, UpdateModelMixin,
    RetrieveModelMixin
)
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from django_filters.rest_framework.backends import DjangoFilterBackend

from db_models.models import (Env, Host, HostOperateLog)
from utils.plugin.crypto import AESCryptor
from utils.common.paginations import PageNumberPager
from hosts.tasks import insert_host_celery_task
from hosts.hosts_filters import (HostFilter, HostOperateFilter)
from hosts.hosts_serializers import (
    HostSerializer, HostMaintenanceSerializer,
    HostFieldCheckSerializer, HostAgentRestartSerializer,
    HostOperateLogSerializer, HostBatchValidateSerializer,
    HostBatchImportSerializer, HostDetailSerializer,
    HostInitSerializer, HostsAgentStatusSerializer,
    HostReinstallSerializer, MonitorReinstallSerializer
)
from promemonitor.prometheus import Prometheus
from promemonitor.grafana_url import explain_url
from utils.common.exceptions import OperateError
from utils.common.views import BaseDownLoadTemplateView

logger = logging.getLogger("server")


class HostListView(GenericViewSet, ListModelMixin, CreateModelMixin):
    """
        list:
        查询主机列表

        create:
        创建一个新主机
    """
    queryset = Host.objects.filter(is_deleted=False)
    serializer_class = HostSerializer
    pagination_class = PageNumberPager
    # 过滤，排序字段
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_class = HostFilter
    ordering_fields = ("ip", "host_agent", "monitor_agent",
                       "service_num", "alert_num")
    # 动态排序字段
    dynamic_fields = ("cpu_usage", "mem_usage",
                      "root_disk_usage", "data_disk_usage")
    # 操作描述信息
    get_description = "查询主机"
    post_description = "创建主机"

    def list(self, request, *args, **kwargs):
        # 获取序列化数据列表
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(
            self.paginate_queryset(queryset), many=True)
        serializer_data = serializer.data
        # 主机密码解密
        for host_info in serializer_data:
            aes_crypto = AESCryptor()
            password = aes_crypto.decode(host_info.get("password"))
            # 密码返回 base64 编码结果
            import base64
            host_info["password"] = base64.b64encode(password.encode())

        # 获取监控及日志的url
        serializer_data = explain_url(serializer_data)

        # 实时获取主机动态
        prometheus_obj = Prometheus()
        serializer_data = prometheus_obj.get_host_info(serializer_data)

        # 获取请求中 ordering 字段
        query_field = request.query_params.get("ordering", "")
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


class HostReinstallView(GenericViewSet, CreateModelMixin):
    """
        create:
        重装主机Agent接口
    """
    queryset = Host.objects.filter(is_deleted=False)
    serializer_class = HostReinstallSerializer
    # 操作信息描述
    post_description = "重装主机Agent"


class MonitorReinstallView(GenericViewSet, CreateModelMixin):
    """
        create:
        重装监控Agent接口
    """
    queryset = Host.objects.filter(is_deleted=False)
    serializer_class = MonitorReinstallSerializer
    # 操作信息描述
    post_description = "重装监控Agent"


class HostDetailView(GenericViewSet, RetrieveModelMixin):
    """
        read:
        查询主机详情
    """
    queryset = Host.objects.filter(is_deleted=False)
    serializer_class = HostDetailSerializer
    # 操作描述信息
    get_description = "查询主机详情"


class HostUpdateView(GenericViewSet, UpdateModelMixin):
    """
        update:
        更新一个主机

        partial_update:
        更新一个现有主机的一个或多个字段
    """
    queryset = Host.objects.filter(is_deleted=False)
    serializer_class = HostSerializer
    # 操作描述信息
    put_description = patch_description = "更新主机"


class HostFieldCheckView(GenericViewSet, CreateModelMixin):
    """
        create:
        验证主机 instance_name/ip 字段重复性
    """
    queryset = Host.objects.filter(is_deleted=False)
    serializer_class = HostFieldCheckSerializer
    # 操作信息描述
    post_description = "校验主机字段重复性"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        return Response(serializer.is_valid())


class IpListView(GenericViewSet, ListModelMixin):
    """
        list:
        查询所有 IP 列表
    """
    queryset = Host.objects.filter(
        is_deleted=False).values_list("ip", flat=True)
    # 操作信息描述
    get_description = "查询主机"

    def list(self, request, *args, **kwargs):
        return Response(list(self.get_queryset()))


class HostMaintenanceView(GenericViewSet, CreateModelMixin):
    """
        create:
        主机进入 / 退出维护模式
    """
    queryset = Host.objects.filter(is_deleted=False)
    serializer_class = HostMaintenanceSerializer
    # 操作信息描述
    post_description = "修改主机维护模式"


class HostAgentRestartView(GenericViewSet, CreateModelMixin):
    """
        create:
        主机重启Agent接口
    """
    queryset = Host.objects.filter(is_deleted=False)
    serializer_class = HostAgentRestartSerializer
    # 操作信息描述
    post_description = "重启主机Agent"


class HostOperateLogView(GenericViewSet, ListModelMixin):
    """
        list:
        主机操作记录
    """
    queryset = HostOperateLog.objects.all()
    serializer_class = HostOperateLogSerializer
    # 过滤，排序字段
    filter_backends = (DjangoFilterBackend,)
    filter_class = HostOperateFilter
    # 操作信息描述
    get_description = "查询主机操作记录"


class HostBatchValidateView(BaseDownLoadTemplateView, CreateModelMixin):
    """
        list:
        获取主机批量导入模板

        create:
        主机数据批量验证
    """
    queryset = Host.objects.filter(is_deleted=False)
    serializer_class = HostBatchValidateSerializer
    # 操作描述信息
    get_description = "获取主机批量导入模板"
    post_description = "主机数据批量验证"

    def list(self, request, *args, **kwargs):
        return super(HostBatchValidateView, self).list(
            request, template_file_name="import_hosts_template.xlsx",
            *args, **kwargs)

    def create(self, request, *args, **kwargs):
        ips = Host.objects.all().values_list("ip", flat=True)
        request_data = []
        repeat_data = []
        for host in request.data.get("host_list"):
            if not host.get("ip") in ips:
                request_data.append(host)
            else:
                host["init_host"] = True
                repeat_data.append(host)
        if len(request_data) == 0:
            return Response({"correct": repeat_data, "error": []})
        serializer = self.get_serializer(data=request_data)
        if not serializer.is_valid():
            logger.error(f"host batch validate failed:{request.data}")
            raise ValidationError("数据格式错误")
        serializer.validated_data.get("result_dict", {}).get(
            "correct", []).extend(repeat_data)
        return Response(serializer.validated_data.get("result_dict"))


class HostBatchImportView(GenericViewSet, CreateModelMixin):
    """
        create:
        主机批量添加
    """
    serializer_class = HostBatchImportSerializer
    # 操作描述信息
    post_description = "主机批量添加"

    def create(self, request, *args, **kwargs):
        # 信任数据，只进行格式校验
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"host batch import failed:{request.data}")
            raise ValidationError("数据格式错误")
        try:
            # 主机、操作记录数据入库
            default_env = Env.objects.filter(id=1).first()
            with transaction.atomic():
                # 主机初始化信息，批量创建过程中无 id，故以 ip 作为键
                host_init_info = {}
                host_objs = []
                ips = Host.objects.all().values_list("ip", flat=True)
                for host in serializer.data.get("host_list"):
                    if host.get("ip") in ips:
                        continue
                    # 若存在行号、运行用户则删除
                    if "row" in host:
                        host.pop("row")
                    if "run_user" in host:
                        host.pop("run_user")
                    host_init_info[host.get("ip")] = host.pop(
                        "init_host", False)
                    password = host.pop("password")
                    host_objs.append(Host(
                        password=AESCryptor().encode(password),
                        agent_dir=host.get("data_folder"),
                        env=default_env,
                        **host,
                    ))
                Host.objects.bulk_create(host_objs)
                # bulk_create 不返回 id，需重查获取
                instance_name_list = list(
                    map(lambda x: x.instance_name, host_objs))
                host_instances = Host.objects.filter(
                    instance_name__in=instance_name_list)
                operate_log_objs = []
                for instance in host_instances:
                    operate_log_objs.append(HostOperateLog(
                        username=request.user.username,
                        description="创建主机",
                        host=instance,
                    ))
                    # 下发异步 celery 任务
                    insert_host_celery_task.delay(
                        instance.id, init=host_init_info.get(instance.ip))
                HostOperateLog.objects.bulk_create(operate_log_objs)
        except Exception as err:
            logger.error(f"batch import host err: {err}")
            import traceback
            logger.error(traceback.print_exc())
            raise OperateError("批量导入主机失败")
        return Response("添加成功")


class HostInitView(BaseDownLoadTemplateView, CreateModelMixin):
    """
        create:
        主机初始化
    """
    queryset = Host.objects.filter(is_deleted=False)
    serializer_class = HostInitSerializer
    # 操作描述信息
    get_description = "应用商店下载组件模板"
    # 操作信息描述
    post_description = "主机初始化"

    def list(self, request, *args, **kwargs):
        return super(HostInitView, self).list(
            request, template_file_name="init_host.py",
            parent_path="_modules", *args, **kwargs)


class HostsAgentStatusView(GenericViewSet, CreateModelMixin):
    """
        create:
        主机agent状态查询
    """
    queryset = Host.objects.filter(is_deleted=False)
    serializer_class = HostsAgentStatusSerializer
    # 操作信息描述
    post_description = "主机agent状态查询"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"hosts agent status failed:{request.data}")
            raise ValidationError("数据格式错误")
        ip_set = set(serializer.data.get("ip_list"))
        agent_online_ip_set = set(self.get_queryset().filter(
            ip__in=ip_set, host_agent=Host.AGENT_RUNNING
        ).values_list("ip", flat=True))
        return Response(ip_set == agent_online_ip_set)
