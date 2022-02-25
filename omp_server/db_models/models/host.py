from django.db import models

from db_models.mixins import TimeStampMixin, DeleteMixin
from .env import Env


class Host(TimeStampMixin, DeleteMixin):
    """ 主机表 """

    AGENT_RUNNING = 0
    AGENT_RESTART = 1
    AGENT_START_ERROR = 2
    AGENT_DEPLOY_ING = 3
    AGENT_DEPLOY_ERROR = 4
    AGENT_STATUS_CHOICES = (
        (AGENT_RUNNING, "正常"),
        (AGENT_RESTART, "重启中"),
        (AGENT_START_ERROR, "启动失败"),
        (AGENT_DEPLOY_ING, "部署中"),
        (AGENT_DEPLOY_ERROR, "部署失败")
    )

    INIT_SUCCESS = 0
    INIT_NOT_EXECUTED = 1
    INIT_EXECUTING = 2
    INIT_FAILED = 3
    INIT_STATUS_CHOICES = (
        (INIT_SUCCESS, "成功"),
        (INIT_NOT_EXECUTED, "未执行"),
        (INIT_EXECUTING, "执行中"),
        (INIT_FAILED, "失败")
    )
    NTPDATE_INSTALL_SUCCESS = 0
    NTPDATE_NOT_INSTALL = 1
    NTPDATE_INSTALLING = 2
    NTPDATE_INSTALL_FAILED = 3
    NTPDATE_STATUS_CHOICES = (
        (NTPDATE_INSTALL_SUCCESS, "执行成功"),
        (NTPDATE_NOT_INSTALL, "未执行"),
        (NTPDATE_INSTALLING, "执行中"),
        (NTPDATE_INSTALL_FAILED, "执行失败")
    )

    objects = None
    instance_name = models.CharField(
        "实例名", max_length=64, help_text="实例名", unique=True)
    ip = models.GenericIPAddressField(
        "IP地址", help_text="IP地址", unique=True)
    port = models.IntegerField(
        "SSH端口", default=22, help_text="SSH端口")
    username = models.CharField(
        "SSH登录用户名", max_length=256, help_text="SSH登录用户名")
    password = models.CharField(
        "SSH登录密码", max_length=256, help_text="SSH登录密码")
    data_folder = models.CharField(
        "数据分区", max_length=256, default="/data", help_text="数据分区")
    service_num = models.IntegerField(
        "服务个数", default=0, help_text="服务个数")
    alert_num = models.IntegerField(
        "告警次数", default=0, help_text="告警次数")
    operate_system = models.CharField(
        "操作系统", max_length=128, help_text="操作系统")
    host_name = models.CharField(
        "主机名", max_length=64,
        blank=True, null=True, help_text="主机名")
    memory = models.IntegerField(
        "内存", blank=True, null=True, help_text="内存")
    cpu = models.IntegerField(
        "CPU", blank=True, null=True, help_text="CPU")
    disk = models.JSONField(
        "磁盘", blank=True, null=True, help_text="磁盘")
    host_agent = models.CharField(
        "主机Agent状态", max_length=16, help_text="主机Agent状态",
        choices=AGENT_STATUS_CHOICES, default=AGENT_DEPLOY_ING)
    monitor_agent = models.CharField(
        "监控Agent状态", max_length=16, help_text="监控Agent状态",
        choices=AGENT_STATUS_CHOICES, default=AGENT_DEPLOY_ING)
    host_agent_error = models.CharField(
        "主机Agent异常信息", max_length=256,
        blank=True, null=True, help_text="主机Agent异常信息")
    monitor_agent_error = models.CharField(
        "监控Agent异常信息", max_length=256,
        blank=True, null=True, help_text="监控Agent异常信息")
    is_maintenance = models.BooleanField(
        "维护模式", default=False, help_text="维护模式")
    agent_dir = models.CharField(
        "Agent安装目录", max_length=256, default="/data", help_text="Agent安装目录")
    env = models.ForeignKey(
        Env, null=True, on_delete=models.SET_NULL,
        verbose_name="环境", help_text="环境")
    init_status = models.CharField(
        "主机初始化状态", max_length=16, help_text="主机初始化状态",
        choices=INIT_STATUS_CHOICES, default=INIT_NOT_EXECUTED)
    use_ntpd = models.BooleanField("是否开启时间同步服务", default=False)
    ntpd_server = models.GenericIPAddressField("时间同步服务器地址", default="127.0.0.1")
    ntpdate_install_status = models.CharField(
        "安装ntpdate状态", max_length=16, choices=NTPDATE_STATUS_CHOICES, default=NTPDATE_NOT_INSTALL
    )

    class Meta:
        """ 元数据 """
        db_table = "omp_host"
        verbose_name = verbose_name_plural = "主机"
        ordering = ("-created",)


class HostOperateLog(models.Model):
    """ 主机操作记录表 """

    objects = None
    username = models.CharField(
        "操作用户", max_length=128, help_text="操作用户")
    description = models.CharField(
        "用户行为描述", max_length=1024, help_text="用户行为描述")
    result = models.CharField(
        "操作结果", max_length=1024, default="success", help_text="操作结果")
    created = models.DateTimeField(
        '发生时间', null=True, auto_now_add=True, help_text='发生时间')
    host = models.ForeignKey(
        Host, null=True, on_delete=models.SET_NULL, verbose_name="主机")

    class Meta:
        """ 元数据 """
        db_table = "omp_host_operate_log"
        verbose_name = verbose_name_plural = "主机操作记录"
        ordering = ("-created",)
