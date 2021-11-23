"""
omp使用的models集合
"""
import logging
import os

import requests
from django.db import models
from django.contrib.auth.models import AbstractUser
from ruamel import yaml

from db_models.mixins import (
    DeleteMixin,
    TimeStampMixin,
)

logger = logging.getLogger('server')


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

    objects = None
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
    agent_dir = models.CharField(
        "Agent安装目录", max_length=256, default="/data", help_text="Agent安装目录")
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

    objects = None
    is_read = models.IntegerField(
        "已读", default=0, help_text="此消息是否已读，0-未读；1-已读")
    alert_type = models.CharField(
        "告警类型", max_length=32, default="", help_text="告警类型，主机host，服务service")
    alert_host_ip = models.CharField(
        "告警主机ip", max_length=64, default="", help_text="告警来源主机ip")
    alert_service_name = models.CharField(
        "告警服务名称", max_length=128, default="", help_text="服务类告警中的服务名称")
    alert_instance_name = models.CharField(
        "告警实例名称", max_length=128, default="", help_text="告警实例名称")
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


class Labels(models.Model):
    """ 应用&产品标签表 """

    LABEL_TYPE_COMPONENT = 0
    LABEL_TYPE_APPLICATION = 1
    LABELS_CHOICES = (
        (LABEL_TYPE_COMPONENT, "组件"),
        (LABEL_TYPE_APPLICATION, "应用")
    )
    label_name = models.CharField(
        "标签名称", max_length=16,
        null=False, blank=False, help_text="标签名称")
    label_type = models.IntegerField(
        "标签类型", choices=LABELS_CHOICES,
        default=0, help_text="标签类型")

    class Meta:
        """元数据"""
        db_table = 'omp_labels'
        verbose_name = verbose_name_plural = "应用产品标签表"


class UploadPackageHistory(TimeStampMixin, DeleteMixin):
    """ 上传安装包记录表，存储产品包及服务包 """

    objects = None
    PACKAGE_STATUS_SUCCESS = 0
    PACKAGE_STATUS_FAILED = 1
    PACKAGE_STATUS_PARSING = 2
    PACKAGE_STATUS_PUBLISH_SUCCESS = 3
    PACKAGE_STATUS_PUBLISH_FAILED = 4
    PACKAGE_STATUS_PUBLISHING = 5
    PACKAGE_STATUS_CHOICES = (
        (PACKAGE_STATUS_SUCCESS, "成功"),
        (PACKAGE_STATUS_FAILED, "失败"),
        (PACKAGE_STATUS_PARSING, "解析中"),
        (PACKAGE_STATUS_PUBLISH_SUCCESS, "发布成功"),
        (PACKAGE_STATUS_PUBLISH_FAILED, "发布失败"),
        (PACKAGE_STATUS_PUBLISHING, "发布中"),
    )
    operation_uuid = models.CharField(
        "唯一操作uuid", max_length=64,
        null=False, blank=False, help_text="唯一操作uuid")
    operation_user = models.CharField(
        "操作用户", max_length=64,
        null=True, blank=True, help_text="操作用户")
    package_name = models.CharField(
        "安装包名称", max_length=256,
        null=False, blank=False, help_text="安装包名称")
    package_md5 = models.CharField(
        "安装包MD5值", max_length=64,
        null=False, blank=False, help_text="安装包MD5值")
    # 安装包相对路径，相对于package_hub
    package_path = models.CharField(
        "安装包路径", max_length=512,
        null=False, blank=False, help_text="安装包路径")
    package_status = models.IntegerField(
        "安装包状态", choices=PACKAGE_STATUS_CHOICES,
        default=2, help_text="安装包状态")
    error_msg = models.CharField(
        "错误消息", max_length=1024,
        null=True, blank=True, help_text="错误消息")
    package_parent = models.ForeignKey(
        to="self", null=True, blank=True,
        on_delete=models.SET_NULL, help_text="父级包")

    class Meta:
        """元数据"""
        db_table = 'omp_upload_package_history'
        verbose_name = verbose_name_plural = "上传安装包记录"


