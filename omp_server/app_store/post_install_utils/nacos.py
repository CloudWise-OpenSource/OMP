# -*- coding: utf-8 -*-
# Project: nacos
# Author: jon.liu@yunzhihui.com
# Create time: 2021-12-06 11:48
# IDE: PyCharm
# Version: 1.0
# Introduction:

import logging

from db_models.models import (
    Service, DetailInstallHistory
)
from app_store.post_install_utils.base import BasePostInstallUtils

logger = logging.getLogger("server")


class Nacos(BasePostInstallUtils):
    """ nacos更新类 """

    def run(self):
        """
        运行
        :return:
        """
        logger.info("execute Nacos post install action!")
        # nacos仅取一个节点即可
        nacos_obj = Service.objects.filter(
            service__app_name="nacos"
        ).last()
        if not nacos_obj:
            return True, "success"
        detail_obj = DetailInstallHistory.objects.filter(
            service=nacos_obj
        ).last()
        if not detail_obj:
            return True, "success"
        self.send_json(detail_obj=detail_obj)
        # 执行 install.py
        install_flag, install_msg = self.execute_install(
            detail_obj=detail_obj
        )
        logger.info(f"execute nacos install: {install_flag};{install_msg}")
        if not install_flag:
            return False, f"execute install failed: {install_msg}"
        # 执行 init.py
        init_flag, init_msg = self.execute_init(
            detail_obj=detail_obj
        )
        logger.info(f"execute nacos install: {init_flag};{init_msg}")
        if not init_flag:
            return False, f"execute init failed: {init_msg}"
        # 执行 restart
        # restart_flag, restart_msg = self.execute_restart(
        #     detail_obj=detail_obj
        # )
        # logger.info(f"execute nacos install: {restart_flag};{restart_msg}")
        # if not restart_flag:
        #     return False, f"restart nacos failed: {restart_msg}"
        logger.info("Execute post install action for nacos success!")
        return True, "success"
