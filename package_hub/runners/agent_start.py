# -*- coding: utf-8 -*-
# Project: agent_start
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
from utils.plugin.salt_client import SaltClient

logger = logging.getLogger("server")


def get_agent_detail(target):
    """
    获取agent详情的方法
    :param target: agent的id
    :return:
    """
    try:
        salt_obj = SaltClient()
        _flag, res = salt_obj.fun(target=target, fun="saltutil.sync_modules")
        logger.info(f"同步模块返回标志: {_flag}; 返回值: {res}")
        _flag, res = salt_obj.fun(target, "get_agent_info.get_agent_info")
        if _flag is not True:
            logger.error(f"获取target: {target} 详情失败")
            return
        logger.info(f"获取{target}详情成功: {res}")
        obj_list = Host.objects.filter(ip=target)
        if obj_list:
            obj_list.update(
                memory=res.get("memory", {}).get("memory_total", 0),
                cpu=res.get("cpu", 0),
                disk=res.get("disk", {}),
                host_agent=0,
                host_name=res.get("hostname")
            )
            logger.info(f"更新{target}状态成功!")
        # TODO 暂时屏蔽自动入库逻辑，待设计完善后再进行补充
        # else:
        #     Host(
        #         ip=target,
        #         memory=res.get("memory", {}).get("memory_total", 0),
        #         cpu=res.get("cpu", 0),
        #         disk=res.get("disk", {}),
        #         host_agent=0,
        #         host_name=res.get("hostname")
        #     ).save()
        #     logger.info(f"插入{target}状态成功!")
    except Exception as e:
        logger.error(f"{target}状态更新失败: {str(e)}")


def update(agent_id):
    """
    更新agent的代码
    :param agent_id:
    :return:
    """
    get_agent_detail(target=agent_id)
