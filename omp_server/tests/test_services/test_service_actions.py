import json

from rest_framework.reverse import reverse

from db_models.models import (
    ServiceHistory, Service, Env,
    ApplicationHub, DetailInstallHistory
)
from tests.base import AutoLoginTest
from tests.mixin import (
    ServicesResourceMixin
)
from services.tasks import exec_action
from unittest import mock
import time

install_detail = {
    "ip": "10.0.7.184", "name": "mysql", "version": "5.7.31",
    "app_port": [{"key": "service_port", "name": "服务端口", "default": "3306"}],
    "deploy_mode": {"key": "single", "name": "单实例"},
    "app_install_args": [
        {"key": "base_dir", "name": "安装目录",
         "default": "/webber/mysql", "dir_key": "{data_path}",
         "check_msg": "success", "check_flag": "true"},
        {"key": "data_dir", "name": "数据目录",
         "default": "/webber/mysql/data", "dir_key": "{data_path}",
         "check_msg": "success", "check_flag": "true"},
        {"key": "log_dir", "name": "日志目录",
         "default": "/webber/mysql/log", "dir_key": "{data_path}",
         "check_msg": "success", "check_flag": "true"},
        {"key": "username", "name": "用户名", "default": "root"},
        {"key": "password", "name": "密码", "default": "123456"}],
    "service_instance_name": "mysql-7-184"
}


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
        Service.objects.create(
            ip="192.168.0.111",
            service_instance_name="test2-jdk",
            service_status=5,
            alert_count=6,
            self_healing_count=6,
            service_controllers={"start": "1.txt", "stop": "2.txt"},
            service=app_obj,
            service_port=json.dumps([{'default': '18080', 'key': 'http_port'}])
        )

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
        return_value="")
    @mock.patch(
        "promemonitor.prometheus_utils.PrometheusUtils.delete_service",
        return_value=""
    )
    @mock.patch(
        "utils.plugin.salt_client.SaltClient",
        return_value="")
    def test_service_action_delete(self, salt_client, delete_service, status):
        status.side_effect = [
            (True, "success"), (True, "success"), (True, "success")
        ]
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
        DetailInstallHistory.objects.create(
            service=service_obj,
            send_msg="send_log",
            unzip_msg="unzip_log",
            install_msg="install_log",
            init_msg="init_log",
            start_msg="start_log",
            install_detail_args=json.dumps(install_detail)
        )
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
