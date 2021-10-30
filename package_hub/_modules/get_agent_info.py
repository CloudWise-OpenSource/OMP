# -*- coding: utf-8 -*-
# Project: get_agent_info
# Author: jon.liu@yunzhihui.com
# Create time: 2020-12-31 19:04
# IDE: PyCharm
# Version: 1.0
# Introduction:

import math
import socket

import psutil
import salt.utils.network


def byte_to_gb(b):
    """
    byte 转 gb
    :param b:
    :return:
    """
    if not isinstance(b, int):
        return 0
    return math.ceil(b / 1024 / 1024 / 1024)


def get_cpu_info():
    """
    获取cpu个数信息
    :return:
    """
    return psutil.cpu_count()


def get_memory_detail():
    """
    获取内存使用信息
    :return:
    """
    memory = psutil.virtual_memory()
    memory_total = int(memory.total)
    memory_used = int(memory.used)
    memory_free = int(memory.free)
    memory_available = int(memory.available)
    return {
        "memory_total": byte_to_gb(memory_total),
        "memory_used": byte_to_gb(memory_used),
        "memory_free": byte_to_gb(memory_free),
        "memory_available": byte_to_gb(memory_available)
    }


def get_disk_detail():
    """
    获取磁盘使用信息
    :return:
    """
    all_partitions = psutil.disk_partitions()
    ret_dic = {}
    for item in all_partitions:
        # 当过滤到挂载盘中有以下关键字时，跳过此磁盘的检查
        if "docker/overlay" in item.mountpoint or \
                "docker/container" in item.mountpoint or \
                "/boot" == item.mountpoint or \
                item.mountpoint.startswith("/run/media"):
            continue
        disk_usage = psutil.disk_usage(item.mountpoint)
        _disk_total = byte_to_gb(int(disk_usage.total))
        ret_dic[item.mountpoint] = _disk_total
    return ret_dic


def get_hostname():
    """
    获取主机名信息
    :return:
    """
    return socket.gethostname()


def get_ip():
    """
    获取ip地址信息
    :return:
    """
    all_ips = salt.utils.network.ip_addrs()
    for item in all_ips:
        if item.startswith("127"):
            continue
        return item


def get_agent_info():
    """
    获取agent信息
    :return:
    """
    return {
        "cpu": get_cpu_info(),
        "disk": get_disk_detail(),
        "memory": get_memory_detail(),
        "hostname": get_hostname(),
        "ip": get_ip()
    }


if __name__ == '__main__':
    print(get_agent_info())
