import os

from django.db import models

from .env import Env


class InspectionHistory(models.Model):
    """巡检记录历史表"""
    objects = None
    id = models.AutoField(primary_key=True, unique=True, help_text="自增主键")
    inspection_name = models.CharField(
        max_length=256, null=False, blank=False, help_text="报告名称:巡检类型名称")
    inspection_type = models.CharField(
        max_length=32, default="service", help_text="巡检类型，service、host、deep")
    inspection_status = models.IntegerField(
        default=0, help_text="巡检状态:1-进行中；2-成功；3-失败")
    execute_type = models.CharField(
        max_length=32, null=False, blank=False, default="man",
        help_text="执行方式: 手动-man；定时：auto")
    inspection_operator = models.CharField(
        max_length=16, null=False, blank=False, help_text="操作人员-当前登录人")
    hosts = models.JSONField(
        null=True, blank=True, help_text="巡检主机:['10.0.9.158']")
    services = models.JSONField(
        null=True, blank=True, help_text="巡检组件: [8,9]")
    start_time = models.DateTimeField(auto_now_add=True, help_text="开始时间")
    end_time = models.DateTimeField(null=True, help_text="结束时间，后端后补")
    duration = models.IntegerField(default=0, help_text="巡检用时：单位s，后端后补")
    env = models.ForeignKey(
        Env, null=True, on_delete=models.SET_NULL, verbose_name="当前环境id",
        help_text="当前环境id")
    NOT_SEND = 3
    SUCCESS = 1
    ING = 2
    FAIL = 0
    SEND_RESULT_CHOICES = (
        ("发送成功", SUCCESS),
        ("发送中", ING),
        ("发送失败", FAIL),
        ("未发送", NOT_SEND)
    )
    send_email_result = models.IntegerField(
        "邮件推送状态", choices=SEND_RESULT_CHOICES, default=NOT_SEND)

    class Meta:
        db_table = 'inspection_history'
        verbose_name = verbose_name_plural = "巡检记录历史表"
        ordering = ("-start_time",)

    def send_email_content(self):
        return f"""
                巡检任务名称：{self.inspection_name}\n
                巡检时间：{self.start_time.strftime("%Y-%m-%d %H:%M:%S")}
                """

    def fetch_file_kwargs(self):
        from omp_server.settings import PROJECT_DIR
        inspection_report = InspectionReport.objects.filter(
            inst_id=self.id).first()
        file_path = os.path.join(
            PROJECT_DIR, f"data/inspection_file/{inspection_report.file_name}")
        return {"path": file_path}


class InspectionCrontab(models.Model):
    """巡检任务 定时配置表"""
    j_type = (
        (0, "深度分析"),
        (1, "主机巡检"),
        (2, "组件巡检")
    )

    objects = None
    id = models.AutoField(primary_key=True, unique=True, help_text="自增主键")
    job_type = models.IntegerField(
        default=0, choices=j_type, help_text="任务类型：0-深度分析 1-主机巡检 2-组建巡检")
    job_name = models.CharField(
        max_length=128, null=False, blank=False, help_text="任务名称")
    is_start_crontab = models.IntegerField(
        default=0, help_text="是否开启定时任务：0-开启，1-关闭")
    crontab_detail = models.JSONField(help_text="定时任务详情")
    create_date = models.DateTimeField(auto_now_add=True, help_text="创建时间")
    update_time = models.DateTimeField(auto_now=True, help_text="修改时间")
    env = models.ForeignKey(
        Env, null=True, on_delete=models.SET_NULL, verbose_name="环境",
        help_text="环境")

    class Meta:
        """表名等信息"""
        db_table = 'inspection_crontab'
        verbose_name = verbose_name_plural = "巡检任务 定时配置表"
        ordering = ("id",)


class InspectionReport(models.Model):
    """巡检 报告"""
    objects = None
    id = models.AutoField(primary_key=True, unique=True, help_text="自增主键")
    file_name = models.CharField(
        max_length=128, null=True, blank=True, help_text="导出文件名")
    scan_info = models.JSONField(null=True, blank=True, help_text="扫描统计")
    scan_result = models.JSONField(null=True, blank=True, help_text="分析结果")
    risk_data = models.JSONField(null=True, blank=True, help_text="风险指标")
    host_data = models.JSONField(null=True, blank=True, help_text="主机列表")
    serv_plan = models.JSONField(null=True, blank=True, help_text="服务平面图")
    serv_data = models.JSONField(null=True, blank=True, help_text="服务列表")
    inst_id = models.OneToOneField(
        InspectionHistory, null=True, on_delete=models.SET_NULL,
        verbose_name="巡检记录历史表", help_text="巡检记录历史表id")

    class Meta:
        """表名等信息"""
        db_table = 'inspection_report'
        verbose_name = verbose_name_plural = "巡检任务 报告数据"
        ordering = ("id",)
