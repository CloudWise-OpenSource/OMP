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
import subprocess


def local_cmd(command):
    """
    执行本地shell命令
    :param command: 执行命令
    :return: (stdout, stderr, ret_code)
    """
    p = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True
    )
    stdout, stderr = p.communicate()
    _out, _err, _code = \
        stdout.decode("utf8"), stderr.decode("utf8"), p.returncode
    return _out, _err, _code


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


class DurationTime:

    def __init__(self, seconds):
        self.second = seconds
        self.minute = self.hour = self.day = 0

    def analysis_day(self):
        day, hour = divmod(self.hour, 24)
        setattr(self, "hour", hour)
        setattr(self, "day", day)

    def analysis_hour(self):
        hour, minute = divmod(self.minute, 60)
        setattr(self, "minute", minute)
        setattr(self, "hour", hour)

    def analysis_minute(self):
        minute, second = divmod(self.second, 60)
        setattr(self, "second", second)
        setattr(self, "minute", minute)

    def __call__(self, *args, **kwargs):
        for key in ["minute", "hour", "day"]:
            getattr(self, f"analysis_{key}")()
            if not getattr(self, key):
                return self
        return self


def timedelta_strftime(timedelta):
    """
    四舍五入格式化timedelta
    :param timedelta: <class datetime.timedelta>
    :return: "XX天XX时XX分XX秒"
    """
    seconds = round(timedelta.total_seconds())
    duration = DurationTime(seconds)()
    en_zh = [("day", "天"), ("hour", "时"), ("minute", "分"), ("second", "秒")]
    strftime = ""
    for en, zh in en_zh:
        if strftime:
            strftime += f"{getattr(duration, en)}{zh}"
        elif not strftime and getattr(duration, en):
            strftime += f"{getattr(duration, en)}{zh}"
    return strftime
