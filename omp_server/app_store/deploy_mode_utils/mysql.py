# -*- coding: utf-8 -*-
# Project: mysql
# Author: jon.liu@yunzhihui.com
# Create time: 2021-11-16 16:45
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
mysql部署模式工具
"""

from app_store.deploy_mode_utils.base import BaseUtils


class MysqlUtils(BaseUtils):
    """ MySQL的部署模式 """

    def get(self):
        """
        获取mysql的部署模式
        :return:
        """
        if self.host_num == 1:
            return [
                {
                    "key": "single",
                    "name": "单实例"
                }
            ]
        elif self.high_availability and self.host_num >= 2:
            return [
                {
                    "key": "master-slave",
                    "name": "主从"
                },
                {
                    "key": "master-master",
                    "name": "主主(vip)"
                }
            ]
        return [
            {
                "key": "single",
                "name": "单实例"
            },
            {
                "key": "master-slave",
                "name": "主从"
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
        :type mode: str
        :return:
        """
        if self.host_num == 1:
            if mode == "single":
                return True
            return False
        if self.host_num >= 2 and \
                mode in ("single", "master-slave", "master-master"):
            return True
        return False
