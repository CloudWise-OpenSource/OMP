# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/10/22 10:04 下午
# Description:
from db_models.models import Service
from utils.prometheus.prometheus import back_fill
from utils.prometheus.target_service_mysql import ServiceMysqlCrawl


def target_service_run(env, services, history_id, report_id):
    """
    组建巡检
    :env: 环境 queryset 对象
    :services: 组件服务id 列表
    :history_id: 巡检历史表id， 作反填用
    :report_id: 巡检报告表id，作反填用
    """
    # 查询该环境下服务
    services = Service.objects.filter(env=env, service__in=services)
    services = services.values('service_instance_name', 'ip',
                               'service_port', 'service__app_name')
    ret = list()
    for i in services:
        _ = None
        if i.get('service__app_name') == 'mysql':
            _ = ServiceMysqlCrawl(env=env.name, instance=i.get('ip'))
            _.run(['run_status', 'run_time', 'slow_queries',
                   'threads_connected', 'max_connections',
                   'threads_running', 'aborted_connects', 'qps',
                   'slave_sql_running'])
        elif i.get('service_instance_name') == '**':
            # TODO
            pass

        i.update(**_.ret) if _ else ''
        ret.append(i)

    # 反填巡检记录、巡检报告 数据
    back_fill(history_id=history_id, report_id=report_id, serv_data=ret)
