from django.db import models

from .env import Env


class MonitorUrl(models.Model):
    """ 用户操作记录表 """

    objects = None
    name = models.CharField(
        "监控类别", max_length=32, unique=True, help_text="监控类别")
    monitor_url = models.CharField(
        "请求地址", max_length=128, help_text="请求地址")

    class Meta:
        """ 元数据 """
        db_table = "omp_promemonitor_url"
        verbose_name = verbose_name_plural = "监控地址记录"


class Alert(models.Model):
    """告警数据表"""

    objects = None
    is_read = models.IntegerField(
        "已读", default=0, help_text="此消息是否已读，0-未读；1-已读")
    alert_type = models.CharField(
        "告警类型", max_length=32, default="", help_text="告警类型，主机host，服务service")
    alert_host_ip = models.CharField(
        "告警主机ip", max_length=64, default="", help_text="告警来源主机ip")
    alert_service_name = models.CharField(
        "告警服务名称", max_length=128, default="", help_text="服务类告警中的服务名称")
    alert_instance_name = models.CharField(
        "告警实例名称", max_length=128, default="", help_text="告警实例名称")
    alert_service_type = models.CharField(
        "告警服务类型", max_length=128, default="", help_text="服务所属类型")
    alert_level = models.CharField(
        "告警级别", max_length=1024, default="", help_text="告警级别")
    alert_describe = models.CharField(
        "告警描述", max_length=1024, default="", help_text="告警描述")
    alert_receiver = models.CharField(
        "告警接收人", max_length=256, default="", help_text="告警接收人")
    alert_resolve = models.CharField(
        "告警解决方案", max_length=1024, default="", help_text="告警解决方案")
    alert_time = models.DateTimeField(
        "告警发生时间", help_text="告警发生时间")
    create_time = models.DateTimeField(
        "告警信息入库时间", auto_now_add=True, help_text="告警信息入库时间")
    monitor_path = models.CharField(
        "跳转监控路径", max_length=2048, blank=True, null=True, help_text="跳转grafana路由")
    monitor_log = models.CharField(
        "跳转监控日志路径", max_length=2048, blank=True, null=True, help_text="跳转grafana日志页面路由")
    fingerprint = models.CharField(
        "告警的唯一标识", max_length=1024, blank=True, null=True, help_text="告警的唯一标识")
    env = models.ForeignKey(
        Env, null=True, on_delete=models.SET_NULL,
        verbose_name="环境", help_text="环境")

    class Meta:
        """元数据"""
        db_table = 'omp_alert'
        verbose_name = verbose_name_plural = "告警记录"


class Maintain(models.Model):
    """
    维护记录表
    """
    objects = None

    matcher_name = models.CharField(
        "匹配标签", max_length=1024, null=False, help_text="匹配标签")
    matcher_value = models.CharField(
        "匹配值", max_length=1024, null=False, help_text="匹配值")
    maintain_id = models.CharField(
        "维护唯一标识", max_length=1024, null=False, help_text="维护唯一标识")

    class Meta:
        """元数据"""
        db_table = 'omp_maintain'
        verbose_name = verbose_name_plural = "维护记录"


class GrafanaMainPage(models.Model):
    """Grafana 主面板信息表"""
    instance_name = models.CharField(
        "实例名字", max_length=32, unique=True, help_text="信息面板实例名字")
    instance_url = models.CharField(
        "实例地址", max_length=255, unique=True, help_text="实例文根地址")

    class Meta:
        """ 元数据 """
        db_table = "omp_grafana_url"
        verbose_name = verbose_name_plural = "grafana面板记录"


class AlertSendWaySetting(models.Model):
    used = models.BooleanField("是否启用", default=False)
    env_id = models.IntegerField("环境id", default=0)
    way_name = models.CharField("告警推送服务名称", max_length=64)
    server_url = models.TextField("告警推送服务url", default="")
    way_token = models.CharField("服务token", max_length=255, default="")
    extra_info = models.JSONField("服务其他信息", default=dict)

    class Meta:
        db_table = 'omp_alert_send_way_setting'
        verbose_name = verbose_name_plural = '告警推送通道设置'

    # 暂时屏蔽doem的配置
    # @property
    # def get_doem_init_kwargs(self):
    #     """
    #     返回告警推送服务类对象初始化参数
    #     :return:
    #     """
    #     return {"app_key": self.way_token, "server_url": self.server_url}
    #
    # @property
    # def get_doem_dict(self):
    #     return {
    #         "way_token": self.way_token,
    #         "server_url": self.server_url,
    #         "used": self.used
    #     }

    @property
    def get_email_dict(self):
        return {
            "server_url": self.server_url,
            "used": self.used
        }

    @classmethod
    def get_v1_5_email_dict(cls, env_id):
        obj = cls.objects.filter(way_name="email").first()
        kwargs = {
            "server_url": "",
            "used": False
        }
        if obj:
            kwargs.update(server_url=obj.server_url, used=obj.used)
            cls.objects.create(
                env_id=env_id,
                way_name="email",
                server_url=obj.server_url,
                used=obj.used)
        return kwargs

    def get_self_dict(self):
        # 前端展示
        return getattr(self, f"get_{self.way_name}_dict")

    # def get_func_class_obj(self):
    #     """
    #     返回告警推送服务类对象
    #     :return:
    #     """
    #     from base import base_monitor
    #     kwargs = getattr(self, f"get_{self.way_name}_init_kwargs")
    #     return getattr(
    #         base_monitor, f"SendAlertTo{self.way_name.capitalize()}Way"
    #     )(**kwargs)

    @classmethod
    def update_email_config(cls, used, user_emails):
        cls.objects.filter(
            way_name="email"
        ).update(used=used, server_url=user_emails)
