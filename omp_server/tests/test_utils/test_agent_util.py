# -*- coding: utf-8 -*-
# Project: test_agent_util
# Author: jon.liu@yunzhihui.com
# Create time: 2021-09-23 10:25
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
主机Agent使用的测试代码
"""

from unittest import mock
from tests.base import BaseTest
from utils.plugin.ssh import SSH
from utils.plugin.agent_util import Agent


class AgentUtilTest(BaseTest):
    """ 主机Agent的测试类 """

    def setUp(self):
        super(AgentUtilTest, self).setUp()
        self.agent = Agent(
            host="127.0.0.1",
            port=22,
            username="root",
            password="root",
            install_dir="/data"
        )

    @mock.patch.object(SSH, "check", return_value=(True, "success"))
    @mock.patch.object(SSH, "cmd", return_value=(True, "success"))
    @mock.patch.object(SSH, "file_push", return_value=(True, "success"))
    def test_deploy_agent_success(self, check, cmd, file_push):
        """
        测试成功部署
        :return:
        """
        self.assertEqual(self.agent.agent_deploy()[0], True)

    @mock.patch.object(SSH, "check", return_value=(False, "success"))
    @mock.patch.object(SSH, "cmd", return_value=(True, "success"))
    @mock.patch.object(SSH, "file_push", return_value=(True, "success"))
    def test_deploy_agent_false_ssh(self, check, cmd, file_push):
        """
        测试成功部署
        :return:
        """
        self.assertEqual(self.agent.agent_deploy()[0], False)

    @mock.patch.object(SSH, "check", return_value=(True, "success"))
    @mock.patch.object(SSH, "cmd", return_value=(False, "success"))
    @mock.patch.object(SSH, "file_push", return_value=(True, "success"))
    def test_deploy_agent_false_cmd(self, check, cmd, file_push):
        """
        测试成功部署
        :return:
        """
        self.assertEqual(self.agent.agent_deploy()[0], False)

    @mock.patch.object(SSH, "check", return_value=(True, "success"))
    @mock.patch.object(SSH, "cmd", return_value=(True, "success"))
    @mock.patch.object(SSH, "file_push", return_value=(False, "success"))
    def test_deploy_agent_false_file(self, check, cmd, file_push):
        """
        测试成功部署
        :return:
        """
        self.assertEqual(self.agent.agent_deploy()[0], False)

    @mock.patch.object(SSH, "check", return_value=(True, "success"))
    @mock.patch.object(SSH, "cmd", return_value=(True, "success"))
    @mock.patch.object(SSH, "file_push", return_value=(True, "success"))
    @mock.patch.object(Agent, "generate_conf", return_value=(False, "success"))
    def test_deploy_agent_false_generate_conf(self, check, cmd, file_push, generate_conf):
        """
        测试成功部署
        :return:
        """
        self.assertEqual(self.agent.agent_deploy()[0], False)


# generate_conf
