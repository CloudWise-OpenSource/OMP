import json

import requests
from rest_framework.reverse import reverse
from unittest import mock

from tests.base import AutoLoginTest
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


class GlobalMaintainTest(AutoLoginTest):
    """ 全局维护测试类 """

    def setUp(self):
        super(GlobalMaintainTest, self).setUp()
        MonitorUrl.objects.create(
            name='alertmanager', monitor_url='127.0.0.1:19013')
        self.global_maintain_url = reverse("globalMaintain-list")
        # 正确数据
        self.correct_maintain_data = {
            "matcher_name": "env",
            "matcher_value": "default"
        }

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
    def test_set_global_maintain(self, mock_post):
        """ 测试设置全局维护 """
        mock_post.return_value = self.return_set_alertmanager_maintain_response()
        resp = self.post(self.global_maintain_url,
                         self.correct_maintain_data).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertTrue(resp.get("data") is not None)
        # print('已设置全局维护:', resp)

        # 删除主机
        self.revoke_global_maintain(self.correct_maintain_data)

    @mock.patch.object(requests, 'delete', return_value='')
    def revoke_global_maintain(self, maintain_data, mock_post=''):
        mock_post.return_value = self.return_set_alertmanager_maintain_response()
        alertmanager = Alertmanager()
        alertmanager.revoke_maintain_by_env_name(
            env_name=maintain_data.get("matcher_value"))

    def tearDown(self):
        MonitorUrl.objects.filter(name='alertmanager').delete()
