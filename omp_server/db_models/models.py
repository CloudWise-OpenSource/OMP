"""
omp使用的models集合
"""

from django.db import models
from django.contrib.auth.models import AbstractUser

from db_models.mixins import (
    DeleteMixin,
    TimeStampMixin,
)


class UserProfile(AbstractUser):
    """ 自定义用户表 """

    class Meta:
        """ 元数据 """
        db_table = "omp_user_profile"
        verbose_name = verbose_name_plural = "用户"

    def __str__(self):
        """ 显示用户 """
        return f"用户: {self.username}"


class OperateLog(models.Model):
    """ 用户操作记录表 """

    objects = None
    username = models.CharField(
        "操作用户", max_length=128, help_text="操作用户")
    request_method = models.CharField(
        "请求方法", max_length=32, help_text="请求方法")
    request_ip = models.GenericIPAddressField(
        "请求源IP", blank=True, null=True, help_text="请求源IP")
    request_url = models.CharField(
        "用户目标URL", max_length=256, help_text="用户目标URL")
    description = models.CharField(
        "用户行为描述", max_length=256, help_text="用户行为描述")
    response_code = models.IntegerField(
        "响应状态码", default=0, help_text="响应状态码")
    request_result = models.TextField(
        "请求结果", default="success", help_text="请求结果")
    create_time = models.DateTimeField(
        "操作发生时间", auto_now_add=True, help_text="操作发生时间")

    class Meta:
        """ 元数据 """
        db_table = "omp_user_operate_log"
        verbose_name = verbose_name_plural = "用户操作记录"


class Env(models.Model):
    """ 环境表 """

    name = models.CharField(
        "环境名称", max_length=256, help_text="环境名称")
    created = models.DateTimeField(
        '创建时间', null=True, auto_now_add=True, help_text='创建时间')

    class Meta:
        db_table = "omp_env"
        verbose_name = verbose_name_plural = "环境"


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

    objects = None
    instance_name = models.CharField(
        "实例名", max_length=64, help_text="实例名")
    ip = models.GenericIPAddressField(
        "IP地址", help_text="IP地址")
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
    env = models.ForeignKey(
        Env, null=True, on_delete=models.SET_NULL,
        verbose_name="环境", help_text="环境")

    class Meta:
        """ 元数据 """
        db_table = "omp_host"
        verbose_name = verbose_name_plural = "主机"
        ordering = ("-created",)


class HostOperateLog(models.Model):
    """ 主机操作记录表 """

    # objects = None
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


class MonitorUrl(models.Model):
    """ 用户操作记录表 """

    objects = None
    name = models.CharField(
        "监控类别", max_length=32, unique=True, help_text="监控类别")
    monitor_url = models.CharField(
        "请求地址", max_length=128, help_text="请求地址")

    class Meta:
        """ 元数据 """
        db_table = "omp_promemonitor_url"
        verbose_name = verbose_name_plural = "监控地址记录"


class Alert(models.Model):
    """告警数据表"""
    is_read = models.IntegerField(
        "已读", default=0, help_text="此消息是否已读，0-未读；1-已读")
    alert_type = models.CharField(
        "告警类型", max_length=32, default="", help_text="告警类型，主机host，服务service")
    alert_host_ip = models.CharField(
        "告警主机ip", max_length=64, default="", help_text="告警来源主机ip")
    alert_host_instance_name = models.CharField(
        "告警主机实例名称", max_length=256, default="", help_text="告警主机实例名称")
    alert_service_name = models.CharField(
        "告警服务名称", max_length=128, default="", help_text="服务类告警中的服务名称")
    alert_service_instance_name = models.CharField(
        "告警服务实例名称", max_length=128, default="", help_text="告警服务实例名称")
    alert_service_type = models.CharField(
        "告警服务类型", max_length=128, default="", help_text="服务所属类型")
    alert_level = models.CharField(
        "告警级别", max_length=1024, default="", help_text="告警级别")
    alert_describe = models.CharField(
        "告警描述", max_length=1024, default="", help_text="告警描述")
    alert_receiver = models.CharField(
        "告警接收人", max_length=256, default="", help_text="告警接收人")
    alert_resolve = models.CharField(
        "告警解决方案", max_length=1024, default="", help_text="告警解决方案")
    alert_time = models.DateTimeField(
        "告警发生时间", help_text="告警发生时间")
    create_time = models.DateTimeField(
        "告警信息入库时间", auto_now_add=True, help_text="告警信息入库时间")
    monitor_path = models.CharField(
        "跳转监控路径", max_length=2048, blank=True, null=True, help_text="跳转grafana路由")
    monitor_log = models.CharField(
        "跳转监控日志路径", max_length=2048, blank=True, null=True, help_text="跳转grafana日志页面路由")
    fingerprint = models.CharField(
        "告警的唯一标识", max_length=1024, blank=True, null=True, help_text="告警的唯一标识")
    env = models.ForeignKey(
        Env, null=True, on_delete=models.SET_NULL,
        verbose_name="环境", help_text="环境")

    class Meta:
        """元数据"""
        db_table = 'omp_alert'
        verbose_name = verbose_name_plural = "告警记录"


class Maintain(models.Model):
    """
    维护记录表
    """
    objects = None

    matcher_name = models.CharField(
        "匹配标签", max_length=1024, null=False, help_text="匹配标签")
    matcher_value = models.CharField(
        "匹配值", max_length=1024, null=False, help_text="匹配值")
    maintain_id = models.CharField(
        "维护唯一标识", max_length=1024, null=False, help_text="维护唯一标识")

    class Meta:
        """元数据"""
        db_table = 'omp_maintain'
        verbose_name = verbose_name_plural = "维护记录"
