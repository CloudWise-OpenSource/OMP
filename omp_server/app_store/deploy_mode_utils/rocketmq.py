# -*- coding: utf-8 -*-
# Project: mysql
# Author: jon.liu@yunzhihui.com
# Create time: 2021-11-16 16:45
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
rocketmq部署模式工具
"""

from app_store.deploy_mode_utils.base import BaseUtils


class RocketmqUtils(BaseUtils):
    """ Rocket的部署模式 """

    def get(self):
        """
        获取mysql的部署模式
        :return:
        """
        if self.host_num == 1:
            return {
                "default": 1,
                "step": 0
            }
        if self.high_availability:
            if self.host_num >= 2:
                return {
                    "default": 2,
                    "step": 2
                }
            return {
                "default": 1,
                "step": 0
            }
        return {
            "default": 1,
            "step": 0
        }

    def check(self, mode):
        """
        检查部署模式是否符合要求
        :param mode: 部署模式
        :type mode: str
        :return:
        """
        return True
