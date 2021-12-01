import json
import os
import shutil

import requests
import yaml
from rest_framework.reverse import reverse
from unittest import mock

from tests.base import AutoLoginTest
from db_models.models import EmailSMTPSetting, AlertSendWaySetting
from omp_server.settings import PROJECT_DIR


class MockResponse:
    """
    自定义mock response类
    """
    status = 200

    def __init__(self, data):
        self.text = json.dumps(data)
        self.status_code = self.status

    def json(self):
        return json.loads(self.text)


class EmailConfig(AutoLoginTest):

    @staticmethod
    def delete_conf_dir():
        """
        删除alertmanager文件
        :return:
        """
        alertmanager_conf_dir = os.path.join(
            PROJECT_DIR, "component/alertmanager/conf")
        if os.path.exists(alertmanager_conf_dir):
            shutil.rmtree(alertmanager_conf_dir)

    def setUp(self):
        super(EmailConfig, self).setUp()
        self.delete_conf_dir()
        alertmanager_conf_dir = os.path.join(
            PROJECT_DIR, "component/alertmanager/conf")
        if not os.path.exists(alertmanager_conf_dir):
            os.makedirs(alertmanager_conf_dir)
        alertmanager_conf_dict = {"global": {"resolve_timeout": "5m", "smtp_from": "1jayden.liu@cloudwise.com",
                                             "smtp_smarthost": "smtp.feishu.cn:465",
                                             "smtp_auth_username": "jayden.liu@cloudwise.com",
                                             "smtp_auth_password": "Pc6qjfofl0TaqTlf", "smtp_require_tls": False,
                                             "smtp_hello": "qq.com"},
                                  "templates": ["/data/omp/omp_monitor/promemonitor/alertmanager/templates/*tmpl"],
                                  "route": {"group_by": ["instance"], "group_wait": "10s", "group_interval": "10s",
                                            "repeat_interval": "1m", "receiver": "commonuser"}, "receivers": [
            {"name": "commonuser", "email_configs": [
                {"to": "lingyang.guo@cloudwise.com", "headers": {"Subject": "OMP ALERT"},
                     "html": "{{ template \"email.to.html\" . }}"}]}], "inhibit_rules": [
            {"source_match": {"severity": "critical"}, "target_match": {"severity": "warning"},
             "equal": ["instance", "job", "alertname"]}]}
        with open(os.path.join(alertmanager_conf_dir, "alertmanager.yml"), "w", encoding="utf8") as ay_fp:
            yaml.dump(alertmanager_conf_dict, ay_fp, allow_unicode=True)

        self.esc_get_url = reverse("getSendEmailConfig-list")
        self.esc_update_url = reverse("updateSendEmailConfig-list")
        self.rsc_get_url = reverse("getSendAlertSetting-list")
        self.rsc_update_url = reverse("updateSendAlertSetting-list")
        self.ess = EmailSMTPSetting.objects.create(
            email_host="123@qq.com",
            email_port="465",
            email_host_user="test_user",
            email_host_password="test_password"
        )
        self.asws = AlertSendWaySetting.objects.create(
            used=True,
            env_id=1,
            way_name="email",
            server_url="123@qq.com",
            way_token="123",
            extra_info=""
        )

    def tearDown(self):
        super(EmailConfig, self).tearDown()
        self.ess.delete()
        self.asws.delete()
        self.delete_conf_dir()

    def test_get_email_smtp_config(self):
        resp = self.get(self.esc_get_url).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertTrue(resp.get("data") is not None)

    @mock.patch.object(requests, 'post', return_value=None)
    def test_update_smtp_config(self, mock_post=None):
        mock_post.return_value = MockResponse(
            {"status": "success", "status_code": 200})
        post_data = {
            "host": "smtp.163.com",
            "port": 465,
            "username": "123456789@qq.com",
            "password": "12345"
        }
        resp = self.post(self.esc_update_url, data=post_data).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertTrue(resp.get("data") is not None)

    def test_get_send_alert_config(self):
        resp = self.get(self.rsc_get_url).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertTrue(resp.get("data") is not None)

    @mock.patch.object(requests, 'post', return_value=None)
    def test_update_send_alert_config(self, mock_post=None):
        mock_post.return_value = MockResponse(
            {"status": "success", "status_code": 200})
        post_data = {"way_name": "email",
                     "server_url": "98765432dd2@qq.com", "used": True, "env_id": 0}
        resp = self.post(self.rsc_update_url, data=post_data).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertTrue(resp.get("data") is not None)
