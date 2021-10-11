import json

from rest_framework.reverse import reverse
from unittest import mock

from tests.base import AutoLoginTest, BaseTest


class MockResponse:
    """
    自定义mock response类
    """
    status_code = 0

    def __init__(self, data):
        self.text = json.dumps(data)

    def json(self):
        return json.loads(self.text)


class ReceiveAlertTest(AutoLoginTest):
    """ 接收并解析alertmanager告警测试类 """

    def setUp(self):
        super(ReceiveAlertTest, self).setUp()
        self.alerts_url = reverse("alerts-list")
        # 正确请求数据
        self.origin_alert_str = {
            "receiver": "cloudwise",
            "status": "firing",
            "alerts": [
                {
                    "status": "resolved",
                    "labels": {
                        "alertname": "host cpu_used critical alert",
                        "instance": "10.0.7.146",
                        "job": "nodeExporter",
                        "severity": "critical"
                    },
                    "annotations": {
                        "consignee": "123456789@qq.com",
                        "description": "主机 10.0.7.146 CPU 使用率为 10.06%, 大于阈值 10",
                        "summary": "cpu_used (instance 10.0.7.146)"
                    },
                    "startsAt": "2021-06-26T08:13:32.950510932Z",
                    "endsAt": "2021-06-26T08:15:02.950510932Z",
                    "generatorURL": "http://centos7:19011/graph?g0.expr=sum+by%28instance%29+%28avg+without%28cpu%29+"
                                    "%28irate%28node_cpu_seconds_total%7Benv%3D%22caleb%22%2Cmode%21%3D%22idle%22%7D%5B"
                                    "5m%5D%29%29%29+%2A+100+%3E%3D+10&g0.tab=1",
                    "fingerprint": "3e16190fffa56fe0"
                }
            ]
        }
        # self.correct_request_data = {'origin_alert': self.origin_alert_str}

    request_post_response = {
        "code": 0,
        "message": "success",
        "data": {'key': ['...']}
    }

    @mock.patch.object(BaseTest, 'post', return_value='')
    def test_receive_alerts(self, mock_post):
        """
        接收并解析alertmanager告警
        """
        mock_post.return_value = MockResponse(self.request_post_response)
        self.alerts_url = reverse("receive_alert-list")

        resp = self.post(self.alerts_url, self.origin_alert_str).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertIsNotNone(resp.get('data'))
