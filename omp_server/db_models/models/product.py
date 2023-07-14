from django.db import models

from db_models.mixins import TimeStampMixin, DeleteMixin


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

    @property
    def pro_info(self):
        """ 查询是product名字 """
        if self.product:
            return {"pro_name": self.product.pro_name, "pro_version": self.product.pro_version}
        return None


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