class ProductHub(TimeStampMixin):
    """ 存储产品级别模型类 (应用) """
    # 使用is_release标识此条数据是否已发布，是否可用
    objects = None
    is_release = models.BooleanField(
        "是否发布", default=False, help_text="是否发布")
    pro_name = models.CharField(
        "产品名称", max_length=256,
        null=False, blank=False, help_text="产品名称")
    pro_version = models.CharField(
        "产品版本", max_length=256,
        null=False, blank=False, help_text="产品版本")
    pro_labels = models.ManyToManyField(to=Labels, help_text="所属标签")
    pro_description = models.CharField(
        "产品描述", max_length=2048,
        null=True, blank=True, help_text="产品描述")
    # 以下字段在入库时使用json.dumps方法处理，读取时使用json.loads方法反向解析
    # 产品依赖默认向下兼容
    # ["cmdb", "douc"]
    pro_dependence = models.TextField(
        "产品依赖", null=True, blank=True, help_text="产品依赖")
    # [{"name": "cmdbServer", "version": "1.1.0"}]
    pro_services = models.TextField(
        "服务列表", null=True, blank=True, help_text="服务列表")
    # 关联的安装包
    pro_package = models.ForeignKey(
        UploadPackageHistory, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name="安装包", help_text="安装包")
    # 产品图标读取svg数据进行渲染pro_name.svg
    pro_logo = models.TextField(
        "产品图标", null=True, blank=True, help_text="产品图标")
    # 冗余字段，用于存储未定义的其他产品相关数据
    extend_fields = models.JSONField(
        "冗余字段", null=True, blank=True, help_text="冗余字段")

    class Meta:
        """元数据"""
        db_table = 'omp_product'
        verbose_name = verbose_name_plural = "应用商店产品"


class ApplicationHub(TimeStampMixin):
    """ 服务级别模型类 (组件) """
    objects = None
    APP_TYPE_COMPONENT = 0
    APP_TYPE_SERVICE = 1
    APP_TYPE_CHOICES = (
        (APP_TYPE_COMPONENT, "组件"),
        (APP_TYPE_SERVICE, "服务")
    )
    is_release = models.BooleanField(
        "是否发布", default=False, help_text="是否发布")
    app_type = models.IntegerField(
        "应用类型", choices=APP_TYPE_CHOICES,
        default=0, help_text="应用类型")
    app_name = models.CharField(
        "应用名称", max_length=256,
        null=False, blank=False, help_text="应用名称")
    app_labels = models.ManyToManyField(to=Labels, help_text="所属标签")
    app_version = models.CharField(
        "应用版本", max_length=256,
        null=False, blank=False, help_text="应用版本")
    app_description = models.CharField(
        "应用描述", max_length=2048,
        null=True, blank=True, help_text="应用描述")
    # 应用端口使用TextField字段进行存储
    # 在入库时使用json.dumps方法处理，读取时使用json.loads方法反向解析
    # 存储数据格式为[{"default": 18080, "key": "http_port", "name": "服务端口"}]
    app_port = models.TextField(
        "应用端口", null=True, blank=True, help_text="应用端口")
    # 以下字段使用方法同应用端口
    # 服务依赖默认向下兼容
    # [{"name": "mysql", "version": "5.7"}]
    app_dependence = models.TextField(
        "应用依赖", null=True, blank=True, help_text="应用依赖")
    # [{"name": "安装目录", "key": "base_dir", "default": "{data_path}/abc"}]
    app_install_args = models.TextField(
        "安装参数", null=True, blank=True, help_text="安装参数")
    # {"start": "./start.sh", "stop": "./stop.sh"}
    app_controllers = models.TextField(
        "应用控制脚本", null=True, blank=True, help_text="应用控制脚本")
    # 关联的安装包
    app_package = models.ForeignKey(
        UploadPackageHistory, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name="安装包", help_text="安装包")
    product = models.ForeignKey(
        ProductHub, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name="所属产品", help_text="所属产品")
    # 应用图标读取svg数据进行渲染app_name.svg
    app_logo = models.TextField(
        "应用图标", null=True, blank=True, help_text="应用图标")
    # 冗余字段，用于存储未定义的其他服务相关数据
    extend_fields = models.JSONField(
        "冗余字段", null=True, blank=True, help_text="冗余字段")
    # 解析服务数据后，如果服务为jdk、python等，则其为基础数据
    is_base_env = models.BooleanField(
        "是否为基础环境", default=False, help_text="是否为基础环境")
    app_monitor = models.JSONField(
        "监控使用字段", null=True, blank=True, help_text="监控使用字段")

    class Meta:
        """元数据"""
        db_table = 'omp_application'
        verbose_name = verbose_name_plural = "应用商店服务"
        # 服务、组件名称和版本形成联合唯一索引，不允许重复
        unique_together = ("app_name", "app_version")


