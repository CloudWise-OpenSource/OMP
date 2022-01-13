# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: lingyang guo
import datetime
import logging
import os
import re
import subprocess
import tarfile

from celery import shared_task
from django.conf import settings

from backups.backup_service import BackupDB
from db_models.models import BackupHistory, EmailSMTPSetting, ModuleSendEmailSetting, BackupSetting
from utils.plugin.send_email import ModelSettingEmailBackend, SendBackupHistoryEmailContent, many_send, ResultThread

logger = logging.getLogger("server")


def cmd(command):
    """执行本地shell命令"""
    p = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = p.communicate()
    _out, _err, _code = \
        stdout.decode("utf8"), stderr.decode("utf8"), p.returncode
    return _out, _err, _code


def tar_files(source_path, target_path):
    """
    压缩文件
    可以压缩多个文件或者单个目录
    source_path：源文件路径 list [a.tar.gz, b.tar.gz]
    target_path： 目标文件路径
    """
    success = True
    try:
        with tarfile.open(target_path, "w:gz") as tar:
            for file_path in source_path:
                if not os.path.exists(file_path):
                    success = False
                tar.add(file_path)
        logging.info(f"{source_path}文件打包成功,压缩文件为{target_path}")
    except Exception as e:
        logging.error(f"{source_path}文件打包错误,error={e}")
        os.remove(target_path)
        return False
    if not success:
        os.remove(target_path)
        return False
    for file_path in source_path:
        os.remove(file_path)
    return True


def send_email(history_id, emails):
    """
    发送邮件
    :param history_id: 备份历史记录
    :param emails: 邮箱列表
    :return:
    """
    history = BackupHistory.objects.filter(id=history_id).first()
    if not history:
        return

    history.send_email_result = history.ING
    history.save()
    reason = ""
    try:
        connection = ModelSettingEmailBackend()
        content = SendBackupHistoryEmailContent(history)
        fail_user = many_send(connection, content, emails)
    except Exception as e:
        logger.error(f"发送邮件失败， 错误信息：{str(e)}")
        reason = "系统异常，请重试!"
        fail_user = emails
    if fail_user:
        history.send_email_result = history.FAIL
        reason = "发件失败，请检查smtp邮箱服务器配置！"
    else:
        history.send_email_result = history.SUCCESS
    history.email_fail_reason = reason
    history.save()
    return reason


def transfer_week(request):
    """
    适配前端day_of_week参数传递
    """
    day_of_week = request.data.get('crontab_detail').get('day_of_week')
    if day_of_week == '6':
        day_of_week = '0'
    elif day_of_week == '*':
        pass
    else:
        day_of_week = str(int(day_of_week) + 1)

    return day_of_week


def backup_service_data(path, backup_instances, history):
    """
    备份服务
    :param path: 备份策略路径 '/data/backups'
    :param backup_instances: 需要备份的服务， [] or set()
    :param history: 本次备份的记录
    :return:
    """
    threading_list = []

    backup_script_func = BackupDB().backup_service
    _thread = ResultThread(
        target=backup_script_func,
        args=(history.id,))
    threading_list.append(_thread)
    threading_list_result = []
    [thread_obj.start() for thread_obj in threading_list]

    for thread_obj in threading_list:
        thread_obj.join()
        threading_list_result.append(thread_obj.get_result())
    all_fail = True
    file_names, resp_list = [], []
    err_message = ""
    for service_instance_name, result in zip(backup_instances, threading_list_result):
        _out, _err, _code = result
        logger.info(f"备份结果为：{_out}")
        if _code:
            err_message += "执行备份脚本失败！"
            continue
        """
        2021-08-24 10:59:42 - INFO 所有环境中的mysql完成备份 \n
        True  mysql1-20210824105934.tar.gz\n
        """
        com_str = re.compile(".*\n(True|False)\s(.*)\s(.*)\n")  # NOQA
        if not re.findall(com_str, _out)[0]:
            err_message += "执行备份脚本失败！"
            continue
        backup_flag, msg, file_name = re.findall(com_str, _out)[0]
        if "False" in backup_flag:
            err_message += msg
            continue
        resp_list.append(
            {"backup_flag": backup_flag, "msg": msg, "file_name": file_name}
        )
        if backup_flag != "True":
            err_message += msg if not msg else f"备份实例{service_instance_name}失败!"
            continue
        all_fail = False
        file_path = os.path.join(path, file_name)
        file_names.append(file_path)
    if all_fail:
        history.result = history.FAIL
        history.file_name = "-"
        history.file_size = 0
        history.file_deleted = True
        history.expire_time = None
    else:
        file_name = f"backup-{history.backup_name.split('-', 1)[1]}.tar.gz"
        new_file_path = os.path.join(path, file_name)
        status = tar_files(file_names, new_file_path)
        if not status:
            err_message += "压缩合并文件出错！"
            history.result = history.FAIL
            history.file_name = "-"
            history.file_size = None
            history.file_deleted = True
            history.expire_time = None
        else:
            size = os.path.getsize(new_file_path) / 1024 / 1024
            path_file = os.path.join(
                settings.ROOT_DIR, f"data/backup/{file_name}")
            cmd_str = f"ln -s {new_file_path} {path_file}"
            _out, _err, _code = cmd(cmd_str)
            if _code:
                history.result = history.FAIL
                err_message += "  创建软连接出错！"
            else:
                history.result = history.SUCCESS
            if len(file_names) != len(backup_instances):
                history.result = history.FAIL
            history.file_name = file_name
            history.file_size = "%.3f" % size
    history.message = {"script_result": resp_list, "err_message": err_message}
    history.save()
    # 删除原文件
    for bi in backup_instances:
        try:
            old_path = os.path.join(path, bi)
            cmd(f"rm -rf {old_path}/*.tar.gz")
        except Exception as e:
            logger.info(f"删除原文件失败！{str(e)}")
    email_setting = EmailSMTPSetting.objects.first()
    if not email_setting:
        return
    backup_setting = ModuleSendEmailSetting.get_email_settings(
        history.env_id, BackupSetting.__name__
    )
    if not backup_setting:
        return
    if not backup_setting.send_email:
        return
    send_email(history.id, backup_setting.to_users.split(","))


def rm_backend_file(ids=None):
    """
    删除过期文件
    :param ids: BackupHistory ids
    :return:
    """
    if ids:
        histories = BackupHistory.objects.filter(id__in=ids)
    else:
        histories = BackupHistory.objects.filter(
            expire_time__lte=datetime.datetime.now(),
            file_deleted=False
        )
    fail_files = []
    for history in histories:
        expire_file = os.path.join(history.retain_path, history.file_name)
        try:
            os.remove(expire_file)
            history.file_deleted = True
            history.save()
        except Exception as e:
            logger.error(f"删除备份文件{expire_file}失败: {str(e)}")
            if os.path.exists(expire_file):
                fail_files.append(history.file_name)
            else:
                history.file_deleted = True
                history.save()
        ln_path = os.path.join(settings.ROOT_DIR,
                               f"data/backup/{history.file_name}")
        try:
            os.remove(ln_path)
        except Exception as e:
            logger.error(f"删除备份文件软链{ln_path}失败: {str(e)}")
    return fail_files


@shared_task
def backup_once(backup_history_id):
    """
    手动备份
    :param backup_history_id: 历史记录id
    :return:
    """
    history = BackupHistory.objects.get(id=backup_history_id)
    backup_service_data(history.retain_path, history.content, history)
