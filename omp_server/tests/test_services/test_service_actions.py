from rest_framework.reverse import reverse

from db_models.models import ServiceHistory,Service
from tests.base import AutoLoginTest
from tests.mixin import (
    ServicesResourceMixin
)
from services.tasks import exec_action
from unittest import mock
import json

class ListActionTest(AutoLoginTest, ServicesResourceMixin):
    """ 服务动作测试类 """

    def setUp(self):
        super(ListActionTest, self).setUp()
        Service.objects.create(
            ip="192.168.0.110",
            service_instance_name="test1",
            service_port="3306",
            service_status=5,
            alert_count=6,
            self_healing_count=6,
            service_controllers=json.dumps({"start": "1.txt", "stop": "2.txt"}),
        )
        self.create_action_url = reverse("action-list")


    @mock.patch(
        "utils.plugin.salt_client.SaltClient.cmd",
        return_value=(True, "success"))
    def test_service_action_true(self, status):
        service_obj = Service.objects.get(ip="192.168.0.110")
        exec_action("1", service_obj.id, "admin")
        history_count = ServiceHistory.objects.filter(service=service_obj).count()
        service_obj.refresh_from_db()
        res = {service_obj.service_status: history_count}
        self.assertDictEqual(res, {
            0: 1
        })

    @mock.patch(
        "utils.plugin.salt_client.SaltClient.cmd",
        return_value=(False, "false"))
    def test_service_action_false(self, status):
        service_obj = Service.objects.get(ip="192.168.0.110")
        exec_action("1", service_obj.id, "admin")
        history_count = ServiceHistory.objects.filter(service=service_obj).count()
        service_obj.refresh_from_db()
        res = {service_obj.service_status: history_count}
        self.assertDictEqual(res, {
            4: 1
        })

    @mock.patch("services.tasks.exec_action",
        return_value=True)
    def test_service_action_post(self, tasks):
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
