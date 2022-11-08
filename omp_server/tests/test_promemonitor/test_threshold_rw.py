import json
import os
import shutil

import requests
from rest_framework.reverse import reverse
from unittest import mock

from db_models.models import HostThreshold, ServiceThreshold, ServiceCustomThreshold
from tests.base import AutoLoginTest
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


class ThresholdRW(AutoLoginTest):

    @staticmethod
    def delete_conf_dir():
        """
        删除prometheus文件
        :return:
        """
        prometheus_conf_dir = os.path.join(
            PROJECT_DIR, "component/prometheus/conf")
        if os.path.exists(prometheus_conf_dir):
            shutil.rmtree(prometheus_conf_dir)

    def setUp(self):
        super(ThresholdRW, self).setUp()
        self.delete_conf_dir()
        prometheus_conf_dir = os.path.join(
            PROJECT_DIR, "component/prometheus/conf")
        prometheus_rules_dir = os.path.join(prometheus_conf_dir, "rules")
        if not os.path.exists(prometheus_rules_dir):
            os.makedirs(prometheus_rules_dir)

        default_node_yml_file = os.path.join(
            prometheus_rules_dir, "default_node_rule.yml")
        with open(default_node_yml_file, 'w') as fp:
            fp.write("default_node_yml_dict")

        self.host_threshold_rw_url = reverse("hostThreshold-list")
        self.service_threshold_rw_url = reverse("serviceThreshold-list")
        self.custom_threshold_rw_url = reverse("customThreshold-list")

        self.host_threshold = HostThreshold.objects.create(
            index_type="cpu_used",
            condition=">=",
            condition_value="90",
            alert_level="critical",
            env_id=1
        )
        self.service_threshold = ServiceThreshold.objects.create(
            index_type="cpu_used",
            condition=">=",
            condition_value="90",
            alert_level="critical",
            env_id=1
        )
        self.custom_threshold = ServiceCustomThreshold.objects.create(
            service_name="kafka",
            index_type="cpu_used",
            condition=">=",
            condition_value="90",
            alert_level="critical",
            env_id=1
        )

    def tearDown(self):
        super(ThresholdRW, self).tearDown()
        self.delete_conf_dir()
        self.host_threshold.delete()
        self.service_threshold.delete()
        self.custom_threshold.delete()

    def test_get_host_threshold_config(self):
        resp = self.get(f"{self.host_threshold_rw_url}{'?env_id=1'}").json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertTrue(resp.get("data") is not None)

    @mock.patch.object(requests, 'post', return_value=None)
    def test_update_host_threshold_config(self, mock_post=None):
        post_data = {
            "update_data": {
                "cpu_used": [
                    {
                        "index_type": "cpu_used",
                        "condition": ">=",
                        "value": 91,
                        "level": "critical"
                    },
                    {
                        "index_type": "cpu_used",
                        "condition": ">=",
                        "value": "80",
                        "level": "warning"
                    }]},
            "env_id": 1}
        resp = self.post(self.host_threshold_rw_url, data=post_data).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertTrue(resp.get("data") is not None)

    def test_get_service_threshold_config(self):
        resp = self.get(f"{self.service_threshold_rw_url}{'?env_id=1'}").json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertTrue(resp.get("data") is not None)

    @mock.patch.object(requests, 'post', return_value=None)
    def test_update_service_threshold_config(self, mock_post=None):
        post_data = {
            "update_data": {
                "cpu_used": [
                    {
                        "index_type": "cpu_used",
                        "condition": ">=",
                        "value": 91,
                        "level": "critical"
                    },
                    {
                        "index_type": "cpu_used",
                        "condition": ">=",
                        "value": "80",
                        "level": "warning"
                    }]},
            "env_id": 1}
        resp = self.post(self.service_threshold_rw_url, data=post_data).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertTrue(resp.get("data") is not None)

    def test_get_custom_threshold_config(self):
        resp = self.get(f"{self.custom_threshold_rw_url}{'?env_id=1'}").json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertTrue(resp.get("data") is not None)

    @mock.patch.object(requests, 'post', return_value=None)
    def test_update_custom_threshold_config(self, mock_post=None):
        post_data = {
            "env_id": 1,
            "service_name": "kafka",
            "index_type": "kafka_consumergroup_lag",
            "index_type_info": [
                {
                    "condition": ">=",
                    "index_type": "kafka_consumergroup_lag",
                    "level": "critical",
                    "value": 5000
                },
                {
                    "condition": ">=",
                    "index_type": "kafka_consumergroup_lag",
                    "level": "warning",
                    "value": 3000
                }
            ]
        }
        resp = self.post(self.custom_threshold_rw_url, data=post_data).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertTrue(resp.get("data") is not None)
