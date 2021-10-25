# -*- coding: utf-8 -*-
# Project: test_prometheus_utils
# Author: jon.liu@yunzhihui.com
# Create time: 2021-10-11 22:58
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
prometheus 工具集的单元测试代码
"""
import os
import uuid
import shutil
import json
from unittest import mock

import requests

from tests.base import BaseTest
from omp_server.settings import PROJECT_DIR
from promemonitor.prometheus_utils import PrometheusUtils


class MockResponse:
    """
    自定义mock response类
    """
    status_code = 0

    def __init__(self, data):
        self.text = json.dumps(data)

    def json(self):
        return json.loads(self.text)


class PrometheusUtilsTest(BaseTest):
    """ 主机Agent的测试类 """

    @staticmethod
    def delete_conf_dir():
        """
        删除prometheus文件
        :return:
        """
        conf_dir = os.path.join(PROJECT_DIR, "component/prometheus/conf")
        if os.path.exists(conf_dir):
            shutil.rmtree(conf_dir)

    def setUp(self):
        super(PrometheusUtilsTest, self).setUp()
        self.delete_conf_dir()
        self.prometheus_obj = PrometheusUtils()
        if not os.path.exists(self.prometheus_obj.prometheus_rules_path):
            os.makedirs(self.prometheus_obj.prometheus_rules_path)
        if not os.path.exists(self.prometheus_obj.prometheus_targets_path):
            os.makedirs(self.prometheus_obj.prometheus_targets_path)
        if not os.path.exists(self.prometheus_obj.prometheus_conf_path):
            with open(self.prometheus_obj.prometheus_conf_path, 'w') as pf:
                pf.write('')
        self.nodes_data = [
            {
                "data_path": "/data",
                "env": "default",
                "ip": "127.0.0.1"
            }
        ]

    def test_init_success(self):
        """
        测试PrometheusUtils可正常实例化情况
        :return:
        """
        self.assertEqual(
            isinstance(self.prometheus_obj, PrometheusUtils), True)

    def test_add_node_failed_with_null_data(self):
        """
        测试add_node传入空数据情况
        :return:
        """
        flag, message = self.prometheus_obj.add_node([])
        self.assertEqual(flag, False)
        self.assertEqual(message, "nodes_data can not be null")

    def test_add_node_success(self):
        """
        测试add_node成功的情况
        :return:
        """
        flag, message = self.prometheus_obj.add_node(self.nodes_data)
        self.assertEqual(flag, True)

    def test_add_node_success_2(self):
        """
        测试add_node成功的情况
        :return:
        """
        nodes_data = [
            {
                "data_path": "/data1",
                "env": "default",
                "ip": "127.0.0.1"
            }
        ]
        self.prometheus_obj.add_node(self.nodes_data)
        flag, message = self.prometheus_obj.add_node(nodes_data)
        self.assertEqual(flag, True)

    def test_add_node_success_3(self):
        """
        测试add_node成功的情况
        :return:
        """
        nodes_data = [
            {
                "data_path": "/data1",
                "env": "default",
                "ip": "127.0.0.1"
            }
        ]
        self.prometheus_obj.add_node(self.nodes_data)
        self.prometheus_obj.add_node(self.nodes_data)
        flag, message = self.prometheus_obj.add_node(nodes_data)
        self.assertEqual(flag, True)

    def test_delete_node_failed_with_null_data(self):
        """
        测试 delete_node 接收空数据
        :return:
        """
        self.assertEqual(self.prometheus_obj.delete_node([])[0], False)

    def test_delete_node_success(self):
        """
        测试 delete_node 成功
        :return:
        """
        self.test_add_node_success()
        flag, msg = self.prometheus_obj.delete_node(self.nodes_data)
        self.assertEqual(flag, True)

    def test_delete_node_failed_with_file_not_exist(self):
        """
        测试 delete_node 失败，target文件不存在
        :return:
        """
        flag, msg = self.prometheus_obj.delete_node(self.nodes_data)
        self.assertEqual(flag, False)

    def test_delete_node_success_with_empty_file(self):
        """
        测试 delete_node 失败，target文件不存在
        :return:
        """
        with open(self.prometheus_obj.node_exporter_targets_file, "w") as fp:
            fp.write("")
        flag, msg = self.prometheus_obj.delete_node(self.nodes_data)
        self.assertEqual(flag, True)

    def test_add_rules_failed(self):
        """
        测试 add_rules 失败
        :return:
        """
        self.assertEqual(self.prometheus_obj.add_rules("aaa")[0], False)

    def test_add_rules_for_node_success(self):
        """
        测试 add_rules 主机成功
        :return:
        """
        self.assertEqual(self.prometheus_obj.add_rules("node")[0], True)

    def test_add_rules_for_service_success(self):
        """
        测试 add_rules service成功
        :return:
        """
        self.assertEqual(self.prometheus_obj.add_rules("service")[0], True)

    def test_add_rules_for_exporter_success(self):
        """
        测试 add_rules exporter成功
        :return:
        """
        self.assertEqual(self.prometheus_obj.add_rules("exporter")[0], True)

    def test_delete_rules_failed(self):
        """
        测试 delete_rules 失败
        :return:
        """
        self.assertEqual(self.prometheus_obj.delete_rules("aaa")[0], False)

    def test_delete_rules_for_node_success(self):
        """
        测试 delete_rules node成功
        :return:
        """
        self.assertEqual(self.prometheus_obj.delete_rules("node")[0], True)

    def test_delete_rules_for_service_success(self):
        """
        测试 delete_rules status成功
        :return:
        """
        self.assertEqual(self.prometheus_obj.delete_rules("service")[0], True)

    def test_delete_rules_for_exporter_success(self):
        """
        测试 delete_rules exporter成功
        :return:
        """
        self.prometheus_obj.add_rules("exporter")
        self.assertEqual(self.prometheus_obj.delete_rules("exporter")[0], True)

    def test_replace_placeholder_failed(self):
        """
        测试文件不存在时无法替换placeholder
        :return:
        """
        self.assertEqual(
            self.prometheus_obj.replace_placeholder(
                f"/tmp/{str(uuid.uuid4())}",
                []
            )[0], False)

    @mock.patch.object(requests, 'post', return_value='')
    def test_add_service(self, mock_post):
        mock_post.return_value = MockResponse(
            {"return_code": 0, "message": "success"})
        test_service_data = {
            "service_name": "mysql",
            "instance_name": "mysql_dosm",
            "data_path": "/data/appData/mysql",
            "log_path": "/data/logs/mysql",
            "env": "default",
            "ip": "127.0.0.1",
            "listen_port": "3306"
        }
        flag, msg = self.prometheus_obj.add_service(test_service_data)
        self.assertEqual(flag, True)

    @mock.patch.object(requests, 'post', return_value='')
    def test_delete_service(self, mock_post):
        mock_post.return_value = MockResponse(
            {"return_code": 0, "message": "success"})
        mysql_json_file = os.path.join(
            self.prometheus_obj.prometheus_targets_path, 'mysqlExporter_all.json')
        with open(mysql_json_file, 'w') as mp:
            mp.write('')
        test_service_data = {
            "service_name": "mysql",
            "instance_name": "mysql_dosm",
            "data_path": "/data/appData/mysql",
            "log_path": "/data/logs/mysql",
            "env": "default",
            "ip": "127.0.0.1",
            "listen_port": "3306"
        }
        flag, msg = self.prometheus_obj.delete_service(test_service_data)
        self.assertEqual(flag, True)

    def tearDown(self) -> None:
        """
        测试结束操作
        :return:
        """
        self.delete_conf_dir()
