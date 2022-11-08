from django.contrib.auth.models import AbstractUser
from django.db import models


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


class UserLoginLog(models.Model):
    """用户登陆记录"""
    objects = None
    username = models.CharField(max_length=128, verbose_name="Username")
    login_time = models.DateTimeField(
        blank=True, null=True, verbose_name="Login time")
    ip = models.CharField(max_length=32, null=True,
                          blank=True, verbose_name="Login ip")
    role = models.CharField(
        max_length=128, verbose_name="role ", null=True, blank=True)
    request_result = models.CharField(
        "请求结果", max_length=512,
        null=True, blank=True, help_text="请求结果")

    class Meta:
        db_table = "omp_login_log"
        verbose_name = verbose_name_plural = "用户登陆记录"
