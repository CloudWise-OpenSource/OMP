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
import logging
import traceback

from celery import shared_task

from db_models.models import Host
from utils.plugin.ssh import SSH
from utils.plugin.crypto import AESCryptor
from utils.plugin.agent_util import Agent

logger = logging.getLogger("server")


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
        f"install_dir: {host_obj.data_folder}!")
    _obj = Agent(
        host=host_obj.ip,
        port=host_obj.port,
        username=host_obj.username,
        password=AESCryptor().decode(host_obj.password),
        install_dir=host_obj.data_folder
    )
    flag, message = _obj.agent_deploy()
    logger.info(
        f"Deploy Agent for {host_obj.ip}, Res Flag: {flag}; Res Message: {message}")
    # 更新主机Agent状态，0 正常；4 部署失败
    if flag:
        host_obj.host_agent = 0
    else:
        host_obj.host_agent = 4
        host_obj.host_agent_error = \
            str(message)[:200] if len(str(message)) > 200 else str(message)
    host_obj.save()


@shared_task
def deploy_agent(host_id):
    """
    部署主机Agent
    :param host_id:
    :return:
    """
    try:
        host_obj = Host.objects.get(id=host_id)
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
        f"install_dir: {host_obj.data_folder}!")
    _obj = SSH(
        hostname=host_obj.ip,
        port=host_obj.port,
        username=host_obj.username,
        password=AESCryptor().decode(host_obj.password),
    )
    _script_path = os.path.join(
        host_obj.data_folder, "omp_salt_agent/bin/omp_salt_agent")
    flag, message = _obj.cmd(f"bash {_script_path} restart")
    if flag:
        host_obj.host_agent = 0
    else:
        host_obj.host_agent = 2
        host_obj.host_agent_error = \
            str(message)[:200] if len(str(message)) > 200 else str(message)
    host_obj.save()


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
