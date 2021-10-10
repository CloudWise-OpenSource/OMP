# -*- coding: utf-8 -*-
# Project: public_utils
# Author: jon.liu@yunzhihui.com
# Create time: 2021-10-09 19:55
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
文件md5值处理模块
"""

import os
import socket
import hashlib
import ipaddress


def get_file_md5(file_path):
    """
    获取文件的md5值
    :param file_path: 文件路径
    :return:
    """
    if not os.path.exists(file_path):
        return False, "File not exists!"
    m = hashlib.md5()
    with open(file_path, 'rb') as f_obj:
        while True:
            data = f_obj.read(4096)
            if not data:
                break
            m.update(data)
    return True, m.hexdigest()


def check_is_ip_address(value):
    """
    检查是否为ip地址
    :param value: ip地址字符串
    :return:
    """
    try:
        ipaddress.ip_address(value)
        return True, value
    except ValueError:
        return False, "not valid ip address!"


def check_ip_port(ip, port):
    """
    检查ip、port的联通性
    :param ip: 地址
    :param port: 端口
    :return:
    """
    if not check_is_ip_address(value=ip)[0]:
        return False, "ip address not correct"
    try:
        int_port = int(port)
        if int_port < 0 or int_port > 65535:
            return False, "port must be 0 ~ 65535"
    except ValueError:
        return False, "port must be 0 ~ 65535, int or string"
    sock_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock_obj.connect_ex((ip, port))
    if result == 0:
        return_tuple = (True, "success")
    else:
        return_tuple = (False, "failed")
    sock_obj.close()
    return return_tuple
