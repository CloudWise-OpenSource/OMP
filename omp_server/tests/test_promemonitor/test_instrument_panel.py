import json
from unittest import mock

import requests
from rest_framework.reverse import reverse

from tests.base import AutoLoginTest
from db_models.models import MonitorUrl


class MockResponse:
    """
    自定义mock response类
    """
    status_code = 200

    def __init__(self, data):
        self.text = json.dumps(data)

    def json(self):
        return json.loads(self.text)


class InstrumentPanelTest(AutoLoginTest):

    def setUp(self):
        super(InstrumentPanelTest, self).setUp()
        MonitorUrl.objects.create(
            name='prometheus', monitor_url='127.0.0.1:19011')
        self.instrument_panel_url = reverse("instrumentPanel-list")

    @staticmethod
    def return_prometheus_alerts_response():
        prometheus_alerts_response = MockResponse(
            {
                "status": "success",
                "data": {
                    "alerts": [
                        {
                            "labels": {
                                "alertname": "实例宕机",
                                "instance": "10.0.3.71",
                                "service_type": "host",
                                "service_name": "node",
                                "instance_name": "dosm1",
                                "job": "nodeExporter",
                                "severity": "critical"
                            },
                            "annotations": {
                                "consignee": "987654321@qq.com",
                                "description": "实例 10.0.3.71 已宕机超过1分钟",
                                "summary": "实例宕机(10.0.3.71)"
                            },
                            "state": "firing",
                            "activeAt": "2021-10-16T08:16:24.495164774Z",
                            "value": "0e+00"
                        },
                        {
                            "labels": {
                                "alertname": "mysql down",
                                "instance": "10.0.3.72",
                                "service_type": "database",
                                "service_name": "mysql",
                                "instance_name": "mysql1",
                                "job": "mysqlExporter",
                                "severity": "critical"
                            },
                            "annotations": {
                                "consignee": "987654321@qq.com",
                                "description": "实例 10.0.3.72 已宕机超过1分钟",
                                "summary": "实例宕机(10.0.3.72)"
                            },
                            "state": "firing",
                            "activeAt": "2021-10-16T08:16:05.68330499Z",
                            "value": "0e+00"
                        },
                        {
                            "labels": {
                                "alertname": "alertChanel down",
                                "instance": "10.0.3.72",
                                "service_type": "service",
                                "service_name": "alertChanel",
                                "instance_name": "alertChanel",
                                "job": "alertChanelExporter",
                                "severity": "critical"
                            },
                            "annotations": {
                                "consignee": "987654321@qq.com",
                                "description": "实例 10.0.3.72 已宕机超过1分钟",
                                "summary": "实例宕机(10.0.3.72)"
                            },
                            "state": "firing",
                            "activeAt": "2021-10-16T08:16:05.68330499Z",
                            "value": "0e+00"
                        },
                        {
                            "labels": {
                                "alertname": "zookeeper down",
                                "instance": "10.0.3.72",
                                "service_type": "component",
                                "service_name": "zookeeper",
                                "instance_name": "alertChanel",
                                "job": "zookeeperExporter",
                                "severity": "critical"
                            },
                            "annotations": {
                                "consignee": "987654321@qq.com",
                                "description": "实例 10.0.3.72 已宕机超过1分钟",
                                "summary": "实例宕机(10.0.3.72)"
                            },
                            "state": "firing",
                            "activeAt": "2021-10-16T08:16:05.68330499Z",
                            "value": "0e+00"
                        },
                        {
                            "labels": {
                                "alertname": "custom_kafka down",
                                "instance": "10.0.3.75",
                                "service_type": "third",
                                "service_name": "kafka",
                                "instance_name": "custom_kafka",
                                "job": "kafkaExporter",
                                "severity": "critical"
                            },
                            "annotations": {
                                "consignee": "987654321@qq.com",
                                "description": "实例 10.0.3.72 已宕机超过1分钟",
                                "summary": "实例宕机(10.0.3.72)"
                            },
                            "state": "firing",
                            "activeAt": "2021-10-16T08:16:05.68330499Z",
                            "value": "0e+00"
                        }
                    ]
                }
            })
        return prometheus_alerts_response

    @mock.patch.object(requests, 'get', return_value='')
    def test_instrument_panel(self, mock_get):
        mock_get.return_value = self.return_prometheus_alerts_response()
        resp = self.get(self.instrument_panel_url).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertTrue(resp.get("data") is not None)

    def tearDown(self):
        super(InstrumentPanelTest, self).tearDown()
