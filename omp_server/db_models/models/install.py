from django.db import models

from db_models.mixins import TimeStampMixin
from .service import Service


class MainInstallHistory(TimeStampMixin):
    """ 主安装记录表 """

    objects = None
    INSTALL_STATUS_READY = 0
    INSTALL_STATUS_INSTALLING = 1
    INSTALL_STATUS_SUCCESS = 2
    INSTALL_STATUS_FAILED = 3
    INSTALL_STATUS_REGISTER = 4
    INSTALL_STATUS_CHOICES = (
        (INSTALL_STATUS_READY, "待安装"),
        (INSTALL_STATUS_INSTALLING, "安装中"),
        (INSTALL_STATUS_SUCCESS, "安装成功"),
        (INSTALL_STATUS_FAILED, "安装失败"),
        (INSTALL_STATUS_REGISTER, "正在注册"),
    )
    operator = models.CharField(
        "操作用户", max_length=32,
        null=False, blank=False, default="admin", help_text="用户"
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

    @property
    def execution_record_state(self):
        # 执行记录使用
        return self.install_status

    def operate_count(self, exclude_service_ids=None):
        # 安装服务个数, exclude_service_ids删除服务前触发
        queryset = self.detailinstallhistory_set.filter(
            service__isnull=False
        )
        if exclude_service_ids:
            queryset = queryset.exclude(service_id__in=exclude_service_ids)
        return queryset.count()

    @property
    def module_id(self):
        return self.operation_uuid


class PreInstallHistory(TimeStampMixin):
    """ 记录安装过程中主机的操作记录内容 """
    objects = None
    main_install_history = models.ForeignKey(
        MainInstallHistory, null=True, blank=True,
        on_delete=models.SET_NULL, help_text="关联主安装记录")
    name = models.CharField(
        "名称", max_length=32, blank=False, null=False,
        default="初始化安装流程", help_text="名称"
    )
    ip = models.GenericIPAddressField(
        "主机ip地址", blank=False, null=False, help_text="主机ip地址")
    install_flag = models.IntegerField(
        "安装标志", default=0,
        help_text="0-待安装 1-安装中 2-安装成功 3-安装失败")
    install_log = models.TextField("主机层安装日志", help_text="主机层安装日志")

    class Meta:
        """元数据"""
        db_table = "omp_pre_install_history"
        verbose_name = verbose_name_plural = "前置安装记录"


class PostInstallHistory(TimeStampMixin):
    """ 记录安装完成后的其他操作，如注册、tengine、nacos更新 """
    objects = None
    main_install_history = models.ForeignKey(
        MainInstallHistory, null=True, blank=True,
        on_delete=models.SET_NULL, help_text="关联主安装记录")
    name = models.CharField(
        "名称", max_length=32, blank=False, null=False,
        default="安装后续任务", help_text="名称"
    )
    ip = models.CharField(
        "fake主机ip地址", blank=False, null=False, default="postAction",
        max_length=128, help_text="主机ip地址")
    install_flag = models.IntegerField(
        "安装标志", default=0,
        help_text="0-待执行 1-执行中 2-执行成功 3-执行失败")
    install_log = models.TextField("安装后续任务日志", help_text="安装后续任务日志")

    class Meta:
        """元数据"""
        db_table = "omp_post_install_history"
        verbose_name = verbose_name_plural = "后置安装记录"


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
    # 若修改on_delete，需处理update_execution_record
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


class DeploymentPlan(models.Model):
    """ 部署计划 """
    plan_name = models.CharField(
        "部署计划名称", max_length=32,
        null=False, blank=False, help_text="部署计划名称")
    host_num = models.IntegerField(
        "主机数量", default=0, help_text="主机数量")
    product_num = models.IntegerField(
        "产品数量", default=0, help_text="产品数量")
    service_num = models.IntegerField(
        "服务数量", default=0, help_text="服务数量")
    create_user = models.CharField(
        "创建用户", max_length=16,
        null=False, blank=False, help_text="创建用户")
    operation_uuid = models.CharField(
        "部署操作uuid", max_length=36,
        null=False, blank=False, help_text="部署操作uuid")
    created = models.DateTimeField(
        "创建时间", null=True, auto_now_add=True, help_text="创建时间")

    class Meta:
        db_table = 'omp_deployment_plan'
        verbose_name = verbose_name_plural = '部署计划'
