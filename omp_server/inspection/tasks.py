# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/10/13 6:06 下午
# Description: 巡检视图

import logging
import traceback
from datetime import datetime
from celery import shared_task
from celery.utils.log import get_task_logger

from db_models.models import Host
from inspection.models import InspectionHistory, InspectionReport
from utils.prometheus.target_host import HostCrawl
# 屏蔽celery任务日志中的paramiko日志
logging.getLogger("paramiko").setLevel(logging.WARNING)
logger = get_task_logger("celery_log")


@shared_task
def get_prometheus_host_data(env, hosts, history_id, report_id, target):
    try:
        temp_list = list()
        for instance in hosts:
            temp = dict()
            # 主机 prometheus 数据请求
            h_w_obj = HostCrawl(env=env, instance=instance)
            h_w_obj.run(target=target)
            temp['dynamic_data'] = h_w_obj.ret
            temp['static_data'] = {}
            h_obj = Host.objects.filter(id=instance.get('id')).first()
            if h_obj:
                temp['static_data']['operate_system'] = h_obj.operate_system     # 操作系统
                temp['static_data']['host_name'] = h_obj.host_name               # 主机名
                temp['static_data']['instance_name'] = h_obj.instance_name       # 实例名
                temp['static_data']['ip'] = h_obj.ip                             # ip地址
                temp['static_data']['host_agent'] = h_obj.host_agent             # 主机agent状态
                temp['static_data']['monitor_agent'] = h_obj.monitor_agent       # 监控agent状态

            temp_list.append(temp)

        # 反填巡检历史记录InspectionHistory表，结束时间end_time、巡检用时duration字段
        now = datetime.now()
        his_obj = InspectionHistory.objects.filter(id=history_id)
        his_obj.update(end_time=now, duration=(now - his_obj[0].start_time).seconds)
        # 反填巡检报告InspectionReport表，主机列表host_data字段
        InspectionReport.objects.filter(id=report_id).update(host_data=temp_list)
    except Exception as e:
        logger.error(f"Failed with error: {traceback.format_exc(e)}")
