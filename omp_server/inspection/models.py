# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/10/13 6:05 下午
# Description: 巡检数据表 model
from django.db import models
from db_models.models import Env


class InspectionHistory(models.Model):
    """巡检记录历史表"""
    objects = None
    id = models.AutoField(primary_key=True, unique=True, help_text="自增主键")
    inspection_name = models.CharField(max_length=256, null=False, blank=False, help_text="报告名称:巡检类型名称")
    inspection_type = models.CharField(max_length=32, default="service", help_text="巡检类型，service、host、deep")
    inspection_status = models.IntegerField(default=0, help_text="巡检状态: 0-未开始；1-进行中；2-成功；3-失败")
    execute_type = models.CharField(max_length=32, null=False, blank=False, default="man",
                                    help_text="执行方式: 手动-man；定时：auto")
    inspection_operator = models.CharField(max_length=16, null=False, blank=False, help_text="操作人员-当前登录人")
    hosts = models.JSONField(null=True, blank=True, help_text="巡检主机:[{'id':'1', 'host':'10.0.9.158'}]")
    services = models.JSONField(null=True, blank=True, help_text="巡检组件")
    start_time = models.DateTimeField(auto_now_add=True, help_text="开始时间")
    end_time = models.DateTimeField(null=True, help_text="结束时间，后端后补")
    duration = models.IntegerField(default=0, help_text="巡检用时：单位s，后端后补")
    env = models.ForeignKey(Env, null=True, on_delete=models.SET_NULL, verbose_name="当前环境id", help_text="当前环境id")

    class Meta:
        db_table = 'inspection_history'
        verbose_name = verbose_name_plural = "巡检记录历史表"
        ordering = ("-start_time",)


class InspectionCrontab(models.Model):
    """巡检任务 定时配置表"""
    j_type = (
        (0, "深度分析"),
        (1, "主机巡检"),
        (2, "组件巡检")
    )

    objects = None
    id = models.AutoField(primary_key=True, unique=True, help_text="自增主键")
    job_type = models.IntegerField(default=0, choices=j_type, help_text="任务类型：0-深度分析 1-主机巡检 2-组建巡检")
    job_name = models.CharField(max_length=128, null=False, blank=False, help_text="任务名称")
    is_start_crontab = models.IntegerField(default=0, help_text="是否开启定时任务：0-开启，1-关闭")
    crontab_detail = models.JSONField(help_text="定时任务详情")
    create_date = models.DateTimeField(auto_now_add=True, help_text="创建时间")
    update_time = models.DateTimeField(auto_now=True, help_text="修改时间")
    env = models.ForeignKey(Env, null=True, on_delete=models.SET_NULL, verbose_name="环境", help_text="环境")

    class Meta:
        """表名等信息"""
        db_table = 'inspection_crontab'
        verbose_name = verbose_name_plural = "巡检任务 定时配置表"
        ordering = ("id",)


class InspectionReport(models.Model):
    """巡检 报告"""
    objects = None
    id = models.AutoField(primary_key=True, unique=True, help_text="自增主键")
    tag_total_num = models.IntegerField(default=0, help_text="总指标数")
    tag_error_num = models.IntegerField(default=0, help_text="异常指标数")
    risk_data = models.JSONField(null=True, blank=True, help_text="风险指标")
    host_data = models.JSONField(null=True, blank=True, help_text="主机列表")
    serv_plan = models.JSONField(null=True, blank=True, help_text="服务平面图")
    serv_data = models.JSONField(null=True, blank=True, help_text="服务列表")
    inst_id = models.OneToOneField(
        InspectionHistory, null=True, on_delete=models.SET_NULL, verbose_name="巡检记录历史表", help_text="巡检记录历史表id")

    class Meta:
        """表名等信息"""
        db_table = 'inspection_report'
        verbose_name = verbose_name_plural = "巡检任务 报告数据"
        ordering = ("id",)
