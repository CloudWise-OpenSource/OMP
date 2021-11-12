# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/11/8 2:04 下午
# Description:

from db_models.models import Service


def get_topology_data():
    """
    获取服务平面图数据
    "return :" [{'host_ip': 'ip', 'service_list': ['redis', 'mysql']}......]
    """
    topologies = dict()
    _ = Service.objects.all()
    for i in _:
        if i.ip in topologies:
            topologies[i.ip]['service_list'].append(i.service_instance_name)
        else:
            topologies[i.ip] = \
                {'host_ip': i.ip, 'service_list': [i.service_instance_name]}

    return list(topologies.values())
