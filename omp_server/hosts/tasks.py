# -*- coding: utf-8 -*-
# Project: tasks
# Author: jon.liu@yunzhihui.com
# Create time: 2021-09-12 11:54
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
主机相关异步任务
"""

import os
import time
import logging
import traceback

from django.conf import settings
from celery import shared_task
from celery.utils.log import get_task_logger
from promemonitor.alertmanager import Alertmanager

from db_models.models import (
    Host, Service,
    HostOperateLog
)
from utils.plugin.ssh import SSH
from utils.plugin.monitor_agent import MonitorAgentManager
from utils.plugin.crypto import AESCryptor
from utils.plugin.agent_util import Agent
from app_store.tasks import add_prometheus

# 屏蔽celery任务日志中的paramiko日志
logging.getLogger("paramiko").setLevel(logging.WARNING)
logger = get_task_logger("celery_log")


def deploy_monitor_agent(host_obj, salt_flag=True):
    """
    部署监控Agent
    :param host_obj: 主机对象
    :param salt_flag: 部署主机Agent成功或失败标志
    :return:
    """
    logger.info(f"Deploy monitor agent for {host_obj.ip}")
    if not salt_flag:
        Host.objects.filter(ip=host_obj.ip).update(
            monitor_agent=4,
            monitor_agent_error="主机salt-agent部署失败!"
        )
        logger.error(
            "Deploy monitor agent failed because salt agent deploy failed")
        return
    monitor_manager = MonitorAgentManager(host_objs=[host_obj])
    install_flag, install_msg = monitor_manager.install()
    logger.info(
        f"Deploy monitor agent, "
        f"install_flag: {install_flag}; install_msg: {install_msg}")
    if not install_flag:
        Host.objects.filter(ip=host_obj.ip).update(
            monitor_agent=4,
            monitor_agent_error=install_msg if len(
                install_msg) < 200 else install_flag[:200]
        )
    else:
        Host.objects.filter(ip=host_obj.ip).update(monitor_agent=0)


def real_deploy_agent(host_obj, need_monitor=True):
    """
    部署主机Agent
    :param host_obj: 主机对象
    :type host_obj Host
    :param need_monitor: 是否部署monitor
    :type need_monitor bool
    :return:
    """
    logger.info(
        f"Deploy Agent for {host_obj.ip}, Params: "
        f"username: {host_obj.username}; "
        f"port: {host_obj.port}; "
        f"install_dir: {host_obj.agent_dir}!")
    _obj = Agent(
        host=host_obj.ip,
        port=host_obj.port,
        username=host_obj.username,
        password=AESCryptor().decode(host_obj.password),
        install_dir=host_obj.agent_dir
    )
    flag, message = _obj.agent_deploy()
    logger.info(
        f"Deploy Agent for {host_obj.ip}, "
        f"Res Flag: {flag}; Res Message: {message}")
    # 更新主机Agent状态，0 正常；4 部署失败
    # 使用filter查询然后使用update方法进行处理，防止多任务环境
    if flag:
        Host.objects.filter(ip=host_obj.ip).update(host_agent=0)
    else:
        Host.objects.filter(ip=host_obj.ip).update(
            host_agent=4,
            host_agent_error=str(message)[:200] if len(
                str(message)) > 200 else str(message)
        )
    # 部署监控agent
    if need_monitor:
        deploy_monitor_agent(host_obj=host_obj, salt_flag=flag)


@shared_task
def deploy_agent(host_id, need_monitor=True):
    """
    部署主机Agent
    :param host_id:
    :param need_monitor: 是否部署monitor
    :type need_monitor bool
    :return:
    """
    try:
        host_obj = Host.objects.get(id=host_id)
        host_obj.host_agent = 3
        host_obj.save()
        real_deploy_agent(host_obj=host_obj, need_monitor=need_monitor)
    except Exception as e:
        logger.error(
            f"Deploy Host Agent For {host_id} Failed with error: {str(e)};\n"
            f"detail: {traceback.format_exc()}"
        )
        Host.objects.filter(id=host_id).update(
            host_agent=4, host_agent_error=str(e))


def real_host_agent_restart(host_obj):
    """
    重启主机Agent
    :param host_obj: 主机对象
    :type host_obj Host
    :return:
    """
    logger.info(
        f"Restart Agent for {host_obj.ip}, Params: "
        f"username: {host_obj.username}; "
        f"port: {host_obj.port}; "
        f"install_dir: {host_obj.agent_dir}!")
    _obj = SSH(
        hostname=host_obj.ip,
        port=host_obj.port,
        username=host_obj.username,
        password=AESCryptor().decode(host_obj.password),
    )
    _script_path = os.path.join(
        host_obj.agent_dir, "omp_salt_agent/bin/omp_salt_agent")
    flag, message = _obj.cmd(f"bash {_script_path} restart")
    logger.info(
        f"Restart host agent for {host_obj.ip}: "
        f"get flag: {flag}; get res: {message}")
    # 使用filter查询然后使用update方法进行处理，防止多任务环境
    if flag:
        # host_obj.host_agent = 0
        Host.objects.filter(ip=host_obj.ip).update(host_agent=0)
    else:
        # host_obj.host_agent = 2
        # host_obj.host_agent_error = \
        #     str(message)[:200] if len(str(message)) > 200 else str(message)
        Host.objects.filter(ip=host_obj.ip).update(
            host_agent=2,
            host_agent_error=str(message)[:200] if len(
                str(message)) > 200 else str(message)
        )


@shared_task
def host_agent_restart(host_id):
    """
    主机Agent的重启操作
    :param host_id: 主机的id
    :return:
    """
    try:
        host_obj = Host.objects.get(id=host_id)
        real_host_agent_restart(host_obj=host_obj)
    except Exception as e:
        logger.error(
            f"Restart Host Agent For {host_id} Failed with error: {str(e)};\n"
            f"detail: {traceback.format_exc()}"
        )
        Host.objects.filter(id=host_id).update(
            host_agent=2, host_agent_error=str(e))


def real_init_host(host_obj):
    """
    初始化主机
    :param host_obj: 主机对象
    :type host_obj Host
    :return:
    """
    logger.info(f"init host Begin [{host_obj.id}]")
    _ssh = SSH(
        hostname=host_obj.ip,
        port=host_obj.port,
        username=host_obj.username,
        password=AESCryptor().decode(host_obj.password),
    )
    # 验证用户权限
    is_sudo, _ = _ssh.is_sudo()
    if not is_sudo:
        logger.error(f"init host [{host_obj.id}] failed: permission failed")
        raise Exception("permission failed")

    # 发送脚本
    init_script_name = "init_host.py"
    init_script_path = os.path.join(
        settings.BASE_DIR.parent,
        "package_hub", "_modules", init_script_name)
    script_push_state, script_push_msg = _ssh.file_push(
        file=init_script_path,
        remote_path="/tmp",
    )
    if not script_push_state:
        logger.error(f"init host [{host_obj.id}] failed: send script failed, "
                     f"detail: {script_push_msg}")
        raise Exception("send script failed")

    # 执行初始化
    is_success, script_msg = _ssh.cmd(
        f"python /tmp/{init_script_name} init_valid")
    if not (is_success and "init success" in script_msg and "valid success" in script_msg):
        logger.error(f"init host [{host_obj.id}] failed: execute init failed, "
                     f"detail: {script_push_msg}")
        raise Exception("execute failed")

    host_obj.init_status = Host.INIT_SUCCESS
    host_obj.save()
    logger.info("init host Success")


@shared_task
def init_host(host_id):
    """ 初始化主机 """
    try:
        host_obj = Host.objects.get(id=host_id)
        host_obj.init_status = Host.INIT_EXECUTING
        host_obj.save()
        real_init_host(host_obj=host_obj)
    except Exception as e:
        print(e)
        logger.error(
            f"Init Host For {host_id} Failed with error: {str(e)};\n"
            f"detail: {traceback.format_exc()}"
        )
        Host.objects.filter(id=host_id).update(
            init_status=Host.INIT_FAILED)


@shared_task
def insert_host_celery_task(host_id, init=False):
    """ 添加主机 celery 任务 """
    # 执行主机初始化
    if init:
        try:
            num = 0
            host_obj = Host.objects.filter(id=host_id).first()
            while host_obj is None and num < 10:
                host_obj = Host.objects.filter(id=host_id).first()
                time.sleep(2)
                num += 1
            if host_obj is None:
                raise Exception("Host Object not found")
            host_obj.init_status = Host.INIT_EXECUTING
            host_obj.save()
            real_init_host(host_obj=host_obj)
        except Exception as e:
            print(e)
            logger.error(
                f"Init Host For {host_id} Failed with error: {str(e)};\n"
                f"detail: {traceback.format_exc()}"
            )
            Host.objects.filter(id=host_id).update(
                init_status=Host.INIT_FAILED)
    # 部署 agent
    try:
        num = 0
        host_obj = Host.objects.filter(id=host_id).first()
        while host_obj is None and num < 10:
            host_obj = Host.objects.filter(id=host_id).first()
            time.sleep(2)
            num += 1
        if host_obj is None:
            raise Exception("Host Object not found")
        host_obj.host_agent = Host.AGENT_DEPLOY_ING
        host_obj.save()
        real_deploy_agent(host_obj=host_obj)
    except Exception as e:
        logger.error(
            f"Deploy Host Agent For {host_id} Failed with error: {str(e)};\n"
            f"detail: {traceback.format_exc()}"
        )
        Host.objects.filter(id=host_id).update(
            host_agent=Host.AGENT_DEPLOY_ERROR,
            host_agent_error=str(e))


def write_host_log(host_queryset, status, result, username):
    """ 写入主机日志 """
    log_ls = []
    for host in host_queryset:
        log_ls.append(HostOperateLog(
            username=username,
            description=f"{status}[维护模式]",
            result=result,
            host=host))
    HostOperateLog.objects.bulk_create(log_ls)


def maintenance(host_obj, entry, username):
    """ 进入 / 退出维护模式 """
    # 根据 is_maintenance 判断主机进入 / 退出维护模式
    status = "开启" if entry else "关闭"
    en_status = "open" if entry else "close"
    alert_manager = Alertmanager()
    host_ls = [{"ip": host_obj.ip}]
    if entry:
        res_ls = alert_manager.set_maintain_by_host_list(host_ls)
    else:
        res_ls = alert_manager.revoke_maintain_by_host_list(host_ls)
    # 操作失败
    if not res_ls:
        logger.error(f"host {en_status} maintain failed: {host_obj.ip}")
        # 操作失败记录写入
        write_host_log([host_obj], status, "failed", username)
    # 操作成功
    host_obj.is_maintenance = entry
    host_obj.save()
    logger.info(f"host {en_status} maintain success: {host_obj.ip}")
    # 操作成功记录写入
    write_host_log([host_obj], status, "success", username)


@shared_task
def reinstall_monitor_celery_task(host_id, username):
    """ 重新安装主机监控 celery 任务 """
    host_obj = Host.objects.filter(id=host_id).first()
    maintenance(host_obj, True, username)
    logger.info(
        f"Restart Agent for {host_obj.ip}, Params: "
        f"username: {host_obj.username}; "
        f"port: {host_obj.port}; "
        f"install_dir: {host_obj.agent_dir}!")
    _obj = SSH(
        hostname=host_obj.ip,
        port=host_obj.port,
        username=host_obj.username,
        password=AESCryptor().decode(host_obj.password),
    )
    flag, message = _obj.cmd(
        "ps -ef | grep omp_monitor_agent | grep -v grep | awk -F ' ' '{print $2}' | xargs kill -9")
    logger.info(
        f"Stop monitor agent for {host_obj.ip}: "
        f"get flag: {flag}; get res: {message}")
    # 删除目录，防止agent_dir异常保护系统
    if host_obj.agent_dir:
        monitor_dir = os.path.join(host_obj.agent_dir, "omp_monitor_agent")
        flag, message = _obj.cmd(f"rm -rf {monitor_dir}")
    logger.info(
        f"Stop monitor agent for {host_obj.ip}: "
        f"get flag: {flag}; get res: {message}")
    deploy_monitor_agent(host_obj=host_obj, salt_flag=flag)
    host_obj.refresh_from_db()
    if host_obj.monitor_agent == 4:
        maintenance(host_obj, False, username)
        return
    # 刷新prometheus服务列表监控配置,优化功能
    service_obj_list = Service.objects.filter(ip=host_obj.ip)
    detail_obj_list = []
    for service_obj in service_obj_list:
        detail_obj = service_obj.detailinstallhistory_set.first()
        if detail_obj:
            detail_obj_list.append(detail_obj)
    if len(detail_obj_list) != 0:
        add_prometheus(9999, detail_obj_list)
    maintenance(host_obj, False, username)
