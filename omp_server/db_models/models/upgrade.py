from django.db import models

from .product import ApplicationHub
from .env import Env
from .service import Service
from .user import UserProfile
from db_models.mixins import TimeStampMixin, UpgradeStateMixin, \
    UpgradeStateChoices, RollBackStateMixin


class UpgradeHistory(UpgradeStateMixin, TimeStampMixin):

    operator = models.ForeignKey(
        UserProfile, null=True,
        on_delete=models.SET_NULL,
        verbose_name="用户")
    env = models.ForeignKey(
        Env, null=True,
        on_delete=models.SET_NULL,
        verbose_name="所属环境")

    class Meta:
        db_table = "omp_upgrade_history"
        verbose_name = verbose_name_plural = '升级历史记录'

    @property
    def can_roll_back(self):
        return self.upgradedetail_set.filter(
            upgrade_state__in=[
                UpgradeStateChoices.UPGRADE_SUCCESS,
                UpgradeStateChoices.UPGRADE_FAIL
            ],
            has_rollback=False
        ).exists()


class UpgradeDetail(UpgradeStateMixin, TimeStampMixin):
    history = models.ForeignKey(
        UpgradeHistory,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="升级历史记录")
    union_server = models.CharField(
        "唯一服务实例:ip-app_name(适配hadoop，单服务裂开多个服务)",
        max_length=199,
        null=False
    )
    # null=True待定
    service = models.ForeignKey(
        Service, null=True,
        on_delete=models.SET_NULL,
        verbose_name="服务")
    target_app = models.ForeignKey(
        ApplicationHub,
        null=True,
        related_name="target_app_set",
        on_delete=models.SET_NULL,
        verbose_name="升级目标服务")
    current_app = models.ForeignKey(
        ApplicationHub,
        null=True,
        related_name="current_app_set",
        on_delete=models.SET_NULL,
        verbose_name="升级前服务")
    path_info = models.JSONField("服务包备份路径信息", default=dict)
    handler_info = models.JSONField("升级步骤信息", default=dict)
    message = models.TextField("升级日志信息", default="")
    has_rollback = models.BooleanField("是否已回滚", default=False)

    class Meta:
        db_table = "omp_upgrade_detail"
        verbose_name = verbose_name_plural = '单个服务升级记录'

    def get_service_history(self):
        """
        组织服务操作记录参数
        :return: dict
        """
        return {
            "username": self.history.operator.username,
            "description": f"服务自版本{self.current_app.app_version}"
                           f"升级至版本{self.target_app.app_version}",
            "result": "success" if self.upgrade_state == 2 else "failed",
            "created": self.created
        }


class RollbackHistory(RollBackStateMixin, TimeStampMixin):

    operator = models.ForeignKey(
        UserProfile, null=True,
        on_delete=models.SET_NULL,
        verbose_name="用户")
    env = models.ForeignKey(
        Env, null=True,
        on_delete=models.SET_NULL,
        verbose_name="所属环境")

    class Meta:
        db_table = "omp_rollback_history"
        verbose_name = verbose_name_plural = '回滚历史记录'


class RollbackDetail(RollBackStateMixin, TimeStampMixin):
    history = models.ForeignKey(
        RollbackHistory,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="回滚历史记录")
    upgrade = models.ForeignKey(
        UpgradeDetail, null=True,
        on_delete=models.SET_NULL,
        verbose_name="升级记录")
    path_info = models.JSONField("服务包备份路径信息", default=dict)
    handler_info = models.JSONField("回滚步骤信息", default=dict)
    message = models.TextField("回滚日志信息", default="")

    class Meta:
        db_table = "omp_rollback_detail"
        verbose_name = verbose_name_plural = '单个服务回滚记录'

    def get_service_history(self):
        """
        组织服务操作记录参数
        :return: dict
        """
        return {
            "username": self.history.operator.username,
            "description": f"服务自版本{self.upgrade.target_app.app_version}"
                           f"回滚至版本{self.upgrade.current_app.app_version}",
            "result": "success" if self.rollback_state == 2 else "failed",
            "created": self.created
        }