class GrafanaMainPage(models.Model):
    """Grafana 主面板信息表"""
    instance_name = models.CharField(
        "实例名字", max_length=32, unique=True, help_text="信息面板实例名字")
    instance_url = models.CharField(
        "实例地址", max_length=255, unique=True, help_text="实例文根地址")

    class Meta:
        """ 元数据 """
        db_table = "omp_grafana_url"
        verbose_name = verbose_name_plural = "grafana面板记录"


class InspectionHistory(models.Model):
    """巡检记录历史表"""
    objects = None
    id = models.AutoField(primary_key=True, unique=True, help_text="自增主键")
    inspection_name = models.CharField(
        max_length=256, null=False, blank=False, help_text="报告名称:巡检类型名称")
    inspection_type = models.CharField(
        max_length=32, default="service", help_text="巡检类型，service、host、deep")
    inspection_status = models.IntegerField(
        default=0, help_text="巡检状态:1-进行中；2-成功；3-失败")
    execute_type = models.CharField(
        max_length=32, null=False, blank=False, default="man",
        help_text="执行方式: 手动-man；定时：auto")
    inspection_operator = models.CharField(
        max_length=16, null=False, blank=False, help_text="操作人员-当前登录人")
    hosts = models.JSONField(
        null=True, blank=True, help_text="巡检主机:['10.0.9.158']")
    services = models.JSONField(
        null=True, blank=True, help_text="巡检组件: [8,9]")
    start_time = models.DateTimeField(auto_now_add=True, help_text="开始时间")
    end_time = models.DateTimeField(null=True, help_text="结束时间，后端后补")
    duration = models.IntegerField(default=0, help_text="巡检用时：单位s，后端后补")
    env = models.ForeignKey(
        Env, null=True, on_delete=models.SET_NULL, verbose_name="当前环境id",
        help_text="当前环境id")
    NOT_SEND = 3
    SUCCESS = 1
    ING = 2
    FAIL = 0
    SEND_RESULT_CHOICES = (
        ("发送成功", SUCCESS),
        ("发送中", ING),
        ("发送失败", FAIL),
        ("未发送", NOT_SEND)
    )
    send_email_result = models.IntegerField(
        "邮件推送状态", choices=SEND_RESULT_CHOICES, default=NOT_SEND)

    class Meta:
        db_table = 'inspection_history'
        verbose_name = verbose_name_plural = "巡检记录历史表"
        ordering = ("-start_time",)

    def send_email_content(self):
        return f"""
                巡检任务名称：{self.inspection_name}\n
                巡检时间：{self.start_time.strftime("%Y-%m-%d %H:%M:%S")}
                """


class InspectionCrontab(models.Model):
    """巡检任务 定时配置表"""
    j_type = (
        (0, "深度分析"),
        (1, "主机巡检"),
        (2, "组件巡检")
    )

    objects = None
    id = models.AutoField(primary_key=True, unique=True, help_text="自增主键")
    job_type = models.IntegerField(
        default=0, choices=j_type, help_text="任务类型：0-深度分析 1-主机巡检 2-组建巡检")
    job_name = models.CharField(
        max_length=128, null=False, blank=False, help_text="任务名称")
    is_start_crontab = models.IntegerField(
        default=0, help_text="是否开启定时任务：0-开启，1-关闭")
    crontab_detail = models.JSONField(help_text="定时任务详情")
    create_date = models.DateTimeField(auto_now_add=True, help_text="创建时间")
    update_time = models.DateTimeField(auto_now=True, help_text="修改时间")
    env = models.ForeignKey(
        Env, null=True, on_delete=models.SET_NULL, verbose_name="环境",
        help_text="环境")

    class Meta:
        """表名等信息"""
        db_table = 'inspection_crontab'
        verbose_name = verbose_name_plural = "巡检任务 定时配置表"
        ordering = ("id",)


