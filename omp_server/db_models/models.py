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
    # 存储数据格式为[{"port": 18080, "key": "http_port"}]
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
    # [{"start": "./start.sh", "stop": "./stop.sh"}]
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

    class Meta:
        """元数据"""
        db_table = 'omp_application'
        verbose_name = verbose_name_plural = "应用商店服务"


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
