# -*- coding: utf-8 -*-
# Project: tengine
# Author: jon.liu@yunzhihui.com
# Create time: 2021-11-23 16:26
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
tengine部署模式工具
"""

from app_store.deploy_mode_utils.base import BaseUtils


class TengineUtils(BaseUtils):
    """ tengine的部署模式 """

    def get(self):
        """
        获取tengine的部署模式
        :return:
        """
        # return {
        #     "default": 1,
        #     "step": 1
        # }
        return [
            {
                "key": "single",
                "name": "单实例"
            },
            {
                "key": "master-master",
                "name": "主主(vip)"
            }
        ]

    def check(self, mode):
        """
        检查部署模式是否符合要求
        :param mode: 部署模式
        :type mode: int
        :return:
        """
        # if mode != 1:
        #     return False
        return True
