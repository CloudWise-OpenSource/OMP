# -*- coding: utf-8 -*-
# Project: base
# Author: jon.liu@yunzhihui.com
# Create time: 2021-11-16 17:10
# IDE: PyCharm
# Version: 1.0
# Introduction:


class BaseUtils(object):
    """ 部署模式基础类 """

    def __init__(self, host_num, high_availability):
        """
        :param host_num: 主机数量
        :type host_num: int
        :param high_availability: 是否使用高可用
        :type high_availability: bool
        """
        self.host_num = host_num
        self.high_availability = high_availability

    def get(self):
        """
        获取部署模式
        :return:
        """
        raise NotImplementedError(f"{self}必须实现get方法!")

    def check(self, mode):
        """
        校验部署模式
        :param mode: 部署模式
        :return:
        """
        raise NotImplementedError(f"{self}必须实现check方法!")
