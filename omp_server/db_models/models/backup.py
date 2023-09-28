import os

from django.db import models

from db_models.mixins import TimeStampMixin


class BackupCustom(models.Model):
    field_k = models.CharField("自定义字段k", max_length=64, null=False)
    field_v = models.CharField("自定义字段v", max_length=256, null=False)
    notes = models.CharField("备注", max_length=32, default="")

    class Meta:
        db_table = 'omp_backup_custom'
        verbose_name = verbose_name_plural = '自定义备份'


class BackupSetting(models.Model):
    # 校验是否安装该服务，支持的服务
    backup_instances = models.JSONField("备份服务实例名称", default=dict)
    is_on = models.BooleanField("是否开启", default=False)
    crontab_detail = models.JSONField("定时任务详情")
    retain_day = models.IntegerField("文件保存天数", default=1)
    retain_path = models.CharField("文件保存路径", default="/data/omp/data/backup/",
                                   null=False, max_length=256)
    backup_custom = models.ManyToManyField(BackupCustom)

    class Meta:
        db_table = 'omp_backup_setting'
        verbose_name = verbose_name_plural = '备份设置'


class BackupHistory(TimeStampMixin):
    backup_name = models.CharField("备份任务名称", max_length=128)
    content = models.CharField('备份实例', max_length=256, default="")
    SUCCESS = 1
    ING = 2
    FAIL = 0
    RESULT_CHOICES = (
        (SUCCESS, "成功"),
        (ING, "备份中"),
        (FAIL, "失败")
    )
    result = models.IntegerField("结果", choices=RESULT_CHOICES, default=ING)
    message = models.TextField("返回信息", default="", max_length=512)
    file_name = models.CharField("备份文件名", max_length=128, default="")
    file_size = models.CharField("备份文件大小, MB", default="0", max_length=64)
    expire_time = models.DateTimeField("过期时间", null=True)
    file_deleted = models.BooleanField("文件是否被删除", default=False)
    create_time = models.DateTimeField("记录生成时间", auto_now_add=True)
    retain_path = models.TextField(
        "文件保存路径", default="/data/omp/data/backup/", max_length=256, null=True, blank=True
    )
    remote_path = models.CharField("远端备份路径", max_length=256, null=True, blank=True)
    extend_field = models.JSONField("冗余字段", default=dict)

    class Meta:
        db_table = 'omp_backup_history'
        verbose_name = verbose_name_plural = '备份历史记录'

    def fetch_file_kwargs(self):
        file_path = os.path.join(self.retain_path, self.file_name)
        return {"path": file_path}
