from django.test import TestCase

from promemonitor.alertmanager import Alertmanager
from db_models.models import MonitorUrl


class TestAlertmanager(TestCase):

    def setUp(self):
        MonitorUrl.objects.create(
            name='alertmanager', monitor_url='10.0.3.66:19013')

    def test_set_maintain(self):
        alertmanager = Alertmanager()
        maintain_id = alertmanager.add_setting(
            value='10.0.3.91', name='instance')
        TestCase.assertIsNotNone(maintain_id, '添加维护失败')
        return maintain_id

    def test_delete_maintain(self):
        alertmanager = Alertmanager()
        maintain_id = self.test_set_maintain()
        delete_result = alertmanager.delete_setting(maintain_id)
        self.assertTrue(delete_result, '删除维护失败')

    def tearDown(self):
        # MonitorUrl.objects.delete(name='alertmanager')
        pass
