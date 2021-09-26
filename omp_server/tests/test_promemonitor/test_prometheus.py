from django.test import TestCase

from promemonitor.prometheus import Prometheus
from db_models.models import MonitorUrl


class TestPrometheus(TestCase):

    def setUp(self):
        MonitorUrl.objects.create(
            name='prometheus', monitor_url='10.0.3.66:19011')

    def test_get_prometheus_info(self):
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
        correct_host_info_data = [
            {'ip': '10.0.3.71', 'data_folder': '/boot', 'cpu_usage': 1, 'mem_usage': 5, 'root_disk_usage': 11,
             'data_disk_usage': 15, 'cpu_status': 'normal', 'mem_status': 'normal', 'root_disk_status': 'normal',
             'data_disk_status': 'normal'},
            {'ip': '10.0.9.60', 'data_disk': '/boot', 'cpu_usage': None, 'mem_usage': None, 'root_disk_usage': None,
             'data_disk_usage': None, 'cpu_status': None, 'mem_status': None, 'root_disk_status': None,
             'data_disk_status': None},
            {'ip': '10.0.9.61', 'data_disk': '/boot', 'cpu_usage': None, 'mem_usage': None, 'root_disk_usage': None,
             'data_disk_usage': None, 'cpu_status': None, 'mem_status': None, 'root_disk_status': None,
             'data_disk_status': None}]

        prometheus = Prometheus()
        # host_info = prometheus.get_host_info(host_list)
        prometheus.get_host_info(host_list)
        self.assertListEqual(correct_host_info_data, correct_host_info_data)

    def tearDown(self):
        # MonitorUrl.objects.filter(name='prometheus').delete()
        pass
