# -*- coding: utf-8 -*-
# Project: test_ssh
# Author: jon.liu@yunzhihui.com
# Create time: 2021-09-23 15:48
# IDE: PyCharm
# Version: 1.0
# Introduction:

import os
from unittest import mock

from paramiko import SSHClient

from tests.base import BaseTest
from utils.plugin.ssh import SSH


class SshUtilTest(BaseTest):
    """ 主机Agent的测试类 """

    def setUp(self):
        super(SshUtilTest, self).setUp()
        self.ssh = SSH(
            hostname="10.0.7.146",
            port=36000,
            username="root",
            password="Yunzhihui@123",
            timeout=60
        )

    def test_get_connection_failed(self):
        """
        测试ssh连接失败信息
        :return:
        """
        ssh_obj = SSH(
            hostname="127.0.0.1",
            port=22,
            username="root",
            password="root",
            timeout=60
        )
        self.assertEqual(ssh_obj._get_connection(), None)

    def test_get_connection_success(self):
        """
        测试ssh连接正常
        :return:
        """
        self.assertEqual(self.ssh._get_connection(), None)
        self.assertEqual(self.ssh.is_error, None)

    def test_is_sudo_success(self):
        """
        测试sudo
        :return:
        """
        self.assertEqual(self.ssh.is_sudo()[0], True)

    def test_is_sudo_failed(self):
        """
        测试sudo
        :return:
        """
        ssh_obj = SSH(
            hostname="10.0.7.146",
            port=36000,
            username="common",
            password="Yunzhihui@123",
            timeout=60
        )
        self.assertEqual(ssh_obj.is_sudo()[0], False)

    @mock.patch.object(SSHClient, "exec_command", return_value=("", b"", 0))
    def test_ssh_check_failed(self, exec_command):
        """
        测试ssh检查报错
        :return:
        """
        _test_file_path = "/tmp/exec_command.txt"
        with open(_test_file_path, "w") as fp:
            fp.write("exec_command")
        fp_a = open(_test_file_path, "r")
        exec_command.side_effect = [("", fp_a, 0), ]
        os.remove(_test_file_path)
        self.assertEqual(self.ssh.check()[0], False)
        fp_a.close()

    def test_ssh_check_success(self):
        """
        测试ssh检查成功
        :return:
        """
        self.assertEqual(self.ssh.check()[0], True)

    def test_ssh_check_failed_connected(self):
        """
        测试ssh检查报错，连接信息报错
        :return:
        """
        ssh_obj = SSH(
            hostname="127.0.0.1",
            port=22,
            username="root",
            password="root",
            timeout=60
        )
        self.assertEqual(ssh_obj.check()[0], False)

    def test_ssh_cmd_failed(self):
        """
        测试执行命令失败
        :return:
        """
        self.assertEqual(self.ssh.cmd("aaa", get_pty=False)[0], False)

    def test_ssh_cmd_failed_connected(self):
        """
        测试ssh检查报错，连接信息报错
        :return:
        """
        ssh_obj = SSH(
            hostname="127.0.0.1",
            port=22,
            username="root",
            password="root",
            timeout=60
        )
        self.assertEqual(ssh_obj.cmd("ip a")[0], False)

    def test_ssh_cmd_success(self):
        """
        测试执行命令成功
        :return:
        """
        self.assertEqual(self.ssh.cmd("whoami")[0], True)

    def test_ssh_close_success(self):
        """
        关闭连接成功
        :return:
        """
        self.ssh._get_connection()
        self.assertEqual(self.ssh.close(), None)

    def test_ssh_file_push_success(self):
        """
        发送文件失败
        :return:
        """
        self.assertEqual(self.ssh.file_push(__file__, "/tmp")[0], True)

    def test_ssh_file_push_failed_connected(self):
        """
        发送文件失败
        :return:
        """
        ssh_obj = SSH(
            hostname="127.0.0.1",
            port=22,
            username="root",
            password="root",
            timeout=60
        )
        self.assertEqual(ssh_obj.file_push(__file__, "/tmp")[0], False)
