import json
import os

from django.db import models

from db_models.mixins import TimeStampMixin, DeleteMixin
from utils.common.exceptions import GeneralError
from .env import Env
from .product import ApplicationHub


class ServiceConnectInfo(TimeStampMixin):
    """ 存储用户名密码信息 """
    # 服务用户名、密码信息，同一个集群公用一套用户名、密码
    objects = None
    service_name = models.CharField(
        "服务名", max_length=32,
        null=False, blank=False, help_text="服务名")
    service_username = models.CharField(
        "用户名", max_length=512,
        null=True, blank=True, help_text="用户名")
    service_password = models.CharField(
        "密码", max_length=512,
        null=True, blank=True, help_text="密码")
    service_username_enc = models.CharField(
        "加密用户名", max_length=512,
        null=True, blank=True, help_text="加密用户名")
    service_password_enc = models.CharField(
        "加密密码", max_length=512,
        null=True, blank=True, help_text="加密密码")

    class Meta:
        """ 元数据 """
        db_table = "omp_service_connect_info"
        verbose_name = verbose_name_plural = "用户名密码信息表"


class ClusterInfo(TimeStampMixin, DeleteMixin):
    """ 集群信息表 """

    objects = None
    cluster_service_name = models.CharField(
        "集群所属服务", max_length=36,
        null=True, blank=True, help_text="集群所属服务")
    # 选择的集群类型
    cluster_type = models.CharField(
        "集群类型", max_length=36,
        null=True, blank=True, help_text="集群类型")
    # 集群实例名称，虚拟名称
    cluster_name = models.CharField(
        "集群名称", max_length=64,
        null=False, blank=False, help_text="集群名称")
    # 集群连接的信息，公共组件可能存在集群信息，自研服务一般无集群概念
    connect_info = models.CharField(
        "集群连接信息", max_length=512,
        null=True, blank=True, help_text="集群连接信息")
    service_connect_info = models.ForeignKey(
        ServiceConnectInfo, null=True, blank=True,
        on_delete=models.SET_NULL, help_text="用户名密码信息")
    # 预留解析字段，集群连接有多种方式
    # eg1: 10.0.0.1:18117,10.0.0.2:18117,10.0.0.3:18117
    # eg2: 10.0.0.1,10.0.0.2,10.0.0.3:18117
    # 在安装时应该按照指定的方式拼接集群信息
    connect_info_parse_type = models.CharField(
        "连接信息解析方式", max_length=32,
        null=True, blank=True, help_text="连接信息解析方式")

    class Meta:
        """元数据"""
        db_table = "omp_cluster_info"
        verbose_name = verbose_name_plural = "集群信息表"

    def __str__(self):
        return f"<instance> of {self.cluster_name}"


class ExcludeSplit(models.Manager):
    """
    拆分前服务过滤，展示监控纳管专用
    """

    def get_queryset(self):
        return super(ExcludeSplit, self).get_queryset().exclude(service_split=1)


class AfterSplit(models.Manager):
    """
    拆分后服务过滤,安装升级专用
    """

    def get_queryset(self):
        return super(AfterSplit, self).get_queryset().exclude(service_split=2)


