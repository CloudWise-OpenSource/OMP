# -*- coding: utf-8 -*-
# Project: agent_stop
# Author: jon.liu@yunzhihui.com
# Create time: 2021-09-24 11:48
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
在agent启动的时候自动获取到Agent的信息，并入库更新处理
"""

import os
import sys
import logging
import django

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(os.path.dirname(
    os.path.dirname(CURRENT_DIR)), "omp_server"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "omp_server.settings")
django.setup()

from db_models.models import Host

logger = logging.getLogger("server")


def update_agent_detail(agent_id_lst):
    """
    获取agent详情的方法
    :param agent_id_lst: agent的id lst
    :return:
    """
    try:
        # 数据库中的agent是正常的，如果其id不再present列表内，则将其状态更新为'2-启动失败'
        obj_list = Host.objects.filter(
            host_agent=0).exclude(id__in=agent_id_lst).all()
        obj_list.update(host_agent=2)
        logger.info(f"失联Agent: {agent_id_lst}状态更新成功!")
    except Exception as e:
        logger.error(f"{agent_id_lst}状态更新失败: {str(e)}")


def update(agent_id_lst):
    """
    更新agent的代码
    :param agent_id_lst:
    :return:
    """
    update_agent_detail(agent_id_lst=agent_id_lst)
