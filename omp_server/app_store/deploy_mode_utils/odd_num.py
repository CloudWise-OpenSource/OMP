# -*- coding: utf-8 -*-
# Project: odd_num
# Author: jon.liu@yunzhihui.com
# Create time: 2021-11-23 15:55
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
奇数服务集群部署模式
奇数服务集群最小为3
"""

from app_store.deploy_mode_utils.base import BaseUtils


class OddNumUtils(BaseUtils):
    """ 奇数集群控制 """

    def get(self):
        """
        当服务集群为奇数个时，返回部署模式
        :return:
        """
        if self.host_num < 3:
            return {
                "default": 1,
                "step": 0
            }
        return {
            "default": 3,
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
        if self.host_num < 3 and mode > 1:
            return False
        return True