class InspectionReport(models.Model):
    """巡检 报告"""
    objects = None
    id = models.AutoField(primary_key=True, unique=True, help_text="自增主键")
    file_name = models.CharField(
        max_length=128, null=True, blank=True, help_text="导出文件名")
    scan_info = models.JSONField(null=True, blank=True, help_text="扫描统计")
    scan_result = models.JSONField(null=True, blank=True, help_text="分析结果")
    risk_data = models.JSONField(null=True, blank=True, help_text="风险指标")
    host_data = models.JSONField(null=True, blank=True, help_text="主机列表")
    serv_plan = models.JSONField(null=True, blank=True, help_text="服务平面图")
    serv_data = models.JSONField(null=True, blank=True, help_text="服务列表")
    inst_id = models.OneToOneField(
        InspectionHistory, null=True, on_delete=models.SET_NULL,
        verbose_name="巡检记录历史表", help_text="巡检记录历史表id")

    class Meta:
        """表名等信息"""
        db_table = 'inspection_report'
        verbose_name = verbose_name_plural = "巡检任务 报告数据"
        ordering = ("id",)


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


class Product(TimeStampMixin):
    """ 已安装产品表 """
    objects = None
    # 用于存储安装产品时使用的实例名称
    product_instance_name = models.CharField(
        "产品实例名称", max_length=64,
        null=True, blank=True, help_text="安装产品时输入的实例名称")
    # 所属产品的相关信息，可通过此外键查看其对应的产品仓库中的数据
    product = models.ForeignKey(
        ProductHub, null=True, blank=True,
        on_delete=models.SET_NULL, help_text="所属产品")

    class Meta:
        """元数据"""
        db_table = 'omp_product_instance'
        verbose_name = verbose_name_plural = "产品实例表"
        ordering = ("-created",)


class Service(TimeStampMixin):
    """ 服务表 """

    objects = None
    SERVICE_STATUS_NORMAL = 0
    SERVICE_STATUS_STARTING = 1
    SERVICE_STATUS_STOPPING = 2
    SERVICE_STATUS_RESTARTING = 3
    SERVICE_STATUS_STOP = 4
    SERVICE_STATUS_UNKNOWN = 5
    SERVICE_STATUS_INSTALLING = 6
    SERVICE_STATUS_INSTALL_FAILED = 7
    SERVICE_STATUS_CHOICES = (
        (SERVICE_STATUS_NORMAL, "正常"),
        (SERVICE_STATUS_STARTING, "启动中"),
        (SERVICE_STATUS_STOPPING, "停止中"),
        (SERVICE_STATUS_RESTARTING, "重启中"),
        (SERVICE_STATUS_STOP, "停止"),
        (SERVICE_STATUS_UNKNOWN, "未知"),
        (SERVICE_STATUS_INSTALLING, "安装中"),
        (SERVICE_STATUS_INSTALL_FAILED, "安装失败"),
    )

    # 是否用外键关联？
    ip = models.GenericIPAddressField(
        "服务所在主机", help_text="服务所在主机")

    service_instance_name = models.CharField(
        "服务实例名称", max_length=64,
        null=False, blank=False, help_text="服务实例名称")

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

    class Meta:
        """元数据"""
        db_table = 'omp_service'
        verbose_name = verbose_name_plural = "服务实例表"
        ordering = ("-created",)


class ServiceHistory(models.Model):
    """ 服务操作记录表 """

    objects = None
    username = models.CharField(
        "操作用户", max_length=128, help_text="操作用户")
    description = models.CharField(
        "用户行为描述", max_length=1024, help_text="用户行为描述")
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


