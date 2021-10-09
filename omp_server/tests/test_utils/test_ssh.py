# -*- coding: utf-8 -*-
# Project: test_ssh
# Author: jon.liu@yunzhihui.com
# Create time: 2021-09-23 15:48
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
ssh 单元测试代码
# TODO 待完善，与环境隔离
"""

from unittest import mock

from scp import SCPClient
from paramiko import SSHClient

from tests.base import BaseTest
from utils.plugin.ssh import SSH


def get_ssh_obj(username="root"):
    """
    获取ssh对象
    :return:
    """
    return SSH(
        hostname="127.0.0.1",
        port=22,
        username=username,
        password="root",
        timeout=1
    )


class ChannelMock(object):
    """ 模拟channel """

    def recv_exit_status(self):
        """
        模拟方法
        :return:
        """


class StdoutMock(object):
    """ 模拟输出 """

    def __init__(self, content):
        self.content = content
        self.channel = ChannelMock()

    def readline(self):
        """
        读取数据
        :return:
        """
        return self.content

    def readlines(self):
        """
        读取数据
        :return:
        """
        if self.content:
            return [self.content]
        return []


class SshUtilTest(BaseTest):
    """ ssh工具测试类 """

    def setUp(self):
        super(SshUtilTest, self).setUp()
        self.ssh = get_ssh_obj()

    def test_get_connection_failed(self):
        """
        测试ssh连接失败信息
        :return:
        """
        self.assertEqual(self.ssh._get_connection(), None)

    @mock.patch.object(SSHClient, "set_missing_host_key_policy", return_value=None)
    @mock.patch.object(SSHClient, "connect", return_value=None)
    @mock.patch.object(SSHClient, "get_transport", return_value=None)
    @mock.patch.object(SCPClient, "__init__", return_value=None)
    def test_get_connection_success(self, *args, **kwargs):
        """
        测试ssh连接正常
        :return:
        """
        self.assertEqual(self.ssh._get_connection(), None)
        self.assertEqual(self.ssh.is_error, None)

    @mock.patch.object(SSHClient, "set_missing_host_key_policy", return_value=None)
    @mock.patch.object(SSHClient, "connect", return_value=None)
    @mock.patch.object(SSHClient, "get_transport", return_value=None)
    @mock.patch.object(SCPClient, "__init__", return_value=None)
    @mock.patch.object(SSHClient, "exec_command", return_value=("", "success", 0))
    def test_is_sudo_success(self, exec_command, *args, **kwargs):
        """
        测试sudo
        :return:
        """
        stdout = StdoutMock("success")
        exec_command.side_effect = [("", stdout, 0), ]
        self.assertEqual(self.ssh.is_sudo()[0], True)

    @mock.patch.object(SSHClient, "set_missing_host_key_policy", return_value=None)
    @mock.patch.object(SSHClient, "connect", return_value=None)
    @mock.patch.object(SSHClient, "get_transport", return_value=None)
    @mock.patch.object(SCPClient, "__init__", return_value=None)
    @mock.patch.object(SSHClient, "exec_command", return_value=("", "success", 0))
    def test_is_sudo_failed(self, exec_command, *args, **kwargs):
        """
        测试sudo
        :return:
        """
        stdout = StdoutMock("failed")
        exec_command.side_effect = [("", stdout, 0), ]
        self.assertEqual(self.ssh.is_sudo()[0], False)

    def test_is_sudo_failed_connected(self):
        """
        测试ssh检查报错，连接信息报错
        :return:
        """
        self.assertEqual(self.ssh.is_sudo()[0], False)

    @mock.patch.object(SSHClient, "set_missing_host_key_policy", return_value=None)
    @mock.patch.object(SSHClient, "connect", return_value=None)
    @mock.patch.object(SSHClient, "get_transport", return_value=None)
    @mock.patch.object(SCPClient, "__init__", return_value=None)
    @mock.patch.object(SSHClient, "exec_command", return_value=("", "success", 0))
    def test_ssh_check_failed(self, exec_command, *args, **kwargs):
        """
        测试ssh检查报错
        :return:
        """
        stdout = mock.MagicMock()
        exec_command.side_effect = [("", stdout, 0), ]
        self.assertEqual(self.ssh.check()[0], False)

    @mock.patch.object(SSHClient, "set_missing_host_key_policy", return_value=None)
    @mock.patch.object(SSHClient, "connect", return_value=None)
    @mock.patch.object(SSHClient, "get_transport", return_value=None)
    @mock.patch.object(SCPClient, "__init__", return_value=None)
    @mock.patch.object(SSHClient, "exec_command", return_value=("", "success", 0))
    def test_ssh_check_success(self, exec_command, *args, **kwargs):
        """
        测试ssh检查成功
        :return:
        """
        stdout = StdoutMock("root")
        exec_command.side_effect = [("", stdout, 0), ]
        self.assertEqual(self.ssh.check()[0], True)

    def test_ssh_check_failed_connected(self):
        """
        测试ssh检查报错，连接信息报错
        :return:
        """
        self.assertEqual(self.ssh.check()[0], False)

    @mock.patch.object(SSHClient, "set_missing_host_key_policy", return_value=None)
    @mock.patch.object(SSHClient, "connect", return_value=None)
    @mock.patch.object(SSHClient, "get_transport", return_value=None)
    @mock.patch.object(SCPClient, "__init__", return_value=None)
    @mock.patch.object(SSHClient, "exec_command", return_value=("", "success", 0))
    def test_ssh_cmd_failed(self, exec_command, *args, **kwargs):
        """
        测试执行命令失败
        :return:
        """
        stderr = StdoutMock("failed")
        stdout = StdoutMock("test")
        exec_command.side_effect = [("", stdout, stderr), ]
        self.assertEqual(self.ssh.cmd("aaa", get_pty=False)[0], False)

    def test_ssh_cmd_failed_connected(self):
        """
        测试ssh检查报错，连接信息报错
        :return:
        """
        self.assertEqual(self.ssh.cmd("ip a")[0], False)

    @mock.patch.object(SSHClient, "set_missing_host_key_policy", return_value=None)
    @mock.patch.object(SSHClient, "connect", return_value=None)
    @mock.patch.object(SSHClient, "get_transport", return_value=None)
    @mock.patch.object(SCPClient, "__init__", return_value=None)
    @mock.patch.object(SSHClient, "exec_command", return_value=("", "success", 0))
    def test_ssh_cmd_success(self, exec_command, *args, **kwargs):
        """
        测试执行命令成功
        :return:
        """
        stderr = StdoutMock("")
        stdout = StdoutMock("root")
        exec_command.side_effect = [("", stdout, stderr), ]
        self.assertEqual(self.ssh.cmd("whoami")[0], True)

    @mock.patch.object(SSHClient, "set_missing_host_key_policy", return_value=None)
    @mock.patch.object(SSHClient, "connect", return_value=None)
    @mock.patch.object(SSHClient, "get_transport", return_value=None)
    @mock.patch.object(SSHClient, "close", return_value=None)
    @mock.patch.object(SCPClient, "__init__", return_value=None)
    @mock.patch.object(SCPClient, "close", return_value=None)
    def test_ssh_close_success(self, *args, **kwargs):
        """
        关闭连接成功
        :return:
        """
        self.ssh._get_connection()
        self.assertEqual(self.ssh.close(), None)

    @mock.patch.object(SSH, "make_remote_path_exist", return_value=None)
    @mock.patch.object(SSHClient, "set_missing_host_key_policy", return_value=None)
    @mock.patch.object(SSHClient, "connect", return_value=None)
    @mock.patch.object(SSHClient, "get_transport", return_value=None)
    @mock.patch.object(SCPClient, "__init__", return_value=None)
    @mock.patch.object(SCPClient, "put", return_value=None)
    @mock.patch.object(SSHClient, "exec_command", return_value=("", "success", 0))
    def test_ssh_file_push_success(self, *args, **kwargs):
        """
        发送文件成功
        :return:
        """
        self.assertEqual(self.ssh.file_push(__file__, "/tmp")[0], True)

    @mock.patch.object(SSH, "close", return_value=None)
    @mock.patch.object(SSH, "make_remote_path_exist", return_value=None)
    @mock.patch.object(SSHClient, "set_missing_host_key_policy", return_value=None)
    @mock.patch.object(SSHClient, "connect", return_value=None)
    @mock.patch.object(SSHClient, "get_transport", return_value=None)
    @mock.patch.object(SCPClient, "__init__", return_value=None)
    @mock.patch.object(SSHClient, "exec_command", return_value=("", "success", 0))
    def test_ssh_file_push_failed_exception(self, *args, **kwargs):
        """
        发送文件成功
        :return:
        """
        self.assertEqual(self.ssh.file_push(__file__, "/tmp")[0], False)

    def test_ssh_file_push_failed_connected(self):
        """
        发送文件失败
        :return:
        """
        self.assertEqual(self.ssh.file_push(__file__, "/tmp")[0], False)

    @mock.patch.object(SSH, "cmd", return_value=None)
    @mock.patch.object(SSHClient, "set_missing_host_key_policy", return_value=None)
    @mock.patch.object(SSHClient, "connect", return_value=None)
    @mock.patch.object(SSHClient, "get_transport", return_value=None)
    @mock.patch.object(SCPClient, "__init__", return_value=None)
    def test_make_remote_path_exist_root(self, *args, **kwargs):
        """
        测试root用户情况下的远程目录存在
        :return:
        """
        self.assertEqual(self.ssh.make_remote_path_exist("/tmp"), None)

    @mock.patch.object(SSH, "cmd", return_value=None)
    @mock.patch.object(SSHClient, "set_missing_host_key_policy", return_value=None)
    @mock.patch.object(SSHClient, "connect", return_value=None)
    @mock.patch.object(SSHClient, "get_transport", return_value=None)
    @mock.patch.object(SCPClient, "__init__", return_value=None)
    def test_make_remote_path_exist_not_root(self, *args, **kwargs):
        """
        测试root用户情况下的远程目录存在
        :return:
        """
        ssh_obj = get_ssh_obj("aaa")
        self.assertEqual(ssh_obj.make_remote_path_exist("/tmp"), None)
