# -*- coding: utf-8 -*-
# Project: even_num
# Author: jon.liu@yunzhihui.com
# Create time: 2021-11-23 15:55
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
偶数服务集群部署模式
偶数服务集群最小为4
"""

from app_store.deploy_mode_utils.base import BaseUtils


class EvenNumUtils(BaseUtils):
    """ 偶数集群控制 """

    def get(self):
        """
        当服务集群为偶数个时，返回部署模式
        :return:
        """
        if self.host_num < 4:
            return {
                "default": 1,
                "step": 0
            }
        return {
            "default": 4,
            "step": 2
        }

    def check(self, mode):
        """
        检查服务集群部署规则 TODO 待完善
        :param mode:
        :type mode: int
        :return:
        """
        if mode > self.host_num:
            return False
        if self.host_num < 4 and mode > 1:
            return False
        return True
