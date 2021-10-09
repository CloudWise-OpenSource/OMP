# -*- coding: utf-8 -*-
# Project: test_celery_tasks
# Author: jon.liu@yunzhihui.com
# Create time: 2021-09-23 20:11
# IDE: PyCharm
# Version: 1.0
# Introduction:

from unittest import mock

from tests.base import BaseTest
from db_models.models import Host
from utils.plugin.salt_client import SaltClient
from promemonitor.tasks import monitor_agent_restart
from promemonitor.tasks import real_monitor_agent_restart


class MonitorAgentRestartCeleryTaskTest(BaseTest):
    """ 主机Agent的测试类 """

    def setUp(self):
        super(MonitorAgentRestartCeleryTaskTest, self).setUp()
        self.correct_host_data = {
            "instance_name": "mysql_instance_1",
            "ip": "127.0.0.10",
            "port": 36000,
            "username": "root",
            "password": "uea_xeU_d_6YHCCY7Q-e2xZolSw2z2C3KGhLY6iMdnI",
            "data_folder": "/data",
            "operate_system": "CentOS",
        }
        self.host = Host(**self.correct_host_data)
        self.host.save()

    @mock.patch.object(SaltClient, "cmd", return_value=(True, "success"))
    @mock.patch.object(SaltClient, "__init__", return_value=None)
    def test_restart_monitor_agent_success(self, *args, **kwargs):
        """
        测试重启主机Agent成功
        :return:
        """
        self.assertEqual(monitor_agent_restart(self.host.id), None)

    @mock.patch.object(
        SaltClient, "cmd", return_value=(False, "error_message"))
    @mock.patch.object(SaltClient, "__init__", return_value=None)
    def test_restart_agent_failed(self, *args, **kwargs):
        """
        测试重启主机Agent失败
        :return:
        """
        self.assertEqual(monitor_agent_restart(self.host.id), None)

    @mock.patch.object(
        SaltClient, "cmd", return_value=(False, "error_message"))
    @mock.patch.object(SaltClient, "__init__", return_value=None)
    def test_restart_agent_failed_with_wrong_id(self, *args, **kwargs):
        """
        测试重启主机Agent失败，主机id错误
        :return:
        """
        self.assertEqual(monitor_agent_restart(1000), None)

    @mock.patch.object(SaltClient, "cmd", return_value=(True, "success"))
    @mock.patch.object(SaltClient, "__init__", return_value=None)
    def test_real_restart_monitor_agent_success(self, *args, **kwargs):
        """
        测试重启主机Agent成功
        :return:
        """
        self.assertEqual(real_monitor_agent_restart(self.host), None)

    @mock.patch.object(
        SaltClient, "cmd", return_value=(False, "error_message"))
    @mock.patch.object(SaltClient, "__init__", return_value=None)
    def test_real_restart_monitor_agent_failed(self, *args, **kwargs):
        """
        测试重启主机Agent失败
        :return:
        """
        self.assertEqual(real_monitor_agent_restart(self.host), None)
