from rest_framework.reverse import reverse

from db_models.models import ServiceHistory
from tests.base import AutoLoginTest
from tests.mixin import (
    ServicesResourceMixin
)
from services.tasks import exec_action
from unittest import mock


class ListActionTest(AutoLoginTest, ServicesResourceMixin):
    """ 服务动作测试类 """

    def setUp(self):
        super(ListActionTest, self).setUp()
        self.create_action_url = reverse("action-list")
        self.service_ls = self.get_services()

    @mock.patch(
        "utils.plugin.salt_client.SaltClient.cmd",
        return_value=(True, "success"))
    def test_service_action_true(self, action):
        exec_action("1", self.service_ls[1].id, "admin")
        history_count = ServiceHistory.objects.filter(service=self.service_ls[1]).count()
        res = {self.service_ls[1].service_status: history_count}
        self.assertDictEqual(res, {
            0: 1
        })

    @mock.patch(
        "utils.plugin.salt_client.SaltClient.cmd",
        return_value=(False, "false"))
    def test_service_action_false(self, action):
        exec_action("1", self.service_ls[1].id, "admin")
        history_count = ServiceHistory.objects.filter(service=self.service_ls[1]).count()
        res = {self.service_ls[1].service_status: history_count}
        self.assertDictEqual(res, {
            4: 1
        })

    def test_service_action_post(self):
        # 参数正常 -> 成功
        resp = self.post(self.create_action_url, {
            "action": "1",
            "id": "1",
            "operation_user": "admin",
        }).json()
        self.assertEqual(resp.get("code"), 0)
        # 参数缺失 -> 失败
        resp = self.post(self.create_action_url, {
            "action": "1",
        }).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "请输入action或id",
            "data": None
        })
