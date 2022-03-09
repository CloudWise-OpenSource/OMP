import hashlib
from uuid import uuid4
from django.db import models



class HostThreshold(models.Model):
    """主机阈值设置表"""
    # 主机指标项名称：cpu_used;memory_used;disk_root_used;disk_data_used
    index_type = models.CharField(
        max_length=64, null=False, blank=False, help_text="指标项名称")
    condition = models.CharField(
        max_length=32, null=False, blank=False, help_text="阈值条件")
    condition_value = models.CharField(
        max_length=128, null=False, blank=False, help_text="阈值数值，百分号格式")
    # 告警级别: warning critical
    alert_level = models.CharField(
        max_length=32, null=False, blank=False, help_text="告警级别")
    create_date = models.DateTimeField(auto_now_add=True)
    env_id = models.IntegerField(help_text="环境id", default=1)

    class Meta:
        db_table = 'omp_host_threshold'

    def get_dic(self):
        return {
            "index_type": self.index_type,
            "condition": self.condition,
            "value": self.condition_value,
            "level": self.alert_level,
        }

    def __str__(self):
        return str(self.index_type) + "-" + str(self.condition) + "-" \
               + str(self.condition_value) + "-" + str(self.alert_level)


class ServiceThreshold(models.Model):
    """服务阈值设置表"""
    # 服务指标项名称：service_active;service_cpu_used;service_memory_used
    index_type = models.CharField(
        "指标项名称", max_length=64, null=False, blank=False)
    condition = models.CharField(
        "阈值条件", max_length=32, null=False, blank=False)
    condition_value = models.CharField(
        "阈值数值，百分号格式", max_length=128, null=False, blank=False)
    # 告警级别: warning critical
    alert_level = models.CharField(
        "告警级别", max_length=32, null=False, blank=False)
    create_date = models.DateTimeField(auto_now_add=True)
    env_id = models.IntegerField("环境id", default=1)

    class Meta:
        db_table = 'omp_service_threshold'

    def get_dic(self):
        return {
            "index_type": self.index_type,
            "condition": self.condition,
            "value": self.condition_value,
            "level": self.alert_level,
        }

    def __str__(self):
        return str(self.index_type) + "-" + str(self.condition) + "-" + \
               str(self.condition_value) + "-" + str(self.alert_level)


class ServiceCustomThreshold(models.Model):
    """服务特殊指标阈值设置(临时)"""
    service_name = models.CharField(
        "服务名称", max_length=64, null=False, blank=False)
    index_type = models.CharField(
        "指标项名称", max_length=64, null=False, blank=False)
    condition = models.CharField(
        "阈值条件", max_length=32, null=False, blank=False)
    condition_value = models.CharField(
        "阈值数值", max_length=128, null=False, blank=False)
    # 告警级别: warning critical
    alert_level = models.CharField(
        "告警级别", max_length=32, null=False, blank=False)
    create_date = models.DateTimeField(auto_now_add=True)
    env_id = models.IntegerField("环境id", default=1)

    class Meta:
        db_table = 'omp_service_custom_threshold'
        verbose_name = verbose_name_plural = '服务定制指标阈值设置'


class Rule(models.Model):
    """
    表达式存储
    """
    name = models.CharField("指标名称", max_length=255,null=False)
    expr = models.TextField("监控指标表达式，报警语法", null=False, blank=False)
    service = models.CharField("服务名称",max_length=255, null=False)
    description = models.TextField("描述",null=True)

    class Meta:
        """
        元数据
        """
        db_table = "omp_rule"
        verbose_name = verbose_name_plural = "规则表达式"




class AlertRule(models.Model):
    """
    告警规则
    """
    env_id = models.IntegerField("环境id", default=1)
    expr = models.TextField("监控指标表达式，报警语法", null=False, blank=False)
    threshold_value = models.FloatField("阈值的数值", null=False, blank=False)
    compare_str = models.CharField("比较符", max_length=64)
    for_time = models.CharField("持续一段时间获取不到信息就触发告警", max_length=64)
    severity = models.CharField("告警级别", max_length=64)
    alert = models.TextField("标题，自定义摘要")
    service = models.CharField("指标所属服务名称", max_length=255)
    status = models.IntegerField("启用状态", default=0)
    name = models.CharField("内置指标名称", max_length=255, null=True)
    TYPE = (
        (0, "builtins"),
        (1, "custom"),
        (2, "log")
    )
    quota_type = models.IntegerField("指标的类型", choices=TYPE, default=0)
    labels = models.JSONField("额外指定标签",null=True)
    # builtins_not_enabled = models.IntegerField("内置未启用的规则", default=0)
    summary = models.TextField("描述, 告警指标描述", null=True)
    description = models.TextField("描述, 告警指标描述", null=True)
    create_time = models.DateTimeField("告警规则入库时间", auto_now_add=True)
    update_time = models.DateTimeField("告警规则更新时间", auto_now_add=True)
    forbidden = models.IntegerField("禁止删除", default=1)  # 1能删除  2 禁止删除
    hash_data = models.CharField("唯一hash值", null=True, blank=True, max_length=255) # 唯一hash禁止规则重复

    class Meta:
        """
        元数据
        """
        db_table = "omp_alert_ruler"
        verbose_name = verbose_name_plural = "自定义告警规则"
