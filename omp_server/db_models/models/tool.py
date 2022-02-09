# -*- coding: utf-8 -*-
# Project: tools
# Author: jon.liu@yunzhihui.com
# Create time: 2022-02-08 16:04
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
实用工具数据库表结构
"""

from django.db import models

from db_models.mixins import TimeStampMixin


class ToolInfo(TimeStampMixin):
    """ 实用工具基本信息记录表 """

    objects = None

    KIND_MANAGE = 0
    KIND_CHECK = 1
    KIND_SECURE = 2
    KIND_OTHER = 3
    TOOL_KIND_CHOICES = (
        (KIND_MANAGE, "管理工具"),
        (KIND_CHECK, "检查工具"),
        (KIND_SECURE, "安全工具"),
        (KIND_OTHER, "其他工具")
    )

    SCRIPT_TYPE_PYTHON3 = 0
    SCRIPT_TYPE_SHELL = 1
    SCRIPT_TYPE_CHOICES = (
        (SCRIPT_TYPE_PYTHON3, "python3"),
        (SCRIPT_TYPE_SHELL, "shell")
    )

    TARGET_TYPE_HOST = 0
    TARGET_TYPE_SERVICE = 1
    TARGET_TYPE_CHOICES = (
        (TARGET_TYPE_HOST, "主机"),
        (TARGET_TYPE_SERVICE, "服务")
    )

    OUTPUT_TERMINAL = 0
    OUTPUT_FILE = 1
    OUTPUT_TYPE_CHOICES = (
        (OUTPUT_TERMINAL, "终端输出"),
        (OUTPUT_FILE, "文件输出")
    )

    name = models.CharField(
        max_length=128, null=False,
        blank=False, help_text="实用工具名称")
    kind = models.IntegerField(
        "实用工具分类", choices=TOOL_KIND_CHOICES,
        default=0, help_text="实用工具分类")
    script_type = models.IntegerField(
        "脚本类型", choices=SCRIPT_TYPE_CHOICES,
        default=0, help_text="脚本类型")
    # 脚本执行的目标对象，如果是服务类型
    # 在执行时需要获取其username、password作为参数传入脚本
    target_type = models.IntegerField(
        "脚本执行的目标对象", choices=TARGET_TYPE_CHOICES,
        default=0, help_text="脚本执行的目标对象")
    # 当执行对象是服务时，需要存储是针对哪个服务
    target_service = models.CharField(
        "目标服务名称", max_length=128,
        null=True, blank=True, help_text="目标服务名称")
    # 存储脚本路径，如kafka.py
    script_path = models.CharField(
        "脚本相对路径", max_length=128,
        null=False, blank=False, help_text="脚本相对路径")
    # 存储readme的绝对路径，在给前端显示时，直接读取该路径中的内容
    readme_path = models.CharField(
        "readme绝对路径", max_length=512,
        null=True, blank=True, help_text="readme绝对路径")
    # 如果脚本需要模板文件，那么该模板文件的相对路径需要存储到下面字段中
    # 此字段存储列表类型数据
    template_filepath = models.JSONField(
        "模板文件路径", null=True, blank=True, help_text="模板文件路径")
    # 存储脚本执行参数，存储列表类型数据
    # 在入库时需要对每个参数的类型进行校验（前端展示效果）
    script_args = models.JSONField(
        "脚本执行参数", null=True, blank=True, help_text="脚本执行参数")
    # 脚本输出的类型，终端/文件
    output = models.IntegerField(
        "脚本的输出类型", choices=TARGET_TYPE_CHOICES,
        default=0, help_text="脚本的输出类型")
    # 存储实用工具目录路径，如/data/omp/package_hub/tools/kafka-{package_md5}
    tool_folder_path = models.CharField(
        "实用工具目录绝对路径", max_length=128,
        null=False, blank=False, help_text="实用工具目录绝对路径")
    # 原始脚本包MD5值，预留字段
    source_package_md5 = models.CharField(
        "源码包md5值", max_length=32,
        blank=True, null=True, help_text="源码包md5值")
    desc = models.TextField("描述信息", help_text="描述信息")

    class Meta:
        """元数据"""
        db_table = "omp_tool_info"
        verbose_name = verbose_name_plural = "实用工具基本信息表"


class ToolExecuteMainHistory(models.Model):
    """ 实用工具执行记录 """

    objects = None

    STATUS_READY = 0
    STATUS_RUNNING = 1
    STATUS_SUCCESS = 2
    STATUS_FAILED = 3
    STATUS_TYPE_CHOICES = (
        (STATUS_READY, "待执行"),
        (STATUS_RUNNING, "执行中"),
        (STATUS_SUCCESS, "执行成功"),
        (STATUS_FAILED, "执行失败"),
    )

    tool = models.ForeignKey(
        ToolInfo, on_delete=models.CASCADE, help_text="实用工具对象")
    operator = models.CharField(
        "操作人", max_length=128, null=True, blank=True, help_text="操作人")
    status = models.IntegerField(
        "main执行状态", choices=STATUS_TYPE_CHOICES,
        default=0, help_text="main执行状态")
    start_time = models.DateTimeField(
        "开始时间", null=True, auto_now_add=True, help_text="开始时间")
    end_time = models.DateTimeField(
        "结束时间", null=True, auto_now=True, help_text="结束时间")

    class Meta:
        """元数据"""
        db_table = "omp_tool_execute_main_history"
        verbose_name = verbose_name_plural = "实用工具执行记录"


class ToolExecuteDetailHistory(TimeStampMixin):
    """ 实用工具执行详情记录 """

    objects = None

    STATUS_READY = 0
    STATUS_RUNNING = 1
    STATUS_SUCCESS = 2
    STATUS_FAILED = 3
    STATUS_TYPE_CHOICES = (
        (STATUS_READY, "待执行"),
        (STATUS_RUNNING, "执行中"),
        (STATUS_SUCCESS, "执行成功"),
        (STATUS_FAILED, "执行失败"),
    )

    main_history = models.ForeignKey(
        ToolExecuteMainHistory, on_delete=models.CASCADE,
        help_text="实用工具对象")
    # 脚本需要在某台主机上执行，此处代表该主机的ip地址
    target_ip = models.CharField(
        "目标IP地址", max_length=64,
        null=False, blank=False, help_text="目标IP地址")
    status = models.IntegerField(
        "detail执行状态", choices=STATUS_TYPE_CHOICES,
        default=0, help_text="detail执行状态")
    # 脚本执行的参数详情信息
    execute_args = models.JSONField("执行参数信息", help_text="执行参数信息")
    execute_log = models.TextField("执行日志", help_text="执行日志")
    # 仅当脚本输出类型为文件时才输出此内容
    output_filepath = models.CharField(
        "脚本输出文件本机存储路径", max_length=512,
        null=True, blank=True, help_text="脚本输出文件本机存储路径")

    class Meta:
        """元数据"""
        db_table = "omp_tool_execute_detail_history"
        verbose_name = verbose_name_plural = "实用工具执行详情表"