class Service(TimeStampMixin):
    """ 服务表 (删除前会触发update_execution_record)"""
    split_objects = AfterSplit()
    objects = ExcludeSplit()
    SERVICE_STATUS_NORMAL = 0
    SERVICE_STATUS_STARTING = 1
    SERVICE_STATUS_STOPPING = 2
    SERVICE_STATUS_RESTARTING = 3
    SERVICE_STATUS_STOP = 4
    SERVICE_STATUS_UNKNOWN = 5
    SERVICE_STATUS_INSTALLING = 6
    SERVICE_STATUS_INSTALL_FAILED = 7
    SERVICE_STATUS_READY = 8
    SERVICE_STATUS_DELETING = 9
    SERVICE_STATUS_UPGRADE = 10
    SERVICE_STATUS_ROLLBACK = 11
    SERVICE_STATUS_CHOICES = (
        (SERVICE_STATUS_NORMAL, "正常"),
        (SERVICE_STATUS_STARTING, "启动中"),
        (SERVICE_STATUS_STOPPING, "停止中"),
        (SERVICE_STATUS_RESTARTING, "重启中"),
        (SERVICE_STATUS_STOP, "停止"),
        (SERVICE_STATUS_UNKNOWN, "未知"),
        (SERVICE_STATUS_INSTALLING, "安装中"),
        (SERVICE_STATUS_INSTALL_FAILED, "安装失败"),
        (SERVICE_STATUS_READY, "待安装"),
        (SERVICE_STATUS_DELETING, "删除中"),
        (SERVICE_STATUS_UPGRADE, "升级中"),
        (SERVICE_STATUS_ROLLBACK, "回滚中")
    )

    PRE_IS_SPLIT = 1
    NO_SPLIT = 0
    AFT_IS_SPLIT = 2
    SERVICE_STATUS_SPLIT = (
        (
            (PRE_IS_SPLIT, "拆分前"),
            (AFT_IS_SPLIT, "拆分后"),
            (NO_SPLIT, "未拆分")
        )
    )

    # 是否用外键关联？
    ip = models.GenericIPAddressField(
        "服务所在主机", help_text="服务所在主机")

    service_instance_name = models.CharField(
        "服务实例名称", max_length=64,
        null=False, blank=False, help_text="服务实例名称")

    service_split = models.IntegerField(
        "拆分服务前对象", choices=SERVICE_STATUS_SPLIT,
        default=0, help_text="拆分服务前对象")

    service = models.ForeignKey(
        ApplicationHub, null=True, blank=True,
        on_delete=models.SET_NULL, help_text="服务表外键")

    # 以下字段含义同 ApplicationHub 但具备定制化场景，无法做得到唯一关联
    # 存储格式[{"port": 18080, "key": "http_port"}]
    service_port = models.TextField(
        "服务端口", null=True, blank=True, help_text="服务端口")
    # 服务控制脚本，按照其所安装的主机拼接绝对路径并进行存储(主机数据目录存在被更改风险)
    # {"start": "./start.sh", "stop": "./stop.sh"}
    service_controllers = models.JSONField(
        "服务控制脚本", null=True, blank=True, help_text="服务控制脚本")

    # 以下字段用于角色及集群使用
    service_role = models.CharField(
        "服务角色", max_length=128,
        null=True, blank=True, help_text="服务角色")
    cluster = models.ForeignKey(
        ClusterInfo, null=True, blank=True,
        on_delete=models.SET_NULL, help_text="所属集群")
    env = models.ForeignKey(
        Env, null=True, blank=True,
        on_delete=models.SET_NULL, help_text="所属环境")

    service_connect_info = models.ForeignKey(
        ServiceConnectInfo, null=True, blank=True,
        on_delete=models.SET_NULL, help_text="用户名密码信息")

    # 服务状态信息
    service_status = models.IntegerField(
        "服务状态", choices=SERVICE_STATUS_CHOICES,
        default=5, help_text="服务状态")

    # 服务告警、自愈、监控信息
    alert_count = models.IntegerField(
        "告警次数", default=0, help_text="告警次数")
    self_healing_count = models.IntegerField(
        "服务自愈次数", default=0, help_text="服务自愈次数")
    # 服务实例间的依赖关系，此字段标明当前服务实例所依赖的其他服务实例关系
    # 注意，当被依赖服务为base_env时，不在此字段中体现
    # 使用json.dumps存储 list结构数据
    service_dependence = models.TextField(
        "服务依赖关系", null=True, blank=True, help_text="服务依赖关系")

    vip = models.GenericIPAddressField(
        "vip地址", null=True, blank=True, default=None, help_text="vip地址")

    class Meta:
        """元数据"""
        db_table = 'omp_service'
        verbose_name = verbose_name_plural = "服务实例表"
        ordering = ("-created",)

    def update_port(self, app_ports):
        """
        比较服务端口，取并集
        :param app_ports: 目标app服务端口
        :return: new service_ports
        """
        # 存储数据格式为[{"default": 18080, "key": "http_port", "name": "服务端口"}]
        if not app_ports:
            return []
        port_dict = {}
        service_ports = json.loads(self.service_port or [])
        for service_port in service_ports:
            port_dict[service_port.get("key")] = service_port.get("default")
        for app_port in app_ports:
            if app_port.get("key") not in port_dict:
                service_ports.append(app_port)
        return service_ports

    def update_controllers(self, application, install_folder):
        """
        更新服务管理命令
        :param application: 服务目标app
        :param install_folder: 安装目录（用于更新服务命令）
        :return: new service_controllers
        """
        _app_controllers = json.loads(application.app_controllers)
        # 获取服务家目录
        install_args = json.loads(application.app_install_args)
        _home = ""
        for el in install_args:
            if "dir_key" in el and el["key"] == "base_dir":
                _home = el["default"]
        real_home = os.path.join(install_folder, _home.rstrip("/"))
        _new_controller = dict()
        # 更改服务控制脚本、拼接相对路径
        for key, value in _app_controllers.items():
            if not value:
                continue
            # 对于hadoop管控命令不动
            if application.app_name == "hadoop" and key in \
                    {"start", "stop", "restart"}:
                _new_controller[key] = self.service_controllers.get(key)
                continue
            _new_controller[key] = os.path.join(real_home, value)
        # 在每次安装完所有服务后，需要搜索出相应的post_action并统一执行
        if "post_action" in application.extend_fields and \
                application.extend_fields.get("post_action"):
            _new_controller["post_action"] = os.path.join(
                real_home, application.extend_fields["post_action"]
            )
        return _new_controller

    def update_service_connect_info(self):
        """
        更新服务链接信息
        """
        infos = {"username", "password", "username_enc", "password_enc"}
        connect_infos = {}
        for app_info in json.loads(self.service.app_install_args):
            key = app_info.get("key")
            if key in infos:
                connect_infos[f"service_{key}"] = app_info.get("default")

        if not connect_infos:
            return
        if self.service_connect_info:
            for k, v in connect_infos.items():
                if not getattr(self.service_connect_info, k) and v:
                    setattr(self.service_connect_info, k, v)
            self.service_connect_info.save()
            return
        conn_obj, _ = ServiceConnectInfo.objects.get_or_create(
            service_name=self.service.app_name,
            **connect_infos
        )
        self.service_connect_info = conn_obj

    @classmethod
    def update_dependence(cls, service_dependence, app_dependence):
        # 暂不考虑服务依赖减少
        if not app_dependence:
            return []
        dependence_dict = {}
        dependents = json.loads(service_dependence or '[]')
        for dependence in dependents:
            dependence_dict[dependence.get("name")] = dependence
        for _dependence in app_dependence:
            service_name = _dependence.get("name")
            if service_name not in dependence_dict:
                service = Service.objects.filter(
                    service__app_name=service_name
                ).first()
                if not service:
                    raise GeneralError(f"缺少依赖服务{service_name}！")
                _dict = {
                    "name": service_name,
                    "cluster_name": None,
                    "instance_name": None
                }
                if service.cluster:
                    _dict["cluster_name"] = service.cluster.cluster_name
                else:
                    _dict["instance_name"] = service.service_instance_name
                dependents.append(_dict)
        return dependents

    def update_application(self, application, success, install_folder):
        """
        更新服务信息
        :param application: 服务目标app
        :param success: 是否成功（用于更新服务状态）
        :param install_folder: 安装目录（用于更新服务命令）
        :return: self
        """
        self.service = application
        self.service_port = json.dumps(
            self.update_port(json.loads(application.app_port or '[]'))
        )
        self.service_dependence = json.dumps(
            self.update_dependence(
                self.service_dependence,
                json.loads(application.app_dependence or '[]')
            )
        )
        self.service_controllers = self.update_controllers(
            application, install_folder)
        if success:
            self.service_status = self.SERVICE_STATUS_NORMAL
        else:
            self.service_status = self.SERVICE_STATUS_UNKNOWN
        self.update_service_connect_info()
        self.save()
        return self


