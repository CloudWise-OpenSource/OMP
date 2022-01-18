# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: lingyang guo
import datetime
import logging

from celery import shared_task
from celery.utils.log import get_task_logger

from backups.backups_utils import rm_backend_file, backup_service_data
from db_models.models import BackupSetting, BackupHistory

# 屏蔽celery任务日志中的paramiko日志
logging.getLogger("paramiko").setLevel(logging.WARNING)
logger = get_task_logger("celery_log")


@shared_task
def backup_service(**kwargs):
    """
    定时备份函数
    :**kwargs:
    :return:
    """
    # 判断setting是否存在，是否开启
    backup_setting_id = kwargs.get("backup_setting_id")
    backup_setting = BackupSetting.objects.filter(
        id=backup_setting_id).first()
    if not backup_setting or not backup_setting.is_on:
        logger.error("未找到备份策略！")
        return
    date_str = datetime.date.today().strftime('%Y%m%d')
    history_count = BackupHistory.objects.filter(
        create_time__gte=datetime.date.today()
    ).count()
    name = f"{date_str}{history_count + 1}-{backup_setting.env_id}"
    if backup_setting.retain_day == -1:
        expire_time = None
    else:
        expire_time = datetime.datetime.now() + datetime.timedelta(
            days=backup_setting.retain_day)
    history = BackupHistory.objects.create(
        backup_name=f"数据备份-{name}",
        content=backup_setting.backup_instances,
        env_id=backup_setting.env_id,
        expire_time=expire_time,
        message={},
        retain_path=backup_setting.retain_path,
        file_name=f"数据备份-{name}.tar.gz"
    )
    # 调备份
    backup_service_data(history)
    # 如果有过期删过期, 更新file_deleted
    rm_backend_file()


@shared_task
def backup_service_once(history_id):
    history = BackupHistory.objects.get(id=history_id)
    backup_service_data(history)
