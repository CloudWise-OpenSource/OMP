# -*- coding: utf-8 -*-
# Project: test_monitor_agent
# Author: jon.liu@yunzhihui.com
# Create time: 2021-10-07 15:47
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
测试monitor agent脚本
"""

import os
from unittest import mock

from tests.base import BaseTest
from db_models.models import Host
from omp_server.settings import PROJECT_DIR
from utils.plugin.salt_client import SaltClient
from utils.plugin.monitor_agent import MonitorAgentManager


class MonitorAgentTest(BaseTest):
    """ 主机Agent的测试类 """

    def setUp(self):
        super(MonitorAgentTest, self).setUp()
        self.correct_host_data = {
            "instance_name": "mysql_instance_1",
            "ip": "127.0.0.10",
            "port": 36000,
            "username": "root",
            "password": "root_password",
            "data_folder": "/data",
            "operate_system": "CentOS",
        }
        Host(**self.correct_host_data).save()
        self.host_obj_lst = list(Host.objects.all())
        self.agent_path = os.path.join(
            PROJECT_DIR, "package_hub/omp_monitor_agent.tar.gz")
        if not os.path.exists(self.agent_path):
            with open(self.agent_path, "w") as fp:
                fp.write("test")
        self.monitor_agent_name = "omp_monitor_agent.tar.gz"

    def _install(self):
        manager = MonitorAgentManager(host_objs=self.host_obj_lst)
        manager.monitor_agent_package_name = self.monitor_agent_name
        return manager.install()

    @mock.patch.object(SaltClient, "cp_file", return_value=(True, "success"))
    @mock.patch.object(SaltClient, "cmd", return_value=(True, "success"))
    def test_package_do_not_exist(self, *args, **kwargs):
        """
        测试monitor agent安装包不存在场景
        :param args:
        :param kwargs:
        :return:
        """
        manager = MonitorAgentManager(host_objs=self.host_obj_lst)
        manager.monitor_agent_package_name = ""
        flag, msg = manager.install()
        self.assertEqual(flag, False)

    @mock.patch.object(SaltClient, "cp_file", return_value=(False, "success"))
    @mock.patch.object(SaltClient, "cmd", return_value=(True, "success"))
    def test_install_failed_send_package(self, *args, **kwargs):
        """
        测试成功安装monitor agent场景
        :param args:
        :param kwargs:
        :return:
        """
        flag, msg = self._install()
        self.assertEqual(flag, False)

    @mock.patch.object(SaltClient, "cp_file", return_value=(True, "success"))
    @mock.patch.object(SaltClient, "cmd", return_value=(False, "success"))
    def test_install_failed_cmd(self, *args, **kwargs):
        """
        测试成功安装monitor agent场景
        :param args:
        :param kwargs:
        :return:
        """
        self.assertEqual(self._install()[0], False)

    @mock.patch.object(SaltClient, "cp_file", return_value=(True, "success"))
    @mock.patch.object(SaltClient, "cmd", return_value=(True, "success"))
    def test_install_success(self, *args, **kwargs):
        """
        测试成功安装monitor agent场景
        :param args:
        :param kwargs:
        :return:
        """
        flag, msg = self._install()
        self.assertEqual(flag, True)

    @mock.patch.object(SaltClient, "cmd", return_value=(False, "success"))
    def test_uninstall_failed(self, *args, **kwargs):
        """
        测试卸载失败场景
        :param args:
        :param kwargs:
        :return:
        """
        manager = MonitorAgentManager(host_objs=self.host_obj_lst)
        manager.monitor_agent_package_name = self.monitor_agent_name
        self.assertEqual(manager.uninstall()[0], False)

    @mock.patch.object(SaltClient, "cmd", return_value=(True, "success"))
    def test_uninstall_success(self, *args, **kwargs):
        """
        测试卸载失败场景
        :param args:
        :param kwargs:
        :return:
        """
        manager = MonitorAgentManager(host_objs=self.host_obj_lst)
        manager.monitor_agent_package_name = self.monitor_agent_name
        self.assertEqual(manager.uninstall()[0], True)
