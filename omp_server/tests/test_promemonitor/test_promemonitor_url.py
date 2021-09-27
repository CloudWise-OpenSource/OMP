from rest_framework.reverse import reverse
from utils.parse_config import MONITOR_PORT
from tests.base import AutoLoginTest
from db_models.models import MonitorUrl


class PromemonitorTest(AutoLoginTest):

    def setUp(self):
        super(PromemonitorTest, self).setUp()
        self.create_monitorurl_url = reverse("monitorurl-list")
        self.multiple_update = self.create_monitorurl_url + "multiple_update/"
        MonitorList = []
        local_ip = "127.0.0.1:"
        MonitorList.append(MonitorUrl(id="1", name="prometheus",
                                      monitor_url=local_ip + str(MONITOR_PORT.get("prometheus", "19011"))))
        MonitorList.append(MonitorUrl(id="2", name="alertmanager",
                                      monitor_url=local_ip + str(MONITOR_PORT.get("alertmanager", "19013"))))
        MonitorList.append(MonitorUrl(
            id="3", name="grafana", monitor_url=local_ip + str(MONITOR_PORT.get("grafana", "19014"))))
        MonitorUrl.objects.bulk_create(MonitorList)

    def test_list_promeurl(self):
        """ 测试监控配置列表 """

        # 查询配置列表 -> 查询成功
        resp = self.get(self.create_monitorurl_url).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertTrue(resp.get("data", None) is not None)

    def test_create_promeurl(self):
        # name名字重复 -> 无法创建
        resp = self.post(self.create_monitorurl_url, {
            "name": "prometheus",
            "monitor_url": "127.0.0.1:8080",
        }).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "name: name已经存在;",
            "data": None
        })
        # name名字重复,批量创建 -> 无法创建
        resp = self.post(self.create_monitorurl_url, [{
            "name": "prometheus",
            "monitor_url": "127.0.0.1:8080",
        }]).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "non_field_errors: name字段已经存在,detail:prometheus;",
            "data": None
        })

        # name名字空 -> 无法创建
        resp = self.post(self.create_monitorurl_url, {
            "monitor_url": "127.0.0.1:8080",
        }).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "name: This field is required.;",
            "data": None
        })

        # name名字空,批量创建 -> 无法创建
        resp = self.post(self.create_monitorurl_url, [{
            "monitor_url": "127.0.0.1:8080",
        }]).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "non_field_errors: name字段不为空;",
            "data": None
        })

        # name字段超限 -> 无法创建
        resp = self.post(self.create_monitorurl_url, {
            "name": "prometheusprometheusprometheusprometheusprometheusprometheusprometheusprometheus",
            "monitor_url": "127.0.0.1:8080",
        }).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "name: Ensure this field has no more than 32 characters.;",
            "data": None
        })

        # name字段超限,批量创建 -> 无法创建
        resp = self.post(self.create_monitorurl_url, [{
            "name": "prometheusprometheusprometheusprometheusprometheusprometheusprometheusprometheus",
            "monitor_url": "127.0.0.1:8080",
        }]).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "non_field_errors: name字段长度超过32,detail:prometheusprometheusprometheusprometheusprometheusprometheusprometheusprometheus;",
            "data": None
        })

        # monitor_url字段空 -> 无法创建
        resp = self.post(self.create_monitorurl_url, {
            "name": "test1",
        }).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "monitor_url: This field is required.;",
            "data": None
        })

        # monitor_url字段空,批量 -> 无法创建
        resp = self.post(self.create_monitorurl_url, [{
            "name": "test1",
        }]).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "non_field_errors: monitor_url是必须字段;",
            "data": None
        })

        # 创建成功
        resp = self.post(self.create_monitorurl_url, {
            "name": "test1",
            "monitor_url": "127.0.0.1:8080",
        }).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")

        # 成功批量
        resp = self.post(self.create_monitorurl_url, [{
            "name": "test3",
            "monitor_url": "127.0.0.1:8080"
        },
            {
                "name": "test2",
                "monitor_url": "127.0.0.1:8080"
        }
        ]).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")

    def test_partial_update_promeurl(self):
        # 修改url, -> 创建成功
        resp = self.patch(self.multiple_update, [{
            "id": "3",
            "monitor_url": "127.0.0.1:19999"
        }]).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")

        # 修改url批量, -> 创建成功
        resp = self.patch(self.multiple_update, [
            {
                "id": "2",
                "monitor_url": "127.0.0.1:29999"
            }, {
                "id": "3",
                "monitor_url": "127.0.0.1:19999"
            }]).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
