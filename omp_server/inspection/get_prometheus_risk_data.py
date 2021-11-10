# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/11/8 11:53 上午
# Description:
from db_models.models import Host, Service, ApplicationHub
from utils.prometheus.prometheus import Prometheus


def get_risk_data(handle, hosts, services):
    """
     查询 prometheus 异常数据
     :handle: deep host service
     :hosts: []
     :services: []
     """
    risks = Prometheus().query_alerts()
    hosts = hosts if hosts else []
    services = services if services else []

    host_list = []
    service_list = []
    _host = Host.objects
    _service = Service.objects
    app_name = list(ApplicationHub.objects.filter(
        id__in=services).values_list('app_name', flat=True))
    for i in risks:
        if handle in ['host', 'deep']:
            # 主机
            if handle == 'host' and\
                    i.get('labels').get('instance') not in hosts:
                continue
            if i.get('labels').get('job') == 'nodeExporter':
                _ = _host.filter(ip=i.get('labels').get('instance')).first()
                tmp = {'host_ip': i.get('labels').get('instance'),
                       'resolve_info': "-",
                       'risk_describe': i.get('annotations').get('description'),
                       'risk_level': i.get('labels').get('severity'),
                       'system': _.operate_system if _ else '-'}
                host_list.append(tmp)
        if handle in ['service', 'deep']:
            # 组件
            if handle == 'service' and \
                    i.get('labels').get('job').replace('Exporter', '') \
                    not in app_name:
                continue
            if i.get('labels').get('job') != 'nodeExporter':
                tmp = {'host_ip': i.get('labels').get('instance'),
                       'resolve_info': "-",
                       'risk_describe': i.get('annotations').get('description'),
                       'risk_level': i.get('labels').get('severity'),
                       'service_name': i.get('labels').get('job'),
                       'service_port': '-'}
                service_list.append(tmp)

    risk_num = len(host_list) + len(service_list)
    return risk_num, {'host_list': host_list, 'service_list': service_list}
