"""
omp使用的models集合
"""

from django.db import models
from django.contrib.auth.models import AbstractUser


class UserProfile(AbstractUser):
    """
    自定义用户表
    """

    class Meta:
        """元数据信息"""
        verbose_name = u"用户信息"
        db_table = "omp_user_profile"

    def __str__(self):
        """显示用户"""
        return f"用户: {self.username}"


class OperateLog(models.Model):
    """用户操作记录表"""
    objects = None
    username = models.CharField(max_length=128, help_text="操作用户")
    request_ip = models.GenericIPAddressField(
        blank=True, null=True, help_text="请求来自ip")
    request_method = models.CharField(max_length=32, help_text="请求方法")
    request_url = models.CharField(max_length=256, help_text="用户访问的URL")
    description = models.CharField(max_length=256, help_text="用户行为描述")
    response_code = models.IntegerField(default=0, help_text="请求成功或失败标志")
    request_result = models.CharField(
        max_length=1024, default="success", help_text="请求结果")
    create_time = models.DateTimeField(auto_now_add=True, help_text="用户操作发生时间")

    class Meta:
        """元数据"""
        verbose_name = u"用户操作记录"
        db_table = "omp_operate_log"


HOST_STATUS = (
    (0, "正常"),
    (1, "纳管主机中"),
    (2, "主机Agent异常"),
    (3, "监控Agent异常"),
    (4, "纳管主机失败"),
    (5, "维护"),
)


class Hosts(models.Model):
    """主机表"""
    objects = None
    ip = models.GenericIPAddressField(help_text="主机ip地址")
    hostname = models.CharField(
        max_length=64, blank=True, null=True, help_text="主机名")
    port = models.IntegerField(blank=True, null=True, help_text="主机SSH端口")
    username = models.CharField(
        max_length=256, blank=True, null=True, help_text="SSH登录用户名")
    password = models.CharField(
        max_length=256, blank=True, null=True, help_text="SSH登录密码")
    status = models.IntegerField(choices=HOST_STATUS, help_text="主机状态")
    service_num = models.IntegerField(
        blank=True, null=True, help_text="主机上的服务个数")
    alert_num = models.IntegerField(
        blank=True, null=True, help_text="该主机的告警次数")
    data_folder = models.CharField(
        max_length=128, default="/data", help_text="数据目录")
    idc = models.CharField(max_length=128, blank=True,
                           null=True, help_text="IDC机房")
    operate_system = models.CharField(
        max_length=128, blank=True, null=True, help_text="主机操作系统")
    memory = models.IntegerField(blank=True, null=True, help_text="主机内存")
    cpu = models.IntegerField(blank=True, null=True, help_text="主机cpu")
    disk = models.JSONField(blank=True, null=True, help_text="主机磁盘信息")
