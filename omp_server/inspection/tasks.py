# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/10/13 6:06 下午
# Description: 巡检异步任务及定时任务

import logging
import random
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
from utils.prometheus.create_html_tar import create_html_tar
from inspection.joint_json_report import joint_json_data

# 屏蔽celery任务日志中的paramiko日志
logging.getLogger("paramiko").setLevel(logging.WARNING)
logger = get_task_logger("celery_log")


def get_hosts_data(env, hosts):
    """
    查询多主机prometheus数据，组装后进行反填
    :env: 环境queryset
    :hosts: 主机列表，例：["主机ip"]
    """
    temp_list = list()
    scan_info = {"host": len(hosts), "service": 0, "component": 0}  # 扫描统计
    tag_total_num = tag_error_num = 0  # 总指标数/异常指标数
    for instance in hosts:
        temp = dict()
        # 主机 prometheus 数据请求
        h_w_obj = HostCrawl(env=env.name, instance=instance)
        h_w_obj.run()
        _p = h_w_obj.ret
        temp['id'] = random.randint(1, 99999999)
        temp['mem_usage'] = _p.get('rate_memory')
        temp['cpu_usage'] = _p.get('rate_cpu')
        temp['disk_usage_root'] = _p.get('rate_max_disk')
        temp['report_disk_usage_data'] = _p.get('rate_data_disk')
        temp['sys_load'] = _p.get('load')
        temp['run_time'] = _p.get('run_time')
        temp['host_ip'] = instance
        temp['memory_top'] = _p.get('_s').get('memory_top', [])
        temp['cpu_top'] = _p.get('_s').get('cpu_top', [])
        temp['kernel_parameters'] = _p.get('_s').get('kernel_parameters', [])
        # 总指标数/异常指标数 计算
        tag_total_num += 23     # 当前共23个
        tag_error_num += h_w_obj.tag_error_num
        # 操作系统
        _h = Host.objects.filter(ip=instance).first()
        temp['release_version'] = _h.operate_system if _h else ''    # 操作系统
        # 配置信息
        temp['host_massage'] = f"{_h.cpu}C|{_h.memory}G|" \
                               f"{sum(_h.disk.values()) if _h.disk else '-'}G"
        temp['basic'] = [
            {"name": "IP", "name_cn": "主机IP", "value": instance},
            {"name": "hostname", "name_cn": "主机名", "value": _h.host_name},
            {"name": "kernel_version", "name_cn": "内核版本",
             "value": _p.get('_s').get('kernel_version')},
            {"name": "selinux", "name_cn": "SElinux 状态",
             "value": _p.get('_s').get('selinux')},
            {"name": "max_openfile", "name_cn": "最大打开文件数",
             "value": _p.get('total_file_descriptor')},
            {"name": "iowait", "name_cn": "IOWait",
             "value": _p.get('rate_io_wait')},
            {"name": "inode_usage", "name_cn": "inode 使用率",
             "value": {"/": _p.get('rate_inode')}},
            {"name": "now_time", "name_cn": "当前时间",
             "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
            {"name": "run_process", "name_cn": "进程数",
             "value": _p.get('_s').get('run_process')},
            {"name": "umask", "name_cn": "umask",
             "value": _p.get('_s').get('umask')},
            {"name": "bandwidth", "name_cn": "带宽",
             "value": _p.get('network_bytes_total')},
            {"name": "throughput", "name_cn": "IO", "value": _p.get('disk_io')},
            {"name": "zombies_process", "name_cn": "僵尸进程",
             "value": _p.get('_s').get('zombies_process')}
        ]
        temp_list.append(temp)

    scan_result = {
        "all_target_num": tag_total_num,
        "abnormal_target": tag_error_num,
        "healthy": f"{round((tag_error_num / tag_total_num) * 100, 2)}%"
    }
    return scan_info, scan_result, temp_list


@shared_task
def get_prometheus_data(env_id, hosts, services, history_id, report_id, handle):
    """
    异步任务：查询多巡检类型prometheus数据，组装后进行反填
    :env_id: 环境，例：Env id
    :hosts: 主机列表，例：["主机ip"]
    :services: 组件列表，例：[8]
    :history_id: 巡检历史表id，例：1
    :report_id: 巡检报告表id，例：1
    :handle: 巡检类型 service-服务巡检、host-主机巡检、deep-深度巡检
    """
    try:
        file_name = ''  # 导出文件名
        env = Env.objects.filter(id=env_id).first()
        _h = InspectionHistory.objects.filter(id=history_id).first()
        kwargs = {'history_id': history_id, 'report_id': report_id}
        if handle == 'host':
            # 主机巡检
            file_name = f"hostinspection{_h.inspection_name.split('-')[1]}"
            scan_info, scan_result, host_data = get_hosts_data(env, hosts)
            kwargs.update({
                'scan_info': scan_info, 'scan_result': scan_result,
                'host_data': host_data,
                'file_name': f"{file_name}.tar.gz"}
            )
        elif handle == 'service':
            # 组件巡检
            file_name = f"serviceinspection{_h.inspection_name.split('-')[1]}"
            scan_info, scan_result, serv_data = \
                target_service_run(env, services)
            kwargs.update({
                'scan_info': scan_info, 'scan_result': scan_result,
                'serv_data': serv_data,
                'file_name': f"{file_name}.tar.gz"}
            )
        elif handle == 'deep':
            # 主机巡检
            file_name = f"deepinspection{_h.inspection_name.split('-')[1]}"
            hosts = Host.objects.filter(env=env.id).values_list('ip', flat=True)
            if len(hosts) > 0:
                h_info, h_result, host_data = get_hosts_data(env, list(hosts))
            else:
                h_info, host_data = {'host': 0}, []
                h_result = {'all_target_num': 0, 'abnormal_target': 0}

            # 组件巡检
            services = Service.objects.filter(
                service__app_type=ApplicationHub.APP_TYPE_COMPONENT)
            services = list(services.values_list('service__id', flat=True))
            if len(services) > 0:
                s_info, s_result, serv_data = target_service_run(env, services)
            else:
                s_info, serv_data = {'service': 0}, []
                s_result = {'all_target_num': 0, 'abnormal_target': 0}

            # 合并结果
            scan_info = {"host": h_info.get('host'), "component": 0,
                         "service": s_info.get('service')}
            all_target_num = \
                h_result.get('all_target_num') + \
                s_result.get('all_target_num')
            abnormal_target = \
                h_result.get('abnormal_target') + \
                s_result.get('abnormal_target')
            scan_result = {
                "all_target_num": all_target_num,
                "abnormal_target": abnormal_target,
                "healthy":
                    f"{round((abnormal_target / all_target_num) * 100, 2)}%"
                    if all_target_num > 0 else "-"
            }
            kwargs.update({
                'scan_info': scan_info, 'scan_result': scan_result,
                'serv_data': serv_data, 'host_data': host_data,
                'file_name': f"{file_name}.tar.gz"}
            )

        # 反填巡检记录、巡检报告 数据
        back_fill(**kwargs)
        # 打包html文件
        _r = InspectionReport.objects.filter(id=report_id).first()
        _h = InspectionHistory.objects.filter(id=history_id).first()
        ret = joint_json_data(_h.inspection_type, _r, _h)
        create_html_tar(file_name, ret)
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
            if job_type in [0, 1]:
                # 2、查询环境下主机信息
                hosts = Host.objects.filter(env=env.id).values_list(
                    'ip', flat=True)
                if len(hosts) == 0:
                    logger.error(
                        f"Inspection auto task failed with error: "
                        f"ID={env.id}环境下无主机数据")
            if job_type in [0, 2]:
                # 2、查询环境下组件信息
                services = Service.objects.filter(
                    env=env,
                    service__app_type=ApplicationHub.APP_TYPE_COMPONENT)
                services = list(services.values_list('service__id', flat=True))
                if len(services) == 0:
                    logger.error(
                        f"Inspection auto task failed with error: "
                        f"ID={env.id}环境下无组件数据")

            # job_type 与 inspection_type 参数对应
            inspection_type = {0: 'deep', 1: 'host', 2: 'service'}
            # 3、组装巡检历史表入库数据，并存储入库
            now = datetime.now()
            num = InspectionHistory.objects.filter(
                start_time__year=now.year, start_time__month=now.month,
                start_time__day=now.day).count()
            his_dict = {
                'inspection_name':
                    f"{job_name}定时巡检-{now.strftime('%Y%m%d')}{num + 1}",
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
                env_id=env.id, hosts=list(hosts), services=list(services),
                history_id=his_obj.id, report_id=rep_obj.id,
                handle=inspection_type.get(job_type))
    except Exception as e:
        logger.error(
            f"Inspection auto task failed with error:"
            f" {traceback.format_exc(e)}")
