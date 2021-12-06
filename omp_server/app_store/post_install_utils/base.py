# -*- coding: utf-8 -*-
# Project: base
# Author: jon.liu@yunzhihui.com
# Create time: 2021-12-06 13:58
# IDE: PyCharm
# Version: 1.0
# Introduction:

import os

from utils.plugin.salt_client import SaltClient
from db_models.models import Host


class BasePostInstallUtils(object):
    """ 执行安装后动作的基础类 """

    def __init__(self, main_obj):
        self.main_obj = main_obj
        self.json_path = os.path.join(
            "data_files", f"{self.main_obj.operation_uuid}.json"
        )

    def send_json(self, detail_obj):
        """
        发送json文件
        :param detail_obj:
        :return:
        """
        target_ip = detail_obj.service.ip
        data_folder = Host.objects.filter(ip=target_ip).last().data_folder
        target_path = os.path.join(
            data_folder, "omp_packages",
            f"{self.main_obj.operation_uuid}.json")
        salt_obj = SaltClient()
        return salt_obj.cp_file(
            target=target_ip,
            source_path=self.json_path,
            target_path=target_path
        )

    def execute_install(self, detail_obj):
        """
        执行安装脚本
        :param detail_obj:
        :return:
        """
        target_ip = detail_obj.service.ip
        install_path = self.get_install_path(detail_obj=detail_obj)
        if not install_path:
            return True, "no need execute install!"
        data_folder = Host.objects.filter(ip=target_ip).last().data_folder
        target_json_path = os.path.join(
            data_folder, "omp_packages",
            f"{self.main_obj.operation_uuid}.json")
        salt_obj = SaltClient()
        return salt_obj.cmd(
            target=target_ip,
            command=f"python {install_path} --local_ip={target_ip} "
                    f"--data_json={target_json_path}",
            timeout=60
        )

    def execute_init(self, detail_obj):
        """
        执行安装脚本
        :param detail_obj:
        :return:
        """
        target_ip = detail_obj.service.ip
        init_path = self.get_init_path(detail_obj=detail_obj)
        if not init_path:
            return True, "no need execute init!"
        data_folder = Host.objects.filter(ip=target_ip).last().data_folder
        target_json_path = os.path.join(
            data_folder, "omp_packages",
            f"{self.main_obj.operation_uuid}.json")
        salt_obj = SaltClient()
        return salt_obj.cmd(
            target=target_ip,
            command=f"python {init_path} --local_ip={target_ip} "
                    f"--data_json={target_json_path}",
            timeout=60
        )

    def execute_restart(self, detail_obj):
        """
        执行安装脚本
        :param detail_obj:
        :return:
        """
        restart_path = self.get_restart_path(detail_obj=detail_obj)
        if not restart_path:
            return True, "no need execute restart"
        salt_obj = SaltClient()
        return salt_obj.cmd(
            target=detail_obj.service.ip,
            command=f"bash {restart_path}",
            timeout=60
        )

    def get_install_path(self, detail_obj):
        """
        获取安装脚本路径
        :param detail_obj:
        :return:
        """
        return detail_obj.service.service_controllers.get("install")

    def get_init_path(self, detail_obj):
        """
        获取安装脚本路径
        :param detail_obj:
        :return:
        """
        return detail_obj.service.service_controllers.get("init")

    def get_restart_path(self, detail_obj):
        """
        获取安装脚本路径
        :param detail_obj:
        :return:
        """
        return detail_obj.service.service_controllers.get("restart")
