# -*- coding: utf-8 -*-
# Project: test_salt_client
# Author: jon.liu@yunzhihui.com
# Create time: 2021-09-24 15:10
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
salt client相关测试
"""
from unittest import mock

import salt.client

from tests.base import BaseTest
from utils.plugin.salt_client import SaltClient


class SaltClientUtilTest(BaseTest):
    """ 主机Agent的测试类 """

    def setUp(self):
        super(SaltClientUtilTest, self).setUp()
        self.cmd_run = "cmd.run"

    @mock.patch.object(salt.client.LocalClient, "cmd", return_value="")
    def test_salt_module_update_failed(self, local_client):
        """
        测试同步salt模块成功的情况
        :return:
        """
        _obj = SaltClient()
        self.assertEqual(_obj.salt_module_update()[0], False)

    @mock.patch.object(salt.client.LocalClient, "cmd", return_value={
        '192.168.175.149': {'ret': [], 'retcode': 0, 'jid': '20210113213356939481'},
        '192.168.175.150': False,
        '192.168.175.151': [],
    })
    def test_salt_module_update_success(self, local_client):
        """
        测试同步salt模块成功的情况
        :return:
        """
        _obj = SaltClient()
        self.assertEqual(_obj.salt_module_update()[0], True)

    @mock.patch.object(salt.client.LocalClient, "cmd", return_value="")
    def test_fun_for_multi_failed(self, local_client):
        """
        测试批量执行时错误的情况
        :return:
        """
        _obj = SaltClient()
        local_client.side_effect = Exception("aa")
        self.assertEqual(_obj.fun_for_multi("*", self.cmd_run)[0], False)

    @mock.patch.object(salt.client.LocalClient, "cmd", return_value={})
    def test_fun_for_multi_success(self, local_client):
        """
        测试批量执行成功的情况
        :return:
        """
        _obj = SaltClient()
        self.assertEqual(_obj.fun_for_multi("*", self.cmd_run), {})

    @mock.patch.object(salt.client.LocalClient, "cmd", return_value="")
    def test_fun_failed(self, local_client):
        """
        测试执行fun出现异常情况
        :return:
        """
        _obj = SaltClient()
        local_client.side_effect = Exception("aa")
        self.assertEqual(_obj.fun("*", self.cmd_run)[0], False)

    @mock.patch.object(salt.client.LocalClient, "cmd", return_value={
        "key1": {'ret': "success", 'retcode': 0, 'jid': '20210113213356939481'}
    })
    def test_fun_success(self, local_client):
        """
        测试批量执行成功的情况
        :return:
        """
        _obj = SaltClient()
        self.assertEqual(_obj.fun("key1", self.cmd_run)[0], True)

    @mock.patch.object(salt.client.LocalClient, "cmd", return_value="")
    def test_fun_failed_1(self, local_client):
        """
        测试salt.cmd返回不是字典的情况
        :return:
        """
        _obj = SaltClient()
        self.assertEqual(_obj.fun("key1", self.cmd_run)[0], False)

    @mock.patch.object(salt.client.LocalClient, "cmd", return_value={})
    def test_fun_failed_2(self, local_client):
        """
        测试salt.cmd返回中不带salt-key的情况
        :return:
        """
        _obj = SaltClient()
        self.assertEqual(_obj.fun("key1", self.cmd_run)[0], False)

    @mock.patch.object(salt.client.LocalClient, "cmd", return_value={"key1": False})
    def test_fun_failed_3(self, local_client):
        """
        测试salt.cmd返回中salt-key 为False情况
        :return:
        """
        _obj = SaltClient()
        self.assertEqual(_obj.fun("key1", self.cmd_run)[0], False)

    @mock.patch.object(salt.client.LocalClient, "cmd", return_value={"key1": {}})
    def test_fun_failed_4(self, local_client):
        """
        测试salt.cmd返回中retcode不存在情况
        :return:
        """
        _obj = SaltClient()
        self.assertEqual(_obj.fun("key1", self.cmd_run)[0], False)

    @mock.patch.object(salt.client.LocalClient, "cmd", return_value={"key1": {'retcode': 1}})
    def test_fun_failed_5(self, local_client):
        """
        测试salt.cmd返回中retcode不为0情况
        :return:
        """
        _obj = SaltClient()
        self.assertEqual(_obj.fun("key1", self.cmd_run)[0], False)

    @mock.patch.object(salt.client.LocalClient, "cmd", return_value="")
    def test_cmd_failed(self, local_client):
        """
        测试执行cmd出现异常情况
        :return:
        """
        _obj = SaltClient()
        local_client.side_effect = Exception("aa")
        self.assertEqual(_obj.cmd("*", self.cmd_run, 1)[0], False)

    @mock.patch.object(salt.client.LocalClient, "cmd", return_value={
        "key1": {'ret': "success", 'retcode': 0, 'jid': '20210113213356939481'}
    })
    def test_cmd_success(self, local_client):
        """
        测试cmd执行成功的情况
        :return:
        """
        _obj = SaltClient()
        self.assertEqual(_obj.cmd("key1", self.cmd_run, 1)[0], True)

    @mock.patch.object(salt.client.LocalClient, "cmd", return_value="")
    def test_cmd_failed_1(self, local_client):
        """
        测试salt.cmd返回不是字典的情况
        :return:
        """
        _obj = SaltClient()
        self.assertEqual(_obj.cmd("key1", self.cmd_run, 1)[0], False)

    @mock.patch.object(salt.client.LocalClient, "cmd", return_value={})
    def test_cmd_failed_2(self, local_client):
        """
        测试salt.cmd返回中不带salt-key的情况
        :return:
        """
        _obj = SaltClient()
        self.assertEqual(_obj.cmd("key1", self.cmd_run, 1)[0], False)

    @mock.patch.object(salt.client.LocalClient, "cmd", return_value={"key1": False})
    def test_cmd_failed_3(self, local_client):
        """
        测试salt.cmd返回中salt-key 为False情况
        :return:
        """
        _obj = SaltClient()
        self.assertEqual(_obj.cmd("key1", self.cmd_run, 1)[0], False)

    @mock.patch.object(salt.client.LocalClient, "cmd", return_value={"key1": {}})
    def test_cmd_failed_4(self, local_client):
        """
        测试salt.cmd返回中retcode不存在情况
        :return:
        """
        _obj = SaltClient()
        self.assertEqual(_obj.cmd("key1", self.cmd_run, 1)[0], False)

    @mock.patch.object(salt.client.LocalClient, "cmd", return_value={"key1": {'retcode': 1}})
    def test_cmd_failed_5(self, local_client):
        """
        测试salt.cmd返回中retcode不为0情况
        :return:
        """
        _obj = SaltClient()
        self.assertEqual(_obj.cmd("key1", self.cmd_run, 1)[0], False)

    @mock.patch.object(salt.client.LocalClient, "cmd", return_value="")
    def test_cp_file_failed(self, local_client):
        """
        测试执行cp_file出现异常情况
        :return:
        """
        _obj = SaltClient()
        local_client.side_effect = Exception("aa")
        self.assertEqual(_obj.cp_file("*", "", "")[0], False)

    @mock.patch.object(salt.client.LocalClient, "cmd", return_value={
        "key1": "a"
    })
    def test_cp_file_success(self, local_client):
        """
        测试推送文件成功的情况
        :return:
        """
        _obj = SaltClient()
        self.assertEqual(_obj.cp_file("key1", "a", "a")[0], True)

    @mock.patch.object(salt.client.LocalClient, "cmd", return_value="")
    def test_cp_file_failed_1(self, local_client):
        """
        测试cp_file返回不是字典的情况
        :return:
        """
        _obj = SaltClient()
        self.assertEqual(_obj.cp_file("*", "", "")[0], False)

    @mock.patch.object(salt.client.LocalClient, "cmd", return_value={})
    def test_cp_file_failed_2(self, local_client):
        """
        测试cp_file返回中不带salt-key的情况
        :return:
        """
        _obj = SaltClient()
        self.assertEqual(_obj.cp_file("*", "", "")[0], False)

    @mock.patch.object(salt.client.LocalClient, "cmd", return_value={"key1": "PermissionError Permission denied"})
    def test_cp_file_failed_3(self, local_client):
        """
        测试cp_file返回中权限错误情况
        :return:
        """
        _obj = SaltClient()
        self.assertEqual(_obj.cp_file("*", "", "")[0], False)

    @mock.patch.object(salt.client.LocalClient, "cmd", return_value={"key1": {"ret": ""}})
    def test_cp_file_failed_4(self, local_client):
        """
        测试cp_file返回值不准确情况
        :return:
        """
        _obj = SaltClient()
        self.assertEqual(_obj.cp_file("*", "aa", "aa")[0], False)
