from django.db import models
from db_models.mixins import TimeStampMixin


class ModuleChoices(models.TextChoices):
    INSTALL = "MainInstallHistory", "安装"
    UPGRADE = "UpgradeHistory", "升级"
    ROLLBACK = "RollbackHistory", "回滚"


class StateChoices(models.TextChoices):

    MAININSTALLHISTORY_0 = "INSTALL_STATUS_READY", "等待安装"
    MAININSTALLHISTORY_1 = "INSTALL_STATUS_INSTALLING", "正在安装"
    MAININSTALLHISTORY_2 = "INSTALL_STATUS_SUCCESS", "安装成功"
    MAININSTALLHISTORY_3 = "INSTALL_STATUS_FAILED", "安装失败"
    MAININSTALLHISTORY_4 = "INSTALL_STATUS_REGISTER", "正在注册"

    UPGRADEHISTORY_0 = "UPGRADE_WAIT", "等待升级"
    UPGRADEHISTORY_1 = "UPGRADE_ING", "正在升级"
    UPGRADEHISTORY_2 = "UPGRADE_SUCCESS", "升级成功"
    UPGRADEHISTORY_3 = "UPGRADE_FAIL", "升级失败"

    ROLLBACKHISTORY_0 = "ROLLBACK_WAIT", "等待回滚"
    ROLLBACKHISTORY_1 = "ROLLBACK_ING", "正在回滚"
    ROLLBACKHISTORY_2 = "ROLLBACK_SUCCESS", "回滚成功"
    ROLLBACKHISTORY_3 = "ROLLBACK_FAIL", "回滚失败"


class ExecutionRecord(TimeStampMixin):
    # 通过django信号同步生成记录(create_execution_record)

    module = models.CharField(
        "执行记录的module名",
        max_length=32,
        choices=ModuleChoices.choices,
        default=ModuleChoices.INSTALL
    )
    # UpgradeHistory.id & MainInstallHistory.operation_uuid
    module_id = models.CharField("执行记录的id", max_length=36, default="0")
    operator = models.CharField(
        "操作用户",
        max_length=150,
        default="admin"
    )
    state = models.CharField(
        "状态",
        max_length=32,
        choices=StateChoices.choices,
        default=StateChoices.MAININSTALLHISTORY_0
    )
    count = models.IntegerField("服务数量", default=0)
    end_time = models.DateTimeField("更新时间", null=True)

    class Meta:
        db_table = "omp_execution_record"
        verbose_name = verbose_name_plural = '执行记录'
