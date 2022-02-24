# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author:' Lingyang.guo'
# CreateDate: 14:08
import os

from django.db import models

from db_models.mixins import TimeStampMixin


class CustomScript(TimeStampMixin):
    """
    自定义脚本
    """
    objects = None
    script_name = models.CharField(
        "脚本名称", max_length=32, null=False, help_text="自定义脚本名称")
    script_content = models.TextField(
        "脚本内容", max_length=10000, null=False, help_text="脚本内容")
    metrics = models.JSONField("指标列表", null=False, help_text="指标列表")
    metric_num = models.IntegerField(
        "metric数量", help_text="metric数量", null=True)
    scrape_interval = models.IntegerField(
        "探测周期", default=60, help_text="prometheus探测周期")
    enabled = models.BooleanField("是否启用", default=1, help_text="1位启用，0为禁用")
    description = models.TextField(
        "脚本描述", max_length=1024, null=False, help_text="脚本描述")
    bound_hosts = models.JSONField("已下发主机列表", help_text="已下发主机列表")

    def valid_upload_file(self, *args, **kwargs):  # NOQA
        return "package_hub/custom_scripts"

    def upload_file_url(self, file_name, **kwargs):  # NOQA
        return os.path.join("package_hub/custom_scripts", file_name)

    class Meta:
        """元数据"""
        db_table = "omp_custom_script"
        verbose_name = verbose_name_plural = "自定义脚本"
