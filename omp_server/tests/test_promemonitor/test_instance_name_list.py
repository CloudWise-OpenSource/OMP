from rest_framework.reverse import reverse

from tests.base import AutoLoginTest


class GetInstanceNameListTest(AutoLoginTest):
    """ 获取主机和应用实例名测试类 """

    def setUp(self):
        super(GetInstanceNameListTest, self).setUp()
        self.instance_name_list_url = reverse("instanceNameList-list")
        # 正确主机数据

    def test_get_instance_name_list(self):
        """ 测试获取主机和应用实例名 """
        resp = self.get(self.instance_name_list_url).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
