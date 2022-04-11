from django.db import models
from .env import Env


class SelfHealingSetting(models.Model):
    """自愈策略设置表"""
    used = models.BooleanField("是否启用", default=False)
    alert_count = models.IntegerField("触发自愈的告警次数", default=1)
    max_healing_count = models.IntegerField("最多自愈操作次数", default=5)
    env = models.ForeignKey(
        Env, null=True, on_delete=models.SET_NULL,
        verbose_name="环境", help_text="环境")

    class Meta:
        db_table = "omp_self_healing_setting"
        verbose_name = verbose_name_plural = "自愈设置"


class SelfHealingHistory(models.Model):
    """自愈历史记录"""
    is_read = models.IntegerField("此消息是否已读，0-未读；1-已读", default=0)
    host_ip = models.CharField("自愈主机ip", max_length=64)
    service_name = models.CharField("自愈服务名称", max_length=64, default="")
    instance_name = models.CharField("自愈实例名称", max_length=128, default="", help_text="自愈实例名称")
    HEALING_FAIL = 0
    HEALING_ING = 2
    HEALING_SUCCESS = 1
    STATE_CHOICES = (
        (HEALING_ING, "自愈中"),
        (HEALING_FAIL, "自愈失败"),
        (HEALING_SUCCESS, "自愈成功")
    )
    state = models.IntegerField("自愈状态", choices=STATE_CHOICES, default=HEALING_ING)
    healing_count = models.IntegerField("已运行自愈次数", default=0)
    start_time = models.DateTimeField("自愈开始时间", null=True)
    end_time = models.DateTimeField("自愈结束时间", null=True)
    healing_log = models.JSONField("自愈日志", default=dict)
    env = models.ForeignKey(
        Env, null=True, on_delete=models.SET_NULL,
        verbose_name="环境", help_text="环境")
    fingerprint = models.CharField("关联告警唯一值", max_length=64)
    alert_time = models.DateTimeField("关联告警时间，与fingerprint确定同一次告警", null=True)
    alert_content = models.TextField("告警日志内容", default="")
    monitor_log = models.TextField("grafana日志url", default="")
    service_en_type = models.CharField("服务类型，self_dev&component&database", max_length=64, default="")

    class Meta:
        db_table = "omp_self_healing_history"
        verbose_name = verbose_name_plural = "自愈历史记录"
