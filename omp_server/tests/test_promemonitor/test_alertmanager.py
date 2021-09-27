import json
from unittest import mock

import requests
from django.test import TestCase

from promemonitor.alertmanager import Alertmanager
from db_models.models import MonitorUrl


class MockResponse:
    """
    自定义mock response类
    """
    status = 200

    def __init__(self, data):
        self.text = json.dumps(data)

    def json(self):
        return json.loads(self.text)


class TestAlertmanager(TestCase):
    """
    alertmanager功能测试类
    """

    def setUp(self):
        MonitorUrl.objects.create(
            name='alertmanager', monitor_url='127.0.0.1:19013')

    @staticmethod
    def return_host_list():
        host_list = [
            {
                'ip': '10.0.3.71',
                'data_folder': '/boot',
                'cpu_usage': 0,
                'mem_usage': 0,
                'root_disk_usage': 0,
                'data_disk_usage': 0,
            },
            {
                'ip': '10.0.3.72',
                'data_folder': '/boot',
                'cpu_usage': 0,
                'mem_usage': 0,
                'root_disk_usage': 0,
                'data_disk_usage': 0,
            }
        ]
        return host_list

    @staticmethod
    def return_set_alertmanager_maintain_response():
        maintain_info = MockResponse(
            {'status': 'success', 'data': {'silenceId': 'f9aed355-8a99-42ba-9fe6-877633ea3e4a'}})
        return maintain_info

    @staticmethod
    def return_revoke_alertmanager_maintain_response():
        revoke_maintain_info = MockResponse('')
        return revoke_maintain_info

    @mock.patch.object(requests, 'post', return_value='')
    def test_set_maintain_by_host_list(self, mock_post):
        mock_post.return_value = self.return_set_alertmanager_maintain_response()
        alertmanager = Alertmanager()
        maintain_ids = alertmanager.set_maintain_by_host_list(
            self.return_host_list())
        TestCase.assertIsNotNone(maintain_ids, '添加维护失败')
        return maintain_ids

    @mock.patch.object(requests, 'post', return_value='')
    def test_set_maintain_by_env_name(self, mock_post):
        mock_post.return_value = self.return_set_alertmanager_maintain_response()
        alertmanager = Alertmanager()
        maintain_ids = alertmanager.set_maintain_by_env_name('default')
        TestCase.assertIsNotNone(maintain_ids, '添加维护失败')
        return maintain_ids

    # def test_delete_maintain(self):
    #     alertmanager = Alertmanager()
    #     maintain_ids = self.test_set_maintain_by_env_name()
    #     delete_result = alertmanager.delete_setting(maintain_ids[0])
    #     self.assertTrue(delete_result, '删除维护失败')

    @mock.patch.object(requests, 'post', return_value='')
    def test_revoke_alertmanager_maintain_by_host_list(self, mock_post):
        mock_post.return_value = self.return_revoke_alertmanager_maintain_response()
        alertmanager = Alertmanager()
        revoke_result = alertmanager.revoke_maintain_by_host_list(
            self.return_host_list())
        TestCase.assertIsNotNone(revoke_result, '删除维护失败')

    @mock.patch.object(requests, 'post', return_value='')
    def test_revoke_alertmanager_maintain_by_env_name(self, mock_post):
        mock_post.return_value = self.return_revoke_alertmanager_maintain_response()
        alertmanager = Alertmanager()
        revoke_result = alertmanager.revoke_maintain_by_env_name('default')
        TestCase.assertIsNotNone(revoke_result, '删除维护失败')

    def tearDown(self):
        # MonitorUrl.objects.delete(name='alertmanager')
        pass
