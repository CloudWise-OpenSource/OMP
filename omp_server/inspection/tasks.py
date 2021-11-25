# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/10/13 6:06 下午
# Description: 巡检异步任务及定时任务

import logging
import traceback
from datetime import datetime
from celery import shared_task

from inspection.inspection_utils import send_email
from utils.prometheus.thread import MyThread
from celery.utils.log import get_task_logger
from db_models.models import Host, Env, Service, ModuleSendEmailSetting
from db_models.models import InspectionHistory, InspectionReport, ApplicationHub
from utils.prometheus.prometheus import back_fill
from utils.prometheus.target_host import target_host_thread
from utils.prometheus.target_service import target_service_run
from utils.prometheus.create_html_tar import create_html_tar
from inspection.joint_json_report import joint_json_data
from inspection.get_prometheus_risk_data import get_risk_data
from inspection.get_service_topology import get_topology_data

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
    threads = list()
    total_no = error_no = 0     # 总指标数/异常指标数
    for instance in hosts:
        total_no += 23          # 总指标数;当前共23个
        threads.append(MyThread(func=target_host_thread, args=(env, instance)))

    for t in threads:
        t.start()

    for t in threads:
        t.join()                    # 用join等待线程执行结束
        temp_list.append(t.res)     # 组装每个线程的返回值

    scan_result = {
        "all_target_num": total_no, "abnormal_target": error_no, "healthy": ""
    }
    scan_info = {"host": len(hosts), "service": 0, "component": 0}  # 扫描统计
    return scan_info, scan_result, temp_list


@shared_task
def get_prometheus_data(env_id, hosts, services, history_id, report_id, handle):
    """
    异步任务：查询多巡检类型prometheus数据，组装后进行反填
    :env_id: 环境，例：Env id
    :hosts: 主机列表，例：["主机ip"]
    :services: 服务列表，例：[8]
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
                'file_name': f"{file_name}.tar.gz"})
        elif handle == 'service':
            # 组件巡检
            file_name = f"serviceinspection{_h.inspection_name.split('-')[1]}"
            scan_info, scan_result, serv_data = \
                target_service_run(env, services)
            kwargs.update({
                'scan_info': scan_info, 'scan_result': scan_result,
                'serv_data': serv_data,
                'file_name': f"{file_name}.tar.gz"})
        elif handle == 'deep':
            # 主机巡检
            file_name = f"deepinspection{_h.inspection_name.split('-')[1]}"
            hosts = Host.objects.filter(
                env=env.id).values_list('ip', flat=True)
            if len(hosts) > 0:
                h_info, h_result, host_data = get_hosts_data(env, list(hosts))
            else:
                h_info, host_data = {'host': 0}, []
                h_result = {'all_target_num': 0, 'abnormal_target': 0}

            # 组件巡检
            _ = Service.objects.filter(
                service__app_type=ApplicationHub.APP_TYPE_COMPONENT,
                service__is_base_env=False).exclude(
                service_status__in=[5, 6, 7])
            services = list(_.values_list('id', flat=True))
            if len(services) > 0:
                s_info, s_result, serv_data = target_service_run(env, services)
            else:
                s_info, serv_data = {'service': 0}, []
                s_result = {'all_target_num': 0, 'abnormal_target': 0}

            # 主机巡检 + 组件巡检 合并结果
            scan_info = {"host": h_info.get('host'), "component": 0,
                         "service": s_info.get('service')}
            all_target_num = \
                h_result.get('all_target_num') + s_result.get('all_target_num')
            scan_result = {"all_target_num": all_target_num,
                           "abnormal_target": 0, "healthy": "-"}
            kwargs.update({
                'scan_info': scan_info, 'scan_result': scan_result,
                'serv_data': serv_data, 'host_data': host_data,
                'file_name': f"{file_name}.tar.gz"})
            # 服务平面图
            kwargs['serv_plan'] = get_topology_data()

        # 风险指标
        risk_num, risk_data = get_risk_data(handle, hosts, services)
        kwargs['risk_data'] = risk_data
        # 根据风险指标更新
        kwargs['scan_result']['abnormal_target'] = risk_num
        # 反填巡检记录、巡检报告 数据
        back_fill(**kwargs)
        # 打包html文件
        _r = InspectionReport.objects.filter(id=report_id).first()
        _h = InspectionHistory.objects.filter(id=history_id).first()
        ret = joint_json_data(_h.inspection_type, _r, _h)
        create_html_tar(file_name, ret)
        if _h.inspection_status == 2:
            email_users = ModuleSendEmailSetting.get_email_settings(
                env_id, "inspection").to_users
            send_email(_h, email_users)
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
                    logger.error(f"Inspection auto task failed with error: "
                                 f"ID={env.id}环境下无主机数据")
            if job_type in [0, 2]:
                # 2、查询环境下组件信息
                _ = Service.objects.filter(
                    service__app_type=ApplicationHub.APP_TYPE_COMPONENT,
                    service__is_base_env=False
                ).exclude(service_status__in=[5, 6, 7])
                services = list(_.values_list('id', flat=True))
                if len(services) == 0:
                    logger.error(f"Inspection auto task failed with error: "
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
                'inspection_operator': 'admin',
                'hosts': list(hosts), 'services': list(services), 'env': env}
            his_obj = InspectionHistory(**his_dict)
            his_obj.save()
            # 4、组装巡检报告表数据，并存储入库
            rep_obj = InspectionReport(**{'inst_id': his_obj})
            rep_obj.save()
            # 5、查询prometheus数据，组装后进行反填
            get_prometheus_data(
                env_id=env.id, hosts=list(hosts), services=list(services),
                history_id=his_obj.id, report_id=rep_obj.id,
                handle=inspection_type.get(job_type))
    except Exception as e:
        logger.error(f"Inspection auto task failed with error:"
                     f"{traceback.format_exc(e)}")
