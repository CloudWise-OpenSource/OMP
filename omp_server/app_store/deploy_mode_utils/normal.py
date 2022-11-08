# -*- coding: utf-8 -*-
# Project: normal
# Author: jon.liu@yunzhihui.com
# Create time: 2021-11-23 16:06
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
普通服务的集群模式
起始为1 步长为1
"""

from app_store.deploy_mode_utils.base import BaseUtils


class NormalUtils(BaseUtils):
    """ 普通集群控制 """

    def get(self):
        """
        普通服务，返回部署模式
        :return:
        """
        if self.host_num == 1:
            return {
                "default": 1,
                "step": 0
            }
        return {
            "default": 1,
            "step": 1
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
        return True
