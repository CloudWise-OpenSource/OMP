"""
服务相关异步任务
"""
import json
import os

import logging

from celery import shared_task
from celery.utils.log import get_task_logger
from db_models.models import Service, ServiceHistory
from utils.plugin.salt_client import SaltClient
import time

# 屏蔽celery任务日志中的paramiko日志
logging.getLogger("paramiko").setLevel(logging.WARNING)
logger = get_task_logger("celery_log")


@shared_task
def exec_action(action, instance, operation_user):
    action_json = {
        "1": ["start", 1],
        "2": ["stop", 2],
        "3": ["restart", 3]
    }
    result_json = {
        0: "success",
        4: "failure"
    }
    try:
        service_obj = Service.objects.get(id=instance)
    except Exception as e:
        logger.error(f"service实例id，不存在{instance}:{e}")
        return None
    ip = service_obj.ip
    service_controllers = json.loads(service_obj.service_controllers)
    action = action_json.get(str(action))
    if not action:
        logger.error("action动作不合法")
        raise ValueError("action动作不合法")
    exe_action = service_controllers.get(action[0])
    if exe_action:
        salt_obj = SaltClient()
        service_obj.service_status = action[1]
        service_obj.save()
        time_array = time.localtime(int(time.time()))
        time_style = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
        status, info = salt_obj.cmd(ip, exe_action)
        result = 0 if status else 4
        service_obj.service_status = result
        service_obj.save()
        ServiceHistory.objects.create(
            username=operation_user,
            description=f"服务执行{action[0]}操作，执行脚本{exe_action}",
            result=result_json.get(result),
            created=time_style,
            service=service_obj
        )
        logger.info(f"服务操作详情:{info}")
    else:
        logger.error(f"数据库无{action[0]}动作")
        raise ValueError(f"数据库无{action[0]}动作")
