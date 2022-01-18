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
