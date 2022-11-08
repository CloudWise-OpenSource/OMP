import json
from unittest import mock

import requests
from django.test import TestCase

from promemonitor.alertmanager import Alertmanager
from db_models.models import MonitorUrl, Maintain


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

    @mock.patch.object(requests, 'post', return_value='')
    def test_revoke_alertmanager_maintain_by_host_list(self, mock_post):
        mock_post.return_value = self.return_revoke_alertmanager_maintain_response()
        alertmanager = Alertmanager()
        m1 = Maintain.objects.create(
            matcher_name="instance", matcher_value="10.0.3.71", maintain_id=1)
        m2 = Maintain.objects.create(
            matcher_name="instance", matcher_value="10.0.3.71", maintain_id=2)
        revoke_result = alertmanager.revoke_maintain_by_host_list(
            self.return_host_list())
        TestCase.assertIsNotNone(revoke_result, '删除维护失败')
        m1.delete()
        m2.delete()

    @mock.patch.object(requests, 'post', return_value='')
    def test_revoke_alertmanager_maintain_by_env_name(self, mock_post):
        mock_post.return_value = self.return_revoke_alertmanager_maintain_response()
        alertmanager = Alertmanager()
        revoke_result = alertmanager.revoke_maintain_by_env_name('default')
        TestCase.assertIsNotNone(revoke_result, '删除维护失败')

    @mock.patch.object(requests, 'post', return_value='')
    def test_error_alertmanager_func1(self, mock_post):
        alertmanager = Alertmanager()
        result_format_time = alertmanager.format_time(1)
        self.assertIsNone(result_format_time)

        result_add_setting = alertmanager.add_setting(
            value=1, name='env', start_time=1, ends_time=2)
        self.assertIsNone(result_add_setting)

        result_add_setting = alertmanager.add_setting(value=1, name='env', start_time='2021-09-11 12:34:56',
                                                      ends_time=2)
        self.assertIsNone(result_add_setting)

        mock_post.return_value = self.return_revoke_alertmanager_maintain_response()

        MonitorUrl.objects.filter(name='alertmanager').delete()
        alertmanager.get_alertmanager_config()

    def test_error_alertmanager_func2(self):
        alertmanager = Alertmanager()
        result_set_maintain_by_env_name = alertmanager.set_maintain_by_env_name(
            'aaa')
        self.assertIsNone(result_set_maintain_by_env_name)

        result_revoke_maintain_by_host_list = alertmanager.revoke_maintain_by_host_list([
            {
                'ip': '10.0.3.73',
                'data_folder': '/boot',
                'cpu_usage': 0,
                'mem_usage': 0,
                'root_disk_usage': 0,
                'data_disk_usage': 0,
            }])
        self.assertEqual(result_revoke_maintain_by_host_list, False)

    def tearDown(self):
        MonitorUrl.objects.filter(name='alertmanager').delete()
