# -*- coding: utf-8 -*-
# Project: test_celery_tasks
# Author: jon.liu@yunzhihui.com
# Create time: 2021-09-23 20:11
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
主机相关异步任务单元测试
"""

from unittest import mock

from tests.base import BaseTest
from utils.plugin.agent_util import Agent
from utils.plugin.ssh import SSH
from utils.plugin.monitor_agent import MonitorAgentManager
from hosts import tasks
from hosts.tasks import deploy_agent
from hosts.tasks import host_agent_restart
from hosts.tasks import real_deploy_agent
from hosts.tasks import real_host_agent_restart
from hosts.tasks import deploy_monitor_agent
from db_models.models import Host


class HostCeleryTaskTest(BaseTest):
    """ 主机Agent的测试类 """

    def setUp(self):
        super(HostCeleryTaskTest, self).setUp()
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

    @mock.patch.object(Agent, "agent_deploy", return_value=(True, "success"))
    @mock.patch.object(tasks, "deploy_monitor_agent", return_value=None)
    def test_deploy_agent_success(self, *args, **kwargs):
        """
        测试部署Agent成功
        :return:
        """
        self.assertEqual(deploy_agent(self.host.id), None)

    @mock.patch.object(
        Agent, "agent_deploy", return_value=(False, "error_message"))
    @mock.patch.object(tasks, "deploy_monitor_agent", return_value=None)
    def test_deploy_agent_failed(self, *args, **kwargs):
        """
        测试部署Agent失败
        :return:
        """
        self.assertEqual(deploy_agent(self.host.id), None)

    @mock.patch.object(
        Agent, "agent_deploy", return_value=(False, "error_message"))
    @mock.patch.object(tasks, "deploy_monitor_agent", return_value=None)
    def test_deploy_agent_failed_with_wrong_id(self, *args, **kwargs):
        """
        测试部署Agent失败，主机id错误
        :return:
        """
        self.assertEqual(deploy_agent(1000), None)

    @mock.patch.object(Agent, "agent_deploy", return_value=(True, "success"))
    @mock.patch.object(tasks, "deploy_monitor_agent", return_value=None)
    def test_real_deploy_agent_success(self, *args, **kwargs):
        """
        测试部署Agent成功
        :return:
        """
        self.assertEqual(real_deploy_agent(self.host), None)

    @mock.patch.object(
        Agent, "agent_deploy", return_value=(False, "error_message"))
    @mock.patch.object(tasks, "deploy_monitor_agent", return_value=None)
    def test_real_deploy_agent_failed(self, *args, **kwargs):
        """
        测试部署Agent失败
        :return:
        """
        self.assertEqual(real_deploy_agent(self.host), None)

    @mock.patch.object(SSH, "cmd", return_value=(True, "success"))
    def test_restart_agent_success(self, agent_deploy):
        """
        测试重启主机Agent成功
        :return:
        """
        self.assertEqual(host_agent_restart(self.host.id), None)

    @mock.patch.object(SSH, "cmd", return_value=(False, "error_message"))
    def test_restart_agent_failed(self, agent_deploy):
        """
        测试重启主机Agent失败
        :return:
        """
        self.assertEqual(host_agent_restart(self.host.id), None)

    @mock.patch.object(SSH, "cmd", return_value=(False, "error_message"))
    def test_restart_agent_failed_with_wrong_id(self, agent_deploy):
        """
        测试重启主机Agent失败，主机id错误
        :return:
        """
        self.assertEqual(host_agent_restart(1000), None)

    @mock.patch.object(SSH, "cmd", return_value=(True, "success"))
    def test_real_restart_agent_success(self, agent_deploy):
        """
        测试重启主机Agent成功
        :return:
        """
        self.assertEqual(real_host_agent_restart(self.host), None)

    @mock.patch.object(SSH, "cmd", return_value=(False, "error_message"))
    def test_real_restart_agent_failed(self, agent_deploy):
        """
        测试重启主机Agent失败
        :return:
        """
        self.assertEqual(real_host_agent_restart(self.host), None)

    @mock.patch.object(
        MonitorAgentManager, "install", return_value=(True, "error_message"))
    def test_deploy_monitor_agent_success(self, *args, **kwargs):
        """
        测试部署监控Agent函数 成功情况
        :param args:
        :param kwargs:
        :return:
        """
        self.assertEqual(deploy_monitor_agent(self.host, True), None)

    @mock.patch.object(
        MonitorAgentManager, "install", return_value=(True, "error_message"))
    def test_deploy_monitor_agent_false(self, *args, **kwargs):
        """
        测试部署监控Agent函数 成功情况
        :param args:
        :param kwargs:
        :return:
        """
        self.assertEqual(deploy_monitor_agent(self.host, False), None)

    @mock.patch.object(
        MonitorAgentManager, "install", return_value=(False, "error_message"))
    def test_deploy_monitor_agent_failed(self, *args, **kwargs):
        """
        测试部署监控Agent函数 成功情况
        :param args:
        :param kwargs:
        :return:
        """
        self.assertEqual(deploy_monitor_agent(self.host, True), None)
