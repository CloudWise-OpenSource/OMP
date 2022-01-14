import os

from django.db import models

from db_models.mixins import TimeStampMixin


class BackupSetting(models.Model):

    # 校验是否安装该服务，支持的服务
    backup_instances = models.JSONField("备份服务实例名称", default=dict)
    is_on = models.BooleanField("是否开启", default=False)
    crontab_detail = models.JSONField("定时任务详情")
    retain_day = models.IntegerField("文件保存天数", default=1)
    retain_path = models.TextField("文件保存路径", default="/data/omp/data/backup/")
    env_id = models.IntegerField("环境id", default=0)

    class Meta:
        db_table = 'omp_backup_setting'
        verbose_name = verbose_name_plural = '备份设置'


class BackupHistory(TimeStampMixin):

    backup_name = models.CharField("备份任务名称", max_length=128)
    content = models.JSONField('备份内容(实例名):["mysql1","arangodb2"]')
    SUCCESS = 1
    ING = 2
    FAIL = 0
    RESULT_CHOICES = (
        ("成功", SUCCESS),
        ("备份中", ING),
        ("失败", FAIL)
    )
    result = models.IntegerField("结果", choices=RESULT_CHOICES, default=ING)
    message = models.JSONField("返回信息", default=dict)
    file_name = models.CharField("备份文件名", max_length=128, default="")
    file_size = models.CharField("备份文件大小, MB", default="0", max_length=64)
    expire_time = models.DateTimeField("过期时间", null=True)
    file_deleted = models.BooleanField("文件是否被删除", default=False)
    create_time = models.DateTimeField("记录生成时间", auto_now_add=True)
    env_id = models.IntegerField("环境id", default=0)
    retain_path = models.TextField("文件保存路径", default="/data/omp/data/backup/")
    operation = models.CharField("操作方式", default="定时任务执行", max_length=32)
    # omp-v-1.5新增
    NOT_SEND = 3
    SEND_RESULT_CHOICES = (
        ("发送成功", SUCCESS),
        ("发送中", ING),
        ("发送失败", FAIL),
        ("未发送", NOT_SEND)
    )
    send_email_result = models.IntegerField(
        "邮件推送状态", choices=SEND_RESULT_CHOICES, default=NOT_SEND)
    email_fail_reason = models.TextField("邮件推送失败原因", default="")

    class Meta:
        db_table = 'omp_backup_history'
        verbose_name = verbose_name_plural = '备份历史记录'

    def send_email_content(self):
        return f"""
                备份任务名称：{self.backup_name}\n
                备份服务：{','.join(self.content)}\n
                备份时间：{self.create_time.strftime("%Y-%m-%d %H:%M:%S")}
                """

    def fetch_file_kwargs(self):
        file_path = os.path.join(self.retain_path, self.file_name)
        return {"path": file_path}
