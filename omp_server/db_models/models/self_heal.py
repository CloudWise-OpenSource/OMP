from django.db import models
from django.core.validators import MaxValueValidator


class WaitSelfHealing(models.Model):
    # 0 等待自愈 1 自愈中 存在自愈中的服务不被允许再次触发自愈，保证自愈过程中只有一个自愈在进行。
    service_name = models.CharField("自愈服务名称", max_length=64, default="")
    repair_ser = models.JSONField("自愈缓存服务详情", default=dict)
    repair_status = models.IntegerField("自愈缓存服务", default=0)

    class Meta:
        db_table = "omp_wait_self_healing"
        verbose_name = verbose_name_plural = "自愈等待队列"


class SelfHealingSetting(models.Model):
    """自愈策略设置表"""
    REPAIR_CHOICES = [
        (0, "启动"),
        (1, "重新启动")
    ]

    used = models.BooleanField("是否启用", default=False)
    max_healing_count = models.IntegerField("最多自愈操作次数", default=5, validators=[MaxValueValidator(20)])
    fresh_rate = models.IntegerField("周期内采集告警消息频次", default=10, validators=[MaxValueValidator(60)])
    instance_tp = models.IntegerField("实例类别", choices=REPAIR_CHOICES, default=0)
    repair_instance = models.JSONField("修复实例", default=dict, blank=False, null=False)

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
    healing_log = models.TextField("自愈日志", default="")
    alert_time = models.DateTimeField("关联告警时间，与fingerprint确定同一次告警", null=True)
    alert_content = models.TextField("告警日志内容", default="")
    monitor_log = models.TextField("grafana日志url", default="")

    class Meta:
        db_table = "omp_self_healing_history"
        verbose_name = verbose_name_plural = "自愈历史记录"
