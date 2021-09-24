from django.test import TestCase

from promemonitor.prometheus import Prometheus


class TestPrometheus(TestCase):

    def setup(self):
        self.host_list = [
            {
                'ip': '10.0.3.71',
                'data_folder': '/boot',
                'cpu_usage': 0,
                'mem_usage': 0,
                'root_disk_usage': 0,
                'data_disk_usage': 0,
            },
            {
                'ip': '10.0.9.60',
                'data_disk': '/boot',
                'cpu_usage': 0,
                'mem_usage': 0,
                'root_disk_usage': 0,
                'data_disk_usage': 0
            },
            {
                'ip': '10.0.9.61',
                'data_disk': '/boot',
                'cpu_usage': 0,
                'mem_usage': 0,
                'root_disk_usage': 0,
                'data_disk_usage': 0
            }
        ]
        self.correct_host_info_data = [
            {'ip': '10.0.3.71', 'data_folder': '/boot', 'cpu_usage': 1, 'mem_usage': 5, 'root_disk_usage': 11,
             'data_disk_usage': 15, 'cpu_status': 'warning', 'mem_status': 'warning', 'root_disk_status': 'warning'},
            {'ip': '10.0.9.60', 'data_disk': '/boot', 'cpu_usage': None, 'mem_usage': None, 'root_disk_usage': None,
             'data_disk_usage': 0, 'cpu_status': None, 'mem_status': None, 'root_disk_status': None},
            {'ip': '10.0.9.61', 'data_disk': '/boot', 'cpu_usage': None, 'mem_usage': None, 'root_disk_usage': None,
             'data_disk_usage': 0, 'cpu_status': None, 'mem_status': None, 'root_disk_status': None}]

    def test_get_prometheus_info(self):
        prometheus = Prometheus()
        host_info = prometheus.get_host_info(self.host_list)
        TestCase.assertListEqual(host_info, self.correct_host_info_data, list())