class MainInstallHistory(TimeStampMixin):
    """ 主安装记录表 """

    objects = None
    INSTALL_STATUS_READY = 0
    INSTALL_STATUS_INSTALLING = 1
    INSTALL_STATUS_SUCCESS = 2
    INSTALL_STATUS_FAILED = 3
    INSTALL_STATUS_CHOICES = (
        (INSTALL_STATUS_READY, "待安装"),
        (INSTALL_STATUS_INSTALLING, "安装中"),
        (INSTALL_STATUS_SUCCESS, "安装成功"),
        (INSTALL_STATUS_FAILED, "安装失败"),
    )

    operation_uuid = models.CharField(
        "部署操作uuid", max_length=36,
        null=False, blank=False, help_text="部署操作uuid")
    task_id = models.CharField(
        "异步任务id", max_length=36,
        null=True, blank=True, help_text="异步任务id")
    # 直接代表整体的安装状态
    install_status = models.IntegerField(
        "安装状态", choices=INSTALL_STATUS_CHOICES,
        default=0, help_text="安装状态")
    install_args = models.JSONField(
        "主表安装信息", null=True, blank=True, help_text="主表安装信息")
    install_log = models.TextField("MAIN安装日志", help_text="MAIN安装日志")

    class Meta:
        """元数据"""
        db_table = "omp_main_install_history"
        verbose_name = verbose_name_plural = "主安装记录表"


class DetailInstallHistory(TimeStampMixin):
    """
    安装细节表，针对单服务
    在下发安装任务之前，需要对安装顺序进行排序确定
    """

    objects = None
    INSTALL_STATUS_READY = 0
    INSTALL_STATUS_INSTALLING = 1
    INSTALL_STATUS_SUCCESS = 2
    INSTALL_STATUS_FAILED = 3
    INSTALL_STEP_CHOICES = (
        (INSTALL_STATUS_READY, "待安装"),
        (INSTALL_STATUS_INSTALLING, "安装中"),
        (INSTALL_STATUS_SUCCESS, "安装成功"),
        (INSTALL_STATUS_FAILED, "安装失败"),
    )

    service = models.ForeignKey(
        Service, null=True, blank=True,
        on_delete=models.SET_NULL, help_text="关联服务对象")
    main_install_history = models.ForeignKey(
        MainInstallHistory, null=True, blank=True,
        on_delete=models.SET_NULL, help_text="关联主安装记录")
    # 单服务安装步骤:
    install_step_status = models.IntegerField(
        "安装步骤状态", choices=INSTALL_STEP_CHOICES,
        default=0, help_text="安装步骤状态")

    # 安装细节标记及日志
    send_flag = models.IntegerField(
        "发包状态", default=0,
        help_text="0-待发送 1-发送中 2-发送成功 3-发送失败")
    send_msg = models.TextField("发包日志", help_text="发包日志")
    unzip_flag = models.IntegerField(
        "解压包状态", default=0,
        help_text="0-待解压 1-解压中 2-解压成功 3-解压失败")
    unzip_msg = models.TextField("解压日志", help_text="解压日志")
    install_flag = models.IntegerField(
        "安装执行状态", default=0,
        help_text="0-待安装 1-安装中 2-安装成功 3-安装失败")
    install_msg = models.TextField("安装日志", help_text="安装日志")
    init_flag = models.IntegerField(
        "初始化执行状态", default=0,
        help_text="0-待初始化 1-初始化中 2-初始化成功 3-初始化失败")
    init_msg = models.TextField("初始化日志", help_text="初始化日志")
    start_flag = models.IntegerField(
        "启动执行状态", default=0,
        help_text="0-待启动 1-启动中 2-启动成功 3-启动失败")
    start_msg = models.TextField("启动日志", help_text="启动日志")
    install_detail_args = models.JSONField(
        "详情表安装信息", null=True, blank=True, help_text="详情表安装信息")
    post_action_flag = models.IntegerField(
        "安装后执行动作标记", default=0,
        help_text="0-待执行 1-执行中 2-执行成功 3-执行失败 4-无需执行")
    post_action_msg = models.TextField(
        "安装后执行动作日志", default="", help_text="安装后执行动作日志")

    class Meta:
        """元数据"""
        db_table = "omp_detail_install_history"
        verbose_name = verbose_name_plural = "安装记录详情表"

    def __str__(self):
        return self.service.service_instance_name + f"({self.service.ip})"


