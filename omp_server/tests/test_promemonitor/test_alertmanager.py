from django.test import TestCase

from promemonitor.alertmanager import Alertmanager
from db_models.models import MonitorUrl


class TestAlertmanager(TestCase):

    def setUp(self):
        MonitorUrl.objects.create(
            name='alertmanager', monitor_url='10.0.3.66:19013')

    def test_set_maintain_by_host_list(self):
        alertmanager = Alertmanager()
        host_list = [
            {
                'ip': '10.0.3.71',
                'data_folder': '/boot',
                'cpu_usage': 0,
                'mem_usage': 0,
                'root_disk_usage': 0,
                'data_disk_usage': 0,
            }]
        maintain_ids = alertmanager.set_maintain_by_host_list(host_list)
        TestCase.assertIsNotNone(maintain_ids, '添加维护失败')
        return maintain_ids

    def test_set_maintain_by_env_name(self):
        alertmanager = Alertmanager()
        maintain_ids = alertmanager.set_maintain_by_env_name('default')
        TestCase.assertIsNotNone(maintain_ids, '添加维护失败')
        return maintain_ids

    def test_delete_maintain(self):
        alertmanager = Alertmanager()
        maintain_ids = self.test_set_maintain_by_env_name()
        delete_result = alertmanager.delete_setting(maintain_ids[0])
        self.assertTrue(delete_result, '删除维护失败')

    def tearDown(self):
        # MonitorUrl.objects.delete(name='alertmanager')
        pass
