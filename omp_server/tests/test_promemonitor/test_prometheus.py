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
    status_code = 200

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
            {'ip': '10.0.3.71', 'data_folder': '/boot', 'cpu_usage': 12, 'mem_usage': 12, 'root_disk_usage': 12,
             'data_disk_usage': 12, 'cpu_status': "normal", 'mem_status': "normal", 'root_disk_status': "normal",
             'data_disk_status': "normal"}
        ]
        return correct_host_info_data

    request_get_response = {"status": "success", "data": {"resultType": "vector", "result": [
        {"metric": {"instance": "10.0.3.71"}, "value": [
            1633782875.771, "11.360416666623973"]},
        {"metric": {"instance": "10.0.3.72"}, "value": [
            1633782875.771, "11.04166666666666"]}
    ]}}

    error_request_get_response = {"status": "error", "data": {"resultType": "vector", "result": [
        {"metric": {"instance": "10.0.3.71"}, "value": [
            1633782875.771, "11.360416666623973"]},
        {"metric": {"instance": "10.0.3.72"}, "value": [
            1633782875.771, "11.04166666666666"]}
    ]}}

    @mock.patch.object(requests, 'get', return_value='')
    def test_get_prometheus_info(self, mock_post):
        mock_post.return_value = MockResponse(self.request_get_response)
        prometheus = Prometheus()
        result = prometheus.get_host_info(self.return_host_list())
        # print(result)
        self.assertListEqual(result,
                             self.return_host_info_data())

    def test_get_host_metric_status(self):
        p = Prometheus()
        result_none = p.get_host_metric_status('cpu', None)
        self.assertIsNone(result_none)

        result_critical = p.get_host_metric_status('cpu', 91)
        self.assertEqual(result_critical, 'critical')

        result_warning = p.get_host_metric_status('cpu', 81)
        self.assertEqual(result_warning, 'warning')

    @mock.patch.object(requests, 'get', return_value='')
    def test_error_get_host_arg_usage(self, mock_get):
        mock_get.return_value = MockResponse(self.error_request_get_response)
        p = Prometheus()
        result_get_host_cpu_usage = p.get_host_cpu_usage(
            self.return_host_list())
        self.assertIsNone(result_get_host_cpu_usage[0].get("cpu_usage"))

        result_get_host_mem_usage = p.get_host_mem_usage(
            self.return_host_list())
        self.assertIsNone(result_get_host_mem_usage[0].get("mem_usage"))

        result_get_host_root_disk_usage = p.get_host_root_disk_usage(
            self.return_host_list())
        self.assertIsNone(
            result_get_host_root_disk_usage[0].get("root_disk_usage"))

        result_get_host_data_disk_usage = p.get_host_data_disk_usage(
            self.return_host_list())
        self.assertIsNone(
            result_get_host_data_disk_usage[0].get("data_disk_usage"))

        mock_get.return_value.status_code = -1
        result_get_host_cpu_usage = p.get_host_cpu_usage(
            self.return_host_list())
        self.assertIsNone(result_get_host_cpu_usage[0].get("cpu_usage"))

        result_get_host_mem_usage = p.get_host_mem_usage(
            self.return_host_list())
        self.assertIsNone(result_get_host_mem_usage[0].get("mem_usage"))

        result_get_host_root_disk_usage = p.get_host_root_disk_usage(
            self.return_host_list())
        self.assertIsNone(
            result_get_host_root_disk_usage[0].get("root_disk_usage"))

        result_get_host_data_disk_usage = p.get_host_data_disk_usage(
            self.return_host_list())
        self.assertIsNone(
            result_get_host_data_disk_usage[0].get("data_disk_usage"))

        mock_get.return_value = MockResponse(self.request_get_response)
        mock_get.return_value.status_code = 200
        result_get_host_cpu_usage = p.get_host_cpu_usage(1)
        self.assertEqual(result_get_host_cpu_usage, 1)

        result_get_host_mem_usage = p.get_host_mem_usage(1)
        self.assertEqual(result_get_host_mem_usage, 1)

        result_get_host_root_disk_usage = p.get_host_root_disk_usage(1)
        self.assertEqual(result_get_host_root_disk_usage, 1)

        result_get_host_data_disk_usage = p.get_host_data_disk_usage(
            [{"1": 1}, {"2": 2}])
        self.assertEqual(result_get_host_data_disk_usage, [{'1': 1, 'data_disk_usage': None, 'data_disk_status': None},
                                                           {'2': 2, 'data_disk_usage': None, 'data_disk_status': None}])

    def tearDown(self):
        MonitorUrl.objects.filter(name='prometheus').delete()