class ServiceHistory(models.Model):
    """ 服务操作记录表 """

    objects = None
    username = models.CharField(
        "操作用户", max_length=128, help_text="操作用户")
    description = models.CharField(
        "用户行为描述", max_length=1024, help_text="用户行为描述")
    # success or failed
    result = models.CharField(
        "操作结果", max_length=1024, default="success", help_text="操作结果")
    created = models.DateTimeField(
        '发生时间', null=True, auto_now_add=True, help_text='发生时间')
    service = models.ForeignKey(
        Service, null=True, on_delete=models.SET_NULL, verbose_name="服务")

    class Meta:
        """ 元数据 """
        db_table = "omp_service_operate_log"
        verbose_name = verbose_name_plural = "服务操作记录"
        ordering = ("-created",)

    @classmethod
    def create_history(cls, service, operation_obj=None, **kwargs):
        """
        创建服务操作记录
        :param service: 被操作的服务
        :param operation_obj: 操作对象：UpgradeDetail、RollbackDetail
        :param kwargs: 记录参数，在无操作对象情况下传
        :return: obj
        """
        if operation_obj:
            operation_kwargs = operation_obj.get_service_history()
            kwargs.update(operation_kwargs)
        service_history = cls.objects.create(
            service=service,
            **kwargs
        )
        return service_history
