# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/10/13 6:06 下午
# Description: 巡检异步任务及定时任务

import logging
import traceback
from datetime import datetime
from celery import shared_task
from celery.utils.log import get_task_logger
from db_models.models import Host, Env
from db_models.models import Service, ApplicationHub
from db_models.models import InspectionHistory, InspectionReport
from utils.prometheus.target_host import HostCrawl
from utils.prometheus.prometheus import back_fill
from utils.prometheus.target_service import target_service_run
# 屏蔽celery任务日志中的paramiko日志
logging.getLogger("paramiko").setLevel(logging.WARNING)
logger = get_task_logger("celery_log")


def get_hosts_data(env, hosts, history_id, report_id, target):
    """
    查询多主机prometheus数据，组装后进行反填
    :env: 环境，例：demo
    :hosts: 主机列表，例：[{"id":"主键id", "ip":"主机ip"}]
    :history_id: 巡检历史表id，例：1
    :report_id: 巡检报告表id，例：1
    :target: 自定义的实例方法，目的是统一执行实例方法并统一返回值，例：['rate_cpu', 'rate_memory']
    """
    temp_list = list()
    for instance in hosts:
        temp = dict()
        # 主机 prometheus 数据请求
        h_w_obj = HostCrawl(env=env, instance=instance.get('ip'))
        h_w_obj.run(target=target)
        temp['dynamic_data'] = h_w_obj.ret
        temp['static_data'] = {}
        h_obj = Host.objects.filter(id=instance.get('id')).first()
        if h_obj:
            temp['static_data']['operate_system'] = h_obj.operate_system  # 操作系统
            temp['static_data']['host_name'] = h_obj.host_name          # 主机名
            temp['static_data']['instance_name'] = h_obj.instance_name  # 实例名
            temp['static_data']['ip'] = h_obj.ip                  # ip地址
            temp['static_data']['host_agent'] = h_obj.host_agent  # 主机agent状态
            # 监控agent状态
            temp['static_data']['monitor_agent'] = h_obj.monitor_agent

        temp_list.append(temp)

    # 反填巡检记录、巡检报告 数据
    back_fill(history_id=history_id, report_id=report_id, host_data=temp_list)


@shared_task
def get_prometheus_data(env, hosts, services, history_id, report_id, handle):
    """
    异步任务：查询多巡检类型prometheus数据，组装后进行反填
    :env: 环境，例：Env 表的 queryset 对象
    :hosts: 主机列表，例：[{"id":"主键id", "ip":"主机ip"}]
    :services: 组件列表，例：["mysql"]
    :history_id: 巡检历史表id，例：1
    :report_id: 巡检报告表id，例：1
    :handle: 巡检类型 service-服务巡检、host-主机巡检、deep-深度巡检
    """
    try:
        if handle == 'host':
            # 主机巡检
            # target为实例方法，目的是统一执行实例方法并统一返回值
            target = ['rate_cpu', 'rate_memory', 'rate_max_disk',
                      'rate_exchange_disk', 'run_time', 'avg_load',
                      'total_file_descriptor', 'rate_io_wait',
                      'network_bytes_total', 'disk_io', 'run_status']
            get_hosts_data(env.name, hosts, history_id, report_id, target)
        elif handle == 'service':
            # 组件巡检
            target_service_run(env, services, history_id, report_id)
        elif handle == 'deep':
            # 主机巡检
            # target为实例方法，目的是统一执行实例方法并统一返回值
            target = ['rate_cpu', 'rate_memory', 'rate_max_disk',
                      'rate_exchange_disk', 'run_time', 'avg_load',
                      'total_file_descriptor', 'rate_io_wait',
                      'network_bytes_total', 'disk_io', 'run_status']
            get_hosts_data(env.name, hosts, history_id, report_id, target)
            # 组件巡检
            target_service_run(env, services, history_id, report_id)
    except Exception as e:
        logger.error(
            f"Inspection man task failed with error: {traceback.format_exc(e)}")


@shared_task
def inspection_crontab(**kwargs):
    """
    巡检 定时任务，由增加及修改接口增加的celery任务调起执行
    :kwargs: {"env": 1, "job_type": 1, "job_name": "主机巡检"}
    """
    try:
        env = kwargs.get('env')
        job_type = kwargs.get('job_type')
        job_name = kwargs.get('job_name')
        # 1、查询环境是否存在
        env = Env.objects.filter(id=env).first()
        if not env:
            logger.error(
                f"Inspection auto task failed with error: ID={env}的环境不存在")
        else:
            hosts, services = [], []
            if job_type in ['0', '1']:
                # 2、查询环境下主机信息
                hosts = Host.objects.filter(env=env.id).values('id', 'ip')
                if not hosts:
                    logger.error(
                        f"Inspection auto task failed with error: "
                        f"ID={env.id}环境下无主机数据")
            if job_type in ['0', '2']:
                # 2、查询环境下组件信息
                services = Service.objects.filter(
                    env=env,
                    service__app_type=ApplicationHub.APP_TYPE_COMPONENT)
                services = services.values('service_instance_name', 'ip',
                                           'service_port', 'service__app_name')
                if not services:
                    logger.error(
                        f"Inspection auto task failed with error: "
                        f"ID={env.id}环境下无组件数据")

            # job_type 与 inspection_type 参数对应
            inspection_type = {'0': 'deep', '1': 'host', '2': 'service'}
            # 3、组装巡检历史表入库数据，并存储入库
            now = datetime.now()
            num = InspectionHistory.objects.filter(
                start_time__year=now.year, start_time__month=now.month,
                start_time__day=now.day).count()
            his_dict = {
                'inspection_name':
                    f"{job_name}定时巡检{now.strftime('%Y%m%d')}{num+1}",
                'inspection_type': inspection_type.get(job_type),
                'inspection_status': 1, 'execute_type': 'auto',
                'inspection_operator': '定时服务',
                'hosts': list(hosts), 'services': list(services), 'env': env}
            his_obj = InspectionHistory(**his_dict)
            his_obj.save()
            # 4、组装巡检报告表数据，并存储入库
            rep_dict = {'inst_id': his_obj}
            rep_obj = InspectionReport(**rep_dict)
            rep_obj.save()
            # 5、查询prometheus数据，组装后进行反填
            get_prometheus_data(
                env=env, hosts=list(hosts), services=list(services),
                history_id=his_obj.id, report_id=rep_obj.id,
                handle=inspection_type.get(job_type))
    except Exception as e:
        logger.error(
            f"Inspection auto task failed with error:"
            f" {traceback.format_exc(e)}")
