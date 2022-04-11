# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/10/22 10:04 下午
# Description:
import json
import random
import logging
import traceback

from db_models.models import Service
from utils.prometheus.thread import MyThread
from utils.prometheus.target_service_jvm_base import ServiceBase
from utils.prometheus.target_service_arangodb import ServiceArangodbCrawl
from utils.prometheus.target_service_beanstalk import ServiceBeanstalkCrawl
from utils.prometheus.target_service_clickhouse import ServiceClickhouseCrawl
from utils.prometheus.target_service_elasticsearch import ServiceElasticsearchCrawl
from utils.prometheus.target_service_flink import ServiceFlinkCrawl
from utils.prometheus.target_service_gotty import ServiceGottyCrawl
from utils.prometheus.target_service_grafana import ServiceGrafanaCrawl
from utils.prometheus.target_service_hadoop import ServiceHadoopCrawl
from utils.prometheus.target_service_httpd import ServiceHttpdCrawl
from utils.prometheus.target_service_ignite import ServiceIgniteCrawl
from utils.prometheus.target_service_ntpd import ServiceNtpdCrawl
from utils.prometheus.target_service_postgresql import ServicePostgresqlCrawl
from utils.prometheus.target_service_prometheus import ServicePrometheusCrawl
from utils.prometheus.target_service_tengine import ServiceTengineCrawl
from utils.prometheus.target_service_mysql import ServiceMysqlCrawl
from utils.prometheus.target_service_redis import ServiceRedisCrawl
from utils.prometheus.target_service_kafka import ServiceKafkaCrawl
from utils.prometheus.target_service_nacos import ServiceNacosCrawl
from utils.prometheus.target_service_rocketmq import ServiceRocketmqCrawl
from utils.prometheus.target_service_zookeeper import ServiceZookeeperCrawl

logger = logging.getLogger("server")


open_source_class_dict = {
    "arangodb": ServiceArangodbCrawl,
    "beanstalk": ServiceBeanstalkCrawl,
    "clickhouse": ServiceClickhouseCrawl,
    "elasticsearch": ServiceElasticsearchCrawl,
    "flink": ServiceFlinkCrawl,
    "gotty": ServiceGottyCrawl,
    "grafana": ServiceGrafanaCrawl,
    "hadoop": ServiceHadoopCrawl,
    "httpd": ServiceHttpdCrawl,
    "ignite": ServiceIgniteCrawl,
    "kafka": ServiceKafkaCrawl,
    "mysql": ServiceMysqlCrawl,
    "nacos": ServiceNacosCrawl,
    "ntpd": ServiceNtpdCrawl,
    "postgreSql": ServicePostgresqlCrawl,
    "prometheus": ServicePrometheusCrawl,
    "redis": ServiceRedisCrawl,
    "rocketmq": ServiceRocketmqCrawl,
    "tengine": ServiceTengineCrawl,
    "zookeeper": ServiceZookeeperCrawl
}


def get_port_and_status(i):
    """
    组建巡检：统一获取每个服务的端口信息及服务状态
    从target_service_run方法拆出来一段
    """
    # 组装端口
    service_port, service_ports = '', []
    ports = json.loads(i.get('service_port')) if i.get('service_port') else []
    for p in ports:
        service_ports.append(p.get('default'))
        if p.get('key') == 'service_port':
            service_port = p.get('default')

    # 组装服务状态
    serv_status = {0: "正常", 1: "启动中", 2: "停止中", 3: "重启中", 4: "停止"}
    service_status = serv_status.get(i.get('service_status'))
    return [service_port, list(set(service_ports)), service_status]


def _joint(i, ret, basics, service_port, service_ports, service_status):
    """
     组件巡检 统一数据组装
    "desc: i" server表基础信息
    "desc: ret" 各服务基础数据,字典类型
    "desc: basic" 各服务拓展数据,列表类型
    "desc: service_port" 服务端口
    "desc: service_status" 服务状态
    "desc: service_ports" 服务全部的端口
    """
    basic = [
        {"name": "port_status", "name_cn": "监听端口", "value": service_ports},
        {"name": "IP", "name_cn": "IP地址", "value": i.get('ip')},
    ] + basics
    return {
        'id': random.randint(1, 99999999),
        'host_ip': i.get('ip'),
        'cluster_name': "-",
        "cpu_usage": ret.get('cpu_usage', '-'),
        "log_level": ret.get('log_level', '-'),
        "mem_usage": ret.get('mem_usage', '-'),
        "run_time": ret.get('run_time', '-'),
        "service_name": i.get('service_instance_name'),
        "service_port": service_port,
        "service_status": service_status,
        "service_type": "2",
        "basic": basic
    }


def target_service_thread(env, i):
    """
    组件数据采集,把顺序执行的代码拷贝出来-多线程执行
    :param env: 环境表对象
    :param i: 服务表基础数据(端口/服务名/app_name...)
    """
    # 获取每个服务的端口信息及服务状态
    _port_status = get_port_and_status(i)
    if i.get('service__app_monitor', {}).get('type') == 'JavaSpringBoot':
        _ = ServiceBase(env.name, i.get('ip'),
                        f'{i.get("service__app_name")}Exporter')
        _.run()
        tag_total_num = _.metric_num  # 总指标数累加
        tmp = _joint(i, _.ret, _.basic, *_port_status)
    # elif i.get('service__app_monitor', {}).get('type') == 'open_source':  # TODO
    else:
        try:
            crawl_class = open_source_class_dict.get(
                i.get("service__app_name"))
            if not crawl_class:
                return [0, _joint(i, {}, [], *_port_status)]
            _ = crawl_class(env=env.name, instance=i.get('ip'))
            _.run()
            tag_total_num = _.metric_num  # 总指标数累加
            tmp = _joint(i, _.ret, _.basic, *_port_status)
        except Exception as e:
            logger.error(f'服务巡检失败，详情为{traceback.format_exc(e)}')
            tag_total_num = 0  # 总指标数 计算
            ret, basics = {}, []
            tmp = _joint(i, ret, basics, *_port_status)
    # else:
    #     tag_total_num = 0   # 总指标数 计算
    #     ret, basics = {}, []
    #     tmp = _joint(i, ret, basics, *_port_status)

    return [tag_total_num, tmp]


def target_service_run(env, services):
    """
    组建巡检，多线程执行
    :env: 环境 queryset 对象
    :services: 服务id 列表
    """
    tmp_list = list()
    threads = list()
    total_no = error_no = 0  # 总指标数、异常指标数
    # 查询该环境下服务
    services = Service.objects.filter(env=env, id__in=services)
    services = services.values(
        'service_instance_name', 'ip', 'service_port', 'service__app_name',
        'service__app_install_args', 'service_status', 'service__app_monitor')
    for i in services:
        threads.append(MyThread(func=target_service_thread, args=(env, i)))

    for t in threads:
        t.start()

    for t in threads:
        t.join()  # 用join等待线程执行结束
        if not t.res:
            continue
        total_no += t.res[0]
        tmp_list.append(t.res[1])  # 等线程结束，回收返回值

    # 扫描统计
    scan_info = {"host": 0, "service": len(services), "component": 0}
    # 分析结果
    scan_result = {
        "all_target_num": total_no, "abnormal_target": error_no, "healthy": "-"
    }
    return scan_info, scan_result, tmp_list
