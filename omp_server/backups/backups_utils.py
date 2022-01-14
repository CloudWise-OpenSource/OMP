# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: lingyang guo
import datetime
import logging
import os
import subprocess
import tarfile

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


def backup_service_data(history):
    """
    备份服务
    :param history: 本次备份的记录
    :return:
    """

    backup_script_func = BackupDB().backup_service
    _thread = ResultThread(
        target=backup_script_func,
        args=(history.id,))
    _thread.start()
    _thread.join()
    thread_result = _thread.get_result()

    err_message = ""

    backup_flag = thread_result[0]
    backup_message = thread_result[1]
    logger.info(f"备份结果为：{backup_message}")

    back_resp = {"backup_flag": backup_flag,
                 "msg": backup_message, "file_name": history.file_name}

    if not backup_flag:
        history.result = history.FAIL
        history.file_name = "-"
        history.file_size = "-"
        history.file_deleted = True
        history.expire_time = None
        err_message += backup_message if not backup_message else f"备份任务{history.backup_name}动作执行失败!"
    else:
        file_path = os.path.join(history.retain_path, history.file_name)
        size = os.path.getsize(file_path) / 1024 / 1024
        ln_path = os.path.join(
            settings.PROJECT_DIR, "data/backup/", history.file_name)
        cmd_str = f"ln -s {file_path} {ln_path}"
        _out, _err, _code = cmd(cmd_str)
        if _code:
            history.result = history.FAIL
            err_message += "  创建软连接出错！"
        else:
            history.result = history.SUCCESS
        history.file_size = "%.3f" % size
    history.message = {"backup_resp": back_resp, "err_message": err_message}
    history.save()
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
        ln_path = os.path.join(
            settings.PROJECT_DIR, "data/backup/", history.file_name)
        if expire_file == ln_path:
            continue
        try:
            os.remove(ln_path)
        except Exception as e:
            logger.error(f"删除备份文件软链{ln_path}失败: {str(e)}")
    return fail_files
