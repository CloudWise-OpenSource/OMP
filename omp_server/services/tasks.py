"""
服务相关异步任务
"""

import logging

from celery import shared_task
from celery.utils.log import get_task_logger
from db_models.models import (
    Service, ServiceHistory
)
from utils.plugin.salt_client import SaltClient
import time
import json
from promemonitor.prometheus_utils import PrometheusUtils
from db_models.models import Host
from django.db.models import F

# 屏蔽celery任务日志中的paramiko日志
logging.getLogger("paramiko").setLevel(logging.WARNING)
logger = get_task_logger("celery_log")


def delete_action(service_obj):
    """
    删除逻辑
    """
    install_detail = service_obj.detailinstallhistory_set.first().install_detail_args
    dir_list = ["base_dir", "log_dir", "data_dir"]
    valida_rm = []
    for args in install_detail.get("install_args"):
        if args.get("key") in dir_list:
            dir_name = args.get("default")
            if dir_name and len(dir_name) >= 5:
                valida_rm.append(dir_name)
    result = " ".join(valida_rm)
    return result


@shared_task
def exec_action(action, instance, operation_user):
    # edit by vum: 增加服务的目标成功状态、失败状态
    action_json = {
        "1": ["start", 1, 0, 4],
        "2": ["stop", 2, 4, 0],
        "3": ["restart", 3, 0, 4],
        "4": ["delete", 4]
    }
    result_json = {
        True: "success",
        False: "failure"
    }
    try:
        service_obj = Service.objects.get(id=instance)
    except Exception as e:
        logger.error(f"service实例id，不存在{instance}:{e}")
        return None
    ip = service_obj.ip
    # service_controllers 字段为json字段类型
    service_controllers = service_obj.service_controllers
    action = action_json.get(str(action))
    if not action:
        logger.error("action动作不合法")
        raise ValueError("action动作不合法")
    if action[0] == 'delete':
        service_port = None
        if service_obj.service_port is not None:
            service_port_ls = json.loads(service_obj.service_port)
            if len(service_port_ls) > 0:
                service_port = service_port_ls[0].get("default", "")
        if service_port is not None:
            # 端口存在则删除prometheus监控的
            service_data = {
                "service_name": service_obj.service.app_name,
                "instance_name": service_obj.service_instance_name,
                "data_path": None,
                "log_path": None,
                "env": service_obj.env.name,
                "ip": ip,
                "listen_port": service_port
            }
            PrometheusUtils().delete_service(service_data)
        # 删除hosts实例个数
        if not service_obj.service.is_base_env:
            Host.objects.filter(ip=service_obj.ip).update(
                service_num=F("service_num") + 1)
        service_history_obj = ServiceHistory.objects.filter(
            service=service_obj)
        if len(service_history_obj) != 0:
            service_history_obj.delete()
        salt_obj = SaltClient()
        exe_action = service_controllers.get("stop")
        # 存在stop脚本先执行stop脚本后执行删除
        if exe_action:
            is_success, info = salt_obj.cmd(ip, exe_action, 600)
            logger.info(f"执行 [{action[0]}] 操作 {is_success}，原因: {info}")
        base_dir = delete_action(service_obj)
        # 删除安装路径
        if base_dir:
            is_success, info = salt_obj.cmd(ip, f"rm -rf {base_dir}", 600)
            logger.info(f"执行 [{action[0]}] 操作 {is_success}，原因: {info}")
        service_obj.delete()
        return None

    exe_action = service_controllers.get(action[0])
    if exe_action:
        salt_obj = SaltClient()
        service_obj.service_status = action[1]
        service_obj.save()
        time_array = time.localtime(int(time.time()))
        time_style = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
        is_success, info = salt_obj.cmd(ip, exe_action, 600)
        # TODO 服务状态维护问题，临时解决方案，休眠保持中间态
        time.sleep(35)
        service_obj.service_status = action[2] if is_success else action[3]
        service_obj.save()
        logger.info(f"执行 [{action[0]}] 操作 {is_success}，原因: {info}")
        ServiceHistory.objects.create(
            username=operation_user,
            description=f"执行 [{action[0]}] 操作",
            result=result_json.get(is_success),
            created=time_style,
            service=service_obj
        )
        logger.info(f"服务操作详情:{info}")
    else:
        logger.error(f"数据库无{action[0]}动作")
        raise ValueError(f"数据库无{action[0]}动作")
