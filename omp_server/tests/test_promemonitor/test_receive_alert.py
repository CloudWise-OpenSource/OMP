import json

from rest_framework.reverse import reverse

from tests.base import AutoLoginTest
from db_models.models import Host, Alert


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
        self.receive_alert_url = reverse("receiveAlert-list")
        # 正确请求数据
        self.origin_alert_str = {
            "receiver": "cloudwise",
            "status": "firing",
            "alerts": [
                {
                    "status": "firing",
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
        Host.objects.create(
            instance_name="mysql_instance_1",
            ip="10.0.7.146",
            port=36000,
            username="root",
            password="XoIc56a3HiStUZb3Pu9jXEHj8YvMTRpMYnNFD2YS7MA",
            data_folder="/data",
            operate_system="CentOS"
        )

    request_post_response = {
        "code": 0,
        "message": "success",
        "data": {'key': ['...']}
    }

    def test_receive_alerts(self):
        """
        接收并解析alertmanager告警
        """
        # mock_post.return_value = MockResponse(self.request_post_response)

        resp = self.post(self.receive_alert_url, self.origin_alert_str).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertIsNotNone(resp.get('data'))

    def tearDown(self):
        Alert.objects.filter(alert_host_ip='10.0.7.146').delete()
        Host.objects.filter(ip='10.0.7.146').delete()