class AlertSendWaySetting(models.Model):
    used = models.BooleanField("是否启用", default=False)
    env_id = models.IntegerField("环境id", default=0)
    way_name = models.CharField("告警推送服务名称", max_length=64)
    server_url = models.TextField("告警推送服务url", default="")
    way_token = models.CharField("服务token", max_length=255, default="")
    extra_info = models.JSONField("服务其他信息", default=dict)

    class Meta:
        db_table = 'omp_alert_send_way_setting'
        verbose_name = verbose_name_plural = '告警推送通道设置'

    # 暂时屏蔽doem的配置
    # @property
    # def get_doem_init_kwargs(self):
    #     """
    #     返回告警推送服务类对象初始化参数
    #     :return:
    #     """
    #     return {"app_key": self.way_token, "server_url": self.server_url}
    #
    # @property
    # def get_doem_dict(self):
    #     return {
    #         "way_token": self.way_token,
    #         "server_url": self.server_url,
    #         "used": self.used
    #     }

    @property
    def get_email_dict(self):
        return {
            "server_url": self.server_url,
            "used": self.used
        }

    @classmethod
    def get_v1_5_email_dict(cls, env_id):
        # 临时适配1.5，email推送走alert manage
        obj = cls.objects.filter(way_name="email").first()
        kwargs = {
            "server_url": "",
            "used": False
        }
        if obj:
            kwargs.update(server_url=obj.server_url, used=obj.used)
            cls.objects.create(
                env_id=env_id,
                way_name="email",
                server_url=obj.server_url,
                used=obj.used)
        return kwargs

    def get_self_dict(self):
        # 前端展示
        return getattr(self, f"get_{self.way_name}_dict")

    # def get_func_class_obj(self):
    #     """
    #     返回告警推送服务类对象
    #     :return:
    #     """
    #     from base import base_monitor
    #     kwargs = getattr(self, f"get_{self.way_name}_init_kwargs")
    #     return getattr(
    #         base_monitor, f"SendAlertTo{self.way_name.capitalize()}Way"
    #     )(**kwargs)

    @classmethod
    def update_email_config(cls, used, user_emails):
        cls.objects.filter(
            way_name="email"
        ).update(used=used, server_url=user_emails)


