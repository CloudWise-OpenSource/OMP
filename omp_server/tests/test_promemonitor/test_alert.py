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


class GetInstanceNameListTest(AutoLoginTest):
    """ 获取主机和应用实例名测试类 """

    def setUp(self):
        super(GetInstanceNameListTest, self).setUp()
        self.alerts_url = reverse("alerts-list")
        # 正确请求数据
        self.correct_request_data = {'is_read': 1}

    def test_get_alerts(self):
        """ 测试获取主机和应用实例名 """
        resp = self.get(self.alerts_url).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")

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
        self.alerts_url = reverse("alerts-list")

        resp = self.post(self.alerts_url, self.correct_request_data).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertIsNotNone(resp.get('data'))
