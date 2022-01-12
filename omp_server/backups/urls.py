# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: lingyang guo
"""
备份相关的路由
"""
from rest_framework.routers import DefaultRouter

from backups.views import BackupSettingView, BackupOnceView, BackupHistoryView, BackupSendEmailView, \
    CanBackupInstancesView

router = DefaultRouter()
# 获取可备份实例列表
router.register(r'canBackupInstances', CanBackupInstancesView,
                basename='canBackupInstances')
# 备份设置获取/创建/更新
router.register(r'backupSettings', BackupSettingView,
                basename='backupSettings')
# 单次备份
router.register(r'backupOnce', BackupOnceView, basename='backupOnce')
# 备份历史记录、删除备份
router.register(r'backupHistory', BackupHistoryView,
                basename='backupHistory')
# 推送备份
router.register(r'backupSendEmail', BackupSendEmailView,
                basename='backupSendEmail')
urlpatterns = router.urls
