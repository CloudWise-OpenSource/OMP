# !/usr/bin/python3
# -*-coding:utf-8-*-
import os
import time
import datetime
import logging

from celery import shared_task
from celery.utils.log import get_task_logger
from utils.plugin.salt_client import SaltClient

from backups.backups_utils import rm_backend_file, backup_service_data, \
    cmd, change_status, check_ing
from db_models.models import BackupSetting, BackupHistory
from utils.plugin.crontab_utils import maintain

# 屏蔽celery任务日志中的paramiko日志
logging.getLogger("paramiko").setLevel(logging.WARNING)
logger = get_task_logger("celery_log")


@shared_task
@maintain
def backup_service(**kwargs):
    """
    定时备份函数
    :**kwargs:
    :return:
    """
    # 判断setting是否存在，是否开启
    backup_setting_id = kwargs.get("task_id")
    backup_setting = BackupSetting.objects.filter(
        id=backup_setting_id).first()
    if check_ing(backup_setting):
        return False
    if backup_setting.retain_day == -1:
        expire_time = None
    else:
        expire_time = datetime.datetime.now() + datetime.timedelta(
            days=backup_setting.retain_day)
    extend_field = backup_setting.backup_custom
    if extend_field:
        extend_field = dict(extend_field.all().values_list("field_k", "field_v"))

    his_ls = []
    for instance in backup_setting.backup_instances:
        name = f"backup-{str(int(time.time()))}-{instance}"
        his_ls.append(
            BackupHistory.objects.create(
                backup_name=name,
                content=instance,
                expire_time=expire_time,
                message={},
                retain_path=backup_setting.retain_path,
                file_name=f"{name}.tar.gz",
                extend_field=extend_field,
            )

        )
    # 调备份
    backup_service_data(his_ls)

    # 如果有过期删过期, 更新file_deleted ToDo 考虑过期数据走向
    histories = BackupHistory.objects.filter(expire_time__lte=datetime.datetime.now()).exclude(expire_time=None)
    if histories:
        rm_backend_file(histories)
        histories.delete()


@shared_task
def pull_back_file(his_id, remote_path, ip):
    """
    同步节点备份数据到omp所在机器
    """
    # 异步暂时想不到如何同步数据
    his_obj = BackupHistory.objects.filter(id=his_id).first()
    salt_client = SaltClient()
    salt_data = salt_client.client.opts.get("root_dir")
    logger.info(f"获取文件ip:{ip},远端目录:{remote_path},本地目录:{his_obj.file_name}")
    cp_flag, cp_msg = salt_client.cp_push(
        target=ip, source_path=remote_path, upload_path=his_obj.file_name
    )
    if not cp_flag:
        return change_status(his_obj, False, cp_msg)
    package_dir = os.path.join(salt_data, f"var/cache/salt/master/minions/{ip}/files/{his_obj.file_name}")
    size = os.path.getsize(package_dir) / 1024 / 1024
    his_obj.file_size = "%.3fM" % size
    his_obj.remote_path = ""
    _out, _err, _code = cmd(f"mv {package_dir} {his_obj.retain_path}")
    if _code == 0:
        logger.info(f"成功同步到omp {his_obj.file_name}")
        return change_status(his_obj, True, "success")
    return change_status(his_obj, False, _err)
