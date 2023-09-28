# !/usr/bin/python3
# -*-coding:utf-8-*-
"""
备份相关的路由
"""
from rest_framework.routers import DefaultRouter

from backups.views import BackupSettingView, BackupHistoryView, \
    CanBackupInstancesView, BackupCustomView, BackupCustomRepeatView

router = DefaultRouter()
# 获取可备份实例列表
router.register(r'canBackupInstances', CanBackupInstancesView,
                basename='canBackupInstances')
# 备份设置获取/创建/更新/删除 单次测试
router.register(r'backupSettings', BackupSettingView,
                basename='backupSettings')
# 自定义接口
router.register(r'backupCustom', BackupCustomView, basename='backupCustom')
# 自定义接口校验
router.register(r'backupRepeatCustom', BackupCustomRepeatView, basename='backupRepeatCustom')

# 备份历史记录、删除备份
router.register(r'backupHistory', BackupHistoryView,
                basename='backupHistory')

urlpatterns = router.urls
