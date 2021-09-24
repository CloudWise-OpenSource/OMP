from django.test import TestCase

from promemonitor.alertmanager import Alertmanager


class TestAlertmanager(TestCase):

    def setUp(self):
        pass

    def test_set_maintain(self):
        alertmanager = Alertmanager()
        maintain_id = alertmanager.add_setting(value='10.0.3.90', name='instance')
        TestCase.assertIsNotNone(maintain_id, '添加维护失败')

    def test_delete_maintain(self):
        alertmanager = Alertmanager()
        delete_result = alertmanager.delete_setting('f45b3f5d-bea4-40f5-bcb6-207fad21a563')
        self.assertTrue(delete_result, '删除维护失败')