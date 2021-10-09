# -*- coding: utf-8 -*-
# Project: tasks
# Author: jon.liu@yunzhihui.com
# Create time: 2021-10-09 09:17
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
监控端异步任务
"""

import os
import logging
import traceback

from celery import shared_task
from celery.utils.log import get_task_logger

from db_models.models import Host
from utils.plugin.salt_client import SaltClient

# 屏蔽celery任务日志中的paramiko日志
logging.getLogger("paramiko").setLevel(logging.WARNING)
logger = get_task_logger("celery_log")


def real_monitor_agent_restart(host_obj):
    """
    重启监控Agent
    :param host_obj: 主机对象
    :type host_obj Host
    :return:
    """
    logger.info(
        f"Restart Monitor Agent for {host_obj.ip}, Params: "
        f"username: {host_obj.username}; "
        f"port: {host_obj.port}; "
        f"install_dir: {host_obj.agent_dir}!")
    salt_obj = SaltClient()
    _script_path = os.path.join(
        host_obj.agent_dir, "omp_monitor_agent/monitor_agent.sh")
    flag, message = salt_obj.cmd(
        target=host_obj.ip,
        command=f"bash {_script_path} restart",
        timeout=60
    )
    logger.info(
        f"Restart monitor agent for {host_obj.ip}: "
        f"get flag: {flag}; get res: {message}")
    if flag:
        Host.objects.filter(ip=host_obj.ip).update(monitor_agent=0)
    else:
        Host.objects.filter(ip=host_obj.ip).update(
            monitor_agent=2,
            monitor_agent_error=str(message)[:200] if len(
                str(message)) > 200 else str(message)
        )


@shared_task
def monitor_agent_restart(host_id):
    """
    主机Agent的重启操作
    :param host_id: 主机的id
    :return:
    """
    try:
        host_obj = Host.objects.get(id=host_id)
        real_monitor_agent_restart(host_obj=host_obj)
    except Exception as e:
        logger.error(
            f"Restart Monitor Agent For {host_id} Failed with error: "
            f"{str(e)};\ndetail: {traceback.format_exc()}"
        )
        Host.objects.filter(id=host_id).update(
            monitor_agent=2, monitor_agent_error=str(e))