class EmailSMTPSetting(models.Model):
    email_host = models.EmailField("邮箱SMTP主机地址:smtp.163.com", null=True)
    email_port = models.IntegerField("邮箱SMTP端口:465", null=True)
    email_host_user = models.CharField(
        "邮箱SMTP服务器用户名:a@163.com", max_length=128, null=True)
    email_host_password = models.CharField(
        "邮箱SMTP服务器秘钥", max_length=128, null=True)

    class Meta:
        db_table = 'omp_email_smtp_setting'
        verbose_name = verbose_name_plural = '平台邮件服务器配置'

    alert_manage_key = {
        "EMAIL_SEND": "email_host_user",
        "smtp_auth_username": "email_host_user",
        "EMAIL_SEND_PASSWORD": "email_host_password",
        "smtp_auth_password": "email_host_password",
        "EMAIL_ADDRESS": "email_url",
    }

    def get_dict(self):
        return {
            "host": self.email_host,
            "port": self.email_port,
            "username": self.email_host_user,
            "password": self.email_host_password
        }

    @property
    def email_url(self):
        if hasattr(self, "email"):
            return self.email
        email_send = AlertSendWaySetting.objects.filter(
            way_name="email").first()
        email = ""
        if email_send and email_send.used:
            email = email_send.server_url.split(",")[0]
        setattr(self, "email", email)
        return email

    def update_config(self, key):
        if key in {"EMAIL_SEND_USER", "smtp_from"}:
            value = self.email_host_user
        elif key in {"SMTP_SMARTHOST", "smtp_smarthost"}:
            value = f"{self.email_host}:{self.email_port}"
        elif key in self.alert_manage_key:
            value = getattr(self, self.alert_manage_key.get(key))
        elif key in {"smtp_hello", "SMTP_HELLO"}:
            value = ".".join(self.email_host.split(".")[-2:])
        elif key == "RECEIVER":
            value = "cloudwise"
        else:
            value = None
        return value

    @staticmethod
    def reload_alert_manage():
        from promemonitor.alertmanager import Alertmanager
        alertmanager_url = Alertmanager.get_alertmanager_config()
        try:
            response = requests.post(f"http://{alertmanager_url}/-/reload")  # NOQA
        except Exception as e:
            logger.error(f"重载alertmanager配置出错！错误信息：{str(e)}")
            return False
        if response.status_code == 200:
            return True
        return False

    def set_omp_conf(self):
        # 更新omp.yaml
        from utils.parse_config import config_file_path
        with open(config_file_path, "r", encoding="utf8") as fp:
            content = fp.read()
        my_yaml = yaml.YAML()
        code = my_yaml.load(content)
        for key, value in code.get("alert_manager", {}).items():
            if key == "send_email":
                value = bool(self.email_url)
            else:
                value = self.update_config(key)
            if value is None:
                continue
            code["alert_manager"][key] = value
        with open(config_file_path, "w", encoding="utf8") as fp:
            my_yaml.dump(code, fp)

    def set_alert_manage_config(self):
        # 更新alert manage配置
        from omp_server.settings import PROJECT_DIR
        config_path = os.path.join(
            PROJECT_DIR, "component/alertmanager/conf/alertmanager.yml")
        with open(config_path, "r", encoding="utf8") as fp:
            code = yaml.load(fp.read(), yaml.Loader)
        for key, value in code.get("global", {}).items():
            value = self.update_config(key)
            if value is None:
                continue
            code["global"][key] = value

        if not self.email_url:
            for receiver in code.get("receivers"):
                if "email_configs" in receiver:
                    code.get("receivers")[0].pop("email_configs", {})
        else:
            email_configs = [
                {
                    "send_resolved": bool(self.email_url),
                    "to": self.email_url,
                    "headers": {"Subject": "OMP ALERT"},
                    "html": '{{ template \"email.to.html\" . }}'
                }
            ]
            code.get("receivers")[0]["email_configs"] = email_configs
        code["templates"] = [
            f"{PROJECT_DIR}component/alertmanager/templates/*tmpl"]
        with open(config_path, "w", encoding="utf8") as fp:
            yaml.dump(code, fp, Dumper=yaml.RoundTripDumper)
        return self.reload_alert_manage()

    def update_setting_config(self):
        """
        更新配置文件
        :return:
        """
        self.set_omp_conf()
        return self.set_alert_manage_config(), self.email_url


class ModuleSendEmailSetting(models.Model):
    module = models.CharField(
        "功能模块:BackupSetting,JobSetting", max_length=64)
    send_email = models.BooleanField("是否开启邮件推送", default=False)
    to_users = models.TextField("邮箱接收用户", default="")
    env_id = models.IntegerField("环境id", default=0)

    class Meta:
        db_table = 'omp_module_email_send_setting'
        verbose_name = verbose_name_plural = '平台邮件发送账号配置'

    @classmethod
    def get_email_settings(cls, env_id, module):
        try:
            _obj = cls.objects.get(env_id=env_id, module=module)
        except Exception as e:
            logger.error(e)
            logger.error(f"module: {module}, env_id:{env_id}邮箱配置不存在")
            return None
        return _obj

    @classmethod
    def update_email_settings(cls, env_id, module, send_email, to_users):
        _obj, _ = cls.objects.get_or_create(env_id=env_id, module=module)
        _obj.send_email = send_email
        _obj.to_users = to_users
        _obj.save()
