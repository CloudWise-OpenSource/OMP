# -*- coding: utf-8 -*-
# Project: tengine
# Author: jon.liu@yunzhihui.com
# Create time: 2021-12-06 11:47
# IDE: PyCharm
# Version: 1.0
# Introduction:

import logging

from db_models.models import (
    Service, DetailInstallHistory
)
from app_store.post_install_utils.base import BasePostInstallUtils

logger = logging.getLogger("server")


class Tengine(BasePostInstallUtils):
    """ tengine更新类 """

    def run(self):
        """
        运行
        :return:
        """
        logger.info("execute Tengine post install action!")
        # nacos仅取一个节点即可
        tengine_obj_queryset = Service.objects.filter(
            service__app_name="tengine"
        )
        if not tengine_obj_queryset.exists():
            return True, "success"
        detail_obj_queryset = DetailInstallHistory.objects.filter(
            service__in=list(tengine_obj_queryset)
        )
        if not detail_obj_queryset.exists():
            return True, "success"
        for item in detail_obj_queryset:
            # 发送json文件
            self.send_json(detail_obj=item)
            # 执行 install.py
            install_flag, install_msg = self.execute_install(
                detail_obj=item
            )
            logger.info(
                f"execute tengine install: {install_flag};{install_msg}")
            if not install_flag:
                return False, f"execute install failed: {install_msg}"
            # 执行 restart
            restart_flag, restart_msg = self.execute_restart(
                detail_obj=item
            )
            logger.info(
                f"execute tengine install: {restart_flag};{restart_msg}")
            if not restart_flag:
                return False, f"restart tengine failed: {restart_msg}"
            logger.info("Execute post install action for tengine success!")
            return True, "success"
