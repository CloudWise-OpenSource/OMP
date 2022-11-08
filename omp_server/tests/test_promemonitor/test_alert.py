import json

from rest_framework.reverse import reverse
from unittest import mock

from tests.base import AutoLoginTest, BaseTest
from db_models.models import Alert


class MockResponse:
    """
    自定义mock response类
    """
    status_code = 0

    def __init__(self, data):
        self.text = json.dumps(data)

    def json(self):
        return json.loads(self.text)


class AlertTest(AutoLoginTest):
    """ 告警测试类 """

    def setUp(self):
        super(AlertTest, self).setUp()
        self.list_alert_url = reverse("listAlert-list")
        self.update_alert_url = reverse("updateAlert-list")
        # 正确请求数据
        self.correct_request_data = {'is_read': 1}
        Alert.objects.create(
            is_read=0,
            alert_type='host',
            alert_host_ip='10.0.9.61',
            alert_service_name='',
            alert_instance_name='doim',
            alert_service_type='',
            alert_level='critical',
            alert_describe='zsh',
            alert_receiver='test',
            alert_resolve='',
            alert_time='2021-06-28 12:00:01',
            create_time='2021-06-28 12:00:01',
            monitor_path='-',
            monitor_log='-',
            fingerprint='',
            # env='default'  # TODO 此版本默认不赋值
        )

    def test_get_alerts(self):
        """ 测试获取告警记录 """
        resp = self.get(self.list_alert_url,
                        data={"start_alert_time": "2021-09-11 12:34:56",
                              "end_alert_time": "2021-09-11 12:34:57"}).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")

        resp = self.get(self.list_alert_url,
                        data={"start_alert_time": "2021-09-11 12:34:56"}).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")

        error_time_resp = self.get(self.list_alert_url,
                                   data={"start_alert_time": "2021-09-11 12:34:56", "end_alert_time": "123456"}).json()
        self.assertEqual(error_time_resp.get("code"), 0)
        self.assertEqual(error_time_resp.get("message"), "success")

    request_post_response = {
        "code": 0,
        "message": "success",
        "data": {
            "ids": [
                8,
                9
            ],
            "is_read": 1
        }
    }

    @mock.patch.object(BaseTest, 'post', return_value='')
    def test_update_is_read(self, mock_post):
        """
        修改已读/未读
        """
        mock_post.return_value = MockResponse(self.request_post_response)

        resp = self.post(self.update_alert_url,
                         self.correct_request_data).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertIsNotNone(resp.get('data'))

    def tearDown(self):
        Alert.objects.filter(alert_host_ip='10.0.9.61').delete()
