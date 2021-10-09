import json

import requests
from django.test import TestCase

from promemonitor.prometheus import Prometheus
from db_models.models import MonitorUrl
from unittest import mock


class MockResponse:
    """
    自定义mock response类
    """
    status = 200

    def __init__(self, data):
        self.text = json.dumps(data)

    def json(self):
        return json.loads(self.text)


class TestPrometheus(TestCase):

    def setUp(self):
        MonitorUrl.objects.create(
            name='prometheus', monitor_url='127.0.0.1:19011')

    @staticmethod
    def return_host_list():
        host_list = [
            {
                'ip': '10.0.3.71',
                'data_folder': '/boot',
            }
        ]
        return host_list

    @staticmethod
    def return_host_info_data():
        correct_host_info_data = [
            {'ip': '10.0.3.71', 'data_folder': '/boot', 'cpu_usage': None, 'mem_usage': None, 'root_disk_usage': None,
             'data_disk_usage': None, 'cpu_status': None, 'mem_status': None, 'root_disk_status': None,
             'data_disk_status': None}
        ]
        return correct_host_info_data

    @mock.patch.object(requests, 'post', return_value='')
    def test_get_prometheus_info(self, mock_post):
        mock_post.return_value = self.return_host_info_data()
        prometheus = Prometheus()
        result = prometheus.get_host_info(self.return_host_list())
        print(result)
        self.assertListEqual(result,
                             self.return_host_info_data())

    def tearDown(self):
        # MonitorUrl.objects.filter(name='prometheus').delete()
        pass
