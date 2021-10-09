from rest_framework.reverse import reverse

from tests.base import AutoLoginTest
from promemonitor.alertmanager import Alertmanager


class GlobalMaintainTest(AutoLoginTest):
    """ 全局维护测试类 """

    def setUp(self):
        super(GlobalMaintainTest, self).setUp()
        self.global_maintain_url = reverse("global_maintain-list")
        # 正确主机数据
        self.correct_maintain_data = {
            "matcher_name": "env_name",
            "matcher_value": "default"
        }

    def test_set_global_maintain(self):
        """ 测试设置全局维护 """
        resp = self.get(self.global_maintain_url).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertTrue(resp.get("data") is not None)
        # print('已设置全局维护:', resp)

        # 删除主机
        self.revoke_global_maintain(self.correct_maintain_data)

    def revoke_global_maintain(self, maintain_data):
        alertmanager = Alertmanager()
        alertmanager.revoke_maintain_by_env_name(env_name='default')
        # print(self.global_maintain_url)
        # print('已取消全局维护:', maintain_data)
