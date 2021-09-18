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
