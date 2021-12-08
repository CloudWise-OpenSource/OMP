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

from db_models.models import Host
from utils.plugin.ssh import SSH
from utils.plugin.monitor_agent import MonitorAgentManager
from utils.plugin.crypto import AESCryptor
from utils.plugin.agent_util import Agent

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


def real_deploy_agent(host_obj):
    """
    部署主机Agent
    :param host_obj: 主机对象
    :type host_obj Host
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
    deploy_monitor_agent(host_obj=host_obj, salt_flag=flag)


@shared_task
def deploy_agent(host_id):
    """
    部署主机Agent
    :param host_id:
    :return:
    """
    try:
        host_obj = Host.objects.get(id=host_id)
        host_obj.host_agent = 3
        host_obj.save()
        real_deploy_agent(host_obj=host_obj)
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
