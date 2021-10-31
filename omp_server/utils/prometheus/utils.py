# -*- coding: utf-8 -*-
# Project: utils
# Author: jon.liu@yunzhihui.com
# Create time: 2021-10-31 14:07
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
公共数据问题
"""

from db_models.models import Host


def get_host_data_folder(instance):
    """
    解析主机数据，获取主机磁盘分区数据
    :param instance:
    :return:
    """
    item = Host.objects.filter(ip=instance).last()
    if not item:
        return ""
    _data_folder = item.data_folder
    # {"/": 90, "/data": 100}
    _disk_info = item.disk
    if not _disk_info:
        _disk_info = Host.objects.get(id=item.id).disk
    data_path = ""
    if _disk_info and isinstance(_disk_info, dict):
        for key, _ in _disk_info.items():
            if key == "/":
                continue
            _check_data_folder = _data_folder.rstrip("/") + "/"
            _check_key = key.rstrip("/") + "/"
            if _check_data_folder.startswith(_check_key):
                data_path = key
                break
    return data_path
