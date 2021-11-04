import json

from rest_framework.reverse import reverse

from db_models.models import (
    ServiceHistory, Service, Env,
    ApplicationHub
)
from tests.base import AutoLoginTest
from tests.mixin import (
    ServicesResourceMixin
)
from services.tasks import exec_action
from unittest import mock
import time


class ListActionTest(AutoLoginTest, ServicesResourceMixin):
    """ 服务动作测试类 """

    def setUp(self):
        super(ListActionTest, self).setUp()
        env_obj = Env.objects.create(name="default")
        app_obj = ApplicationHub.objects.create(
            app_name="test_app", app_version="1.0.0")
        Service.objects.create(
            ip="192.168.0.110",
            service_instance_name="test1",
            service_status=5,
            alert_count=6,
            self_healing_count=6,
            service_controllers={"start": "1.txt", "stop": "2.txt"},
            env=env_obj,
            service=app_obj,
            service_port=json.dumps([{'default': '18080', 'key': 'http_port'}])
        )
        self.create_action_url = reverse("action-list")

    @mock.patch(
        "utils.plugin.salt_client.SaltClient.cmd",
        return_value=(True, "success"))
    def test_service_action_true(self, status):
        service_obj = Service.objects.get(ip="192.168.0.110")
        exec_action("1", service_obj.id, "admin")
        history_count = ServiceHistory.objects.filter(
            service=service_obj).count()
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
        history_count = ServiceHistory.objects.filter(
            service=service_obj).count()
        service_obj.refresh_from_db()
        res = {service_obj.service_status: history_count}
        self.assertDictEqual(res, {
            4: 1
        })

    @mock.patch(
        "utils.plugin.salt_client.SaltClient.cmd",
        return_value=(True, "success"))
    @mock.patch(
        "promemonitor.prometheus_utils.PrometheusUtils.delete_service",
        return_value=""
    )
    def test_service_action_delete(self, delete_service, status):
        service_obj = Service.objects.get(ip="192.168.0.110")
        time_array = time.localtime(int(time.time()))
        time_style = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
        service_history = ServiceHistory(
            username='admin',
            description='测试',
            result=0,
            created=time_style,
            service=service_obj
        )
        service_history.save()
        exec_action("4", service_obj.id, "admin")
        history_count = ServiceHistory.objects.filter(
            service=service_obj).count()
        new_service = Service.objects.filter(ip="192.168.0.110").count()
        self.assertEqual(history_count, 0)
        self.assertEqual(new_service, 0)

    @mock.patch("services.tasks.exec_action.delay",
                return_value=True)
    def test_service_action_post(self, tasks):
        # 参数正常 -> 成功
        resp = self.post(self.create_action_url, {"data": [{
            "action": "1",
            "id": "1",
            "operation_user": "admin",
        }]}).json()
        self.assertEqual(resp.get("code"), 0)
        # 参数缺失 -> 失败
        resp = self.post(self.create_action_url, {"data": [{
            "action": "1",
        }]}).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "请输入action或id",
            "data": None
        })
