"""
模型混入类
"""
from django.db import models


class TimeStampMixin(models.Model):
    """ 创建、更新时间混入类 """

    created = models.DateTimeField(
        "创建时间", null=True, auto_now_add=True, help_text="创建时间")
    modified = models.DateTimeField(
        "更新时间", null=True, auto_now=True, help_text="更新时间")

    class Meta:
        abstract = True


class DeleteMixin(models.Model):
    """ 软删除混入类 """

    is_deleted = models.BooleanField(default=False, help_text="软删除")

    def delete(self, using=None, soft=True, *args, **kwargs):
        if soft:
            self.is_deleted = True
            self.save(using=using)
        else:
            return super(DeleteMixin, self).delete(using=using, *args, **kwargs)

    class Meta:
        abstract = True


class UpgradeStateChoices(models.IntegerChoices):

    UPGRADE_WAIT = 0, "等待升级"
    UPGRADE_ING = 1, "正在升级"
    UPGRADE_SUCCESS = 2, "升级成功"
    UPGRADE_FAIL = 3, "升级失败"


class UpgradeStateMixin(models.Model):

    upgrade_state = models.IntegerField(
        "升级结果",
        choices=UpgradeStateChoices.choices,
        default=UpgradeStateChoices.UPGRADE_WAIT
    )

    class Meta:
        abstract = True


class RollbackStateChoices(models.IntegerChoices):
    ROLLBACK_WAIT = 0, "等待回滚"
    ROLLBACK_ING = 1, "正在回滚"
    ROLLBACK_SUCCESS = 2, "回滚成功"
    ROLLBACK_FAIL = 3, "回滚失败"


class RollBackStateMixin(models.Model):

    rollback_state = models.IntegerField(
        "回滚结果",
        choices=RollbackStateChoices.choices,
        default=RollbackStateChoices.ROLLBACK_WAIT
    )

    class Meta:
        abstract = True
