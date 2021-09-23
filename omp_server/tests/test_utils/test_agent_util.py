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

import os
import shutil
from unittest import mock

from tests.base import BaseTest
from utils.plugin.ssh import SSH
from utils.plugin.agent_util import Agent
from omp_server.settings import PROJECT_DIR


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
        _test_conf_path = os.path.join(PROJECT_DIR, "package_hub/127.0.0.1")
        if os.path.exists(_test_conf_path):
            shutil.rmtree(_test_conf_path)

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
        测试ssh连接失败
        :return:
        """
        self.assertEqual(self.agent.agent_deploy()[0], False)

    @mock.patch.object(SSH, "check", return_value=(True, "success"))
    @mock.patch.object(SSH, "cmd", return_value=(False, "success"))
    @mock.patch.object(SSH, "file_push", return_value=(True, "success"))
    def test_deploy_agent_false_cmd(self, check, cmd, file_push):
        """
        测试命令执行失败
        :return:
        """
        self.assertEqual(self.agent.agent_deploy()[0], False)

    @mock.patch.object(SSH, "check", return_value=(True, "success"))
    @mock.patch.object(SSH, "cmd", return_value=(True, "success"))
    @mock.patch.object(SSH, "file_push", return_value=(False, "failed"))
    def test_deploy_agent_false_agent_file(self, check, cmd, file_push):
        """
        测试agent文件推送失败
        :return:
        """
        self.assertEqual(self.agent.agent_deploy()[0], False)

    @mock.patch.object(SSH, "check", return_value=(True, "success"))
    @mock.patch.object(SSH, "cmd", return_value=(True, "success"))
    @mock.patch.object(SSH, "file_push", return_value="")
    def test_deploy_agent_false_file_config(self, file_push, cmd, check):
        """
        测试配置文件推送失败
        :return:
        """
        file_push.side_effect = [
            (True, "success"), (False, "error"), (True, "success")]
        self.assertEqual(self.agent.agent_deploy()[0], False)

    @mock.patch.object(SSH, "check", return_value=(True, "success"))
    @mock.patch.object(SSH, "cmd", return_value=(True, "success"))
    @mock.patch.object(SSH, "file_push", return_value="")
    def test_deploy_agent_false_file_script(self, file_push, cmd, check):
        """
        测试Agent脚本文件推送失败
        :return:
        """
        file_push.side_effect = [
            (True, "success"), (True, "success"), (False, "error")]
        self.assertEqual(self.agent.agent_deploy()[0], False)

    @mock.patch.object(SSH, "check", return_value=(True, "success"))
    @mock.patch.object(SSH, "cmd", return_value="")
    @mock.patch.object(SSH, "file_push", return_value=(True, "success"))
    def test_deploy_agent_false_start(self, file_push, cmd, check):
        """
        测试Agent启动失败
        :return:
        """
        cmd.side_effect = [(True, "success"),
                           (True, "success"), (False, "error")]
        self.assertEqual(self.agent.agent_deploy()[0], False)

    @mock.patch.object(SSH, "check", return_value=(True, "success"))
    @mock.patch.object(SSH, "cmd", return_value="")
    @mock.patch.object(SSH, "file_push", return_value=(True, "success"))
    def test_deploy_agent_success_start(self, file_push, cmd, check):
        """
        测试Agent启动成功
        :return:
        """
        cmd.side_effect = [
            (True, "success"),
            (True, "success"),
            (False, "INIT_OMP_SALT_AGENT_SUCCESS")
        ]
        self.assertEqual(self.agent.agent_deploy()[0], True)

    @mock.patch.object(SSH, "check", return_value=(True, "success"))
    @mock.patch.object(SSH, "cmd", return_value=(True, "success"))
    @mock.patch.object(SSH, "file_push", return_value=(True, "success"))
    @mock.patch.object(Agent, "generate_conf", return_value=(False, "success"))
    def test_deploy_agent_false_generate_conf(self, check, cmd, file_push, generate_conf):
        """
        测试生成配置文件报错
        :return:
        """
        self.assertEqual(self.agent.agent_deploy()[0], False)

    @mock.patch.object(SSH, "check", return_value=(True, "success"))
    @mock.patch.object(SSH, "cmd", return_value=(True, "success"))
    def test_agent_start_success(self, cmd, check):
        """
        测试启动成功
        :return:
        """
        self.assertEqual(self.agent.agent_manage(
            "start", "/data/omp_salt_agent")[0], True)

    @mock.patch.object(SSH, "check", return_value=(True, "success"))
    @mock.patch.object(SSH, "cmd", return_value=(False, "success"))
    def test_agent_start_failed(self, cmd, check):
        """
        测试启动失败
        :return:
        """
        self.assertEqual(self.agent.agent_manage(
            "start", "/data/omp_salt_agent")[0], False)

    @mock.patch.object(SSH, "check", return_value=(True, "success"))
    @mock.patch.object(SSH, "cmd", return_value=(True, "success"))
    def test_agent_stop_success(self, cmd, check):
        """
        测试停止成功
        :return:
        """
        self.assertEqual(self.agent.agent_manage(
            "stop", "/data/omp_salt_agent")[0], True)

    @mock.patch.object(SSH, "check", return_value=(True, "success"))
    @mock.patch.object(SSH, "cmd", return_value=(False, "success"))
    def test_agent_stop_failed(self, cmd, check):
        """
        测试停止失败
        :return:
        """
        self.assertEqual(self.agent.agent_manage(
            "stop", "/data/omp_salt_agent")[0], False)

    @mock.patch.object(SSH, "check", return_value=(True, "success"))
    @mock.patch.object(SSH, "cmd", return_value=(True, "success"))
    def test_agent_status_success(self, cmd, check):
        """
        测试查看状态成功
        :return:
        """
        self.assertEqual(self.agent.agent_manage(
            "status", "/data/omp_salt_agent")[0], True)

    @mock.patch.object(SSH, "check", return_value=(True, "success"))
    @mock.patch.object(SSH, "cmd", return_value=(False, "success"))
    def test_agent_status_failed(self, cmd, check):
        """
        测试查看状态失败
        :return:
        """
        self.assertEqual(self.agent.agent_manage(
            "status", "/data/omp_salt_agent")[0], False)

    @mock.patch.object(SSH, "check", return_value=(True, "success"))
    @mock.patch.object(SSH, "cmd", return_value=(True, "success"))
    def test_agent_restart_success(self, cmd, check):
        """
        测试重启成功
        :return:
        """
        self.assertEqual(self.agent.agent_manage(
            "restart", "/data/omp_salt_agent")[0], True)

    @mock.patch.object(SSH, "check", return_value=(True, "success"))
    @mock.patch.object(SSH, "cmd", return_value=(False, "success"))
    def test_agent_restart_failed(self, cmd, check):
        """
        测试重启失败
        :return:
        """
        self.assertEqual(self.agent.agent_manage(
            "restart", "/data/omp_salt_agent")[0], False)

    @mock.patch.object(SSH, "check", return_value=(True, "success"))
    @mock.patch.object(SSH, "cmd", return_value=(False, "success"))
    def test_agent_method_failed(self, cmd, check):
        """
        测试管理方法错误
        :return:
        """
        self.assertEqual(self.agent.agent_manage(
            "test", "/data/omp_salt_agent")[0], False)
