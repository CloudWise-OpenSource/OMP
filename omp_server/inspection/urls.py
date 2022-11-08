# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/10/13 8:52 下午
# Description: 巡检 路由
from rest_framework.routers import DefaultRouter
from inspection.views import (
    InspectionHistoryView, InspectionCrontabView, InspectionReportView,
    InspectionServiceView, InspectionSendEmailSettingView, InspectionSendEmailAPIView)

router = DefaultRouter()
# 巡检 历史记录
router.register("history", InspectionHistoryView, basename="history")
# 巡检-组件巡检 组件列表
router.register("services", InspectionServiceView, basename="services")
# 巡检 定时任务配置
router.register("crontab", InspectionCrontabView, basename="crontab")
# 巡检 报告
router.register("report", InspectionReportView, basename="report")
router.register("inspectionSendEmailSetting",
                InspectionSendEmailSettingView, basename="inspectionSendEmailSetting")
router.register("inspectionSendEmail",
                InspectionSendEmailAPIView, "inspectionSendEmail")
