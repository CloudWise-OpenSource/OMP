from rest_framework.reverse import reverse

from tests.base import AutoLoginTest
from db_models.models import UserProfile


class UsersTest(AutoLoginTest):
    """ 用户功能测试类 """

    @staticmethod
    def get_user():
        """ 获取用户 """
        user = UserProfile.objects.create_user(
            username="test_user",
            password="test_user",
            email="test_user@cloudwise.com",
        )
        return user

    @staticmethod
    def destroy_user():
        """ 销毁用户 """
        UserProfile.objects.filter(
            username="test_user").delete()

    def setUp(self):
        super(UsersTest, self).setUp()
        self.create_user_url = reverse("users-list")
        self.list_user_url = reverse("users-list")

    def test_create_user(self):
        """ 测试创建用户 """

        # 已存在用户名 -> 无法创建
        resp = self.post(self.create_user_url, {
            "username": self.default_user.username,
            "password": self.default_user.password,
            "re_password": self.default_user.password,
            "email": self.default_user.email,
        }).json()
        self.assertDictEqual(resp, {
            'code': 1,
            'message': '用户名已存在',
            'data': None
        })

        # 两次密码不一致 -> 无法创建
        resp = self.post(self.create_user_url, {
            "username": "new_user",
            "password": "new_password",
            "re_password": "diff_password",
            "email": "user@cloudwise.com",
        }).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "两次密码不一致",
            "data": None
        })

        # 邮箱格式不正确 -> 无法创建
        resp = self.post(self.create_user_url, {
            "username": "new_user",
            "password": "new_password",
            "re_password": "diff_password",
            "email": "this is a email",
        }).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "邮箱格式不正确",
            "data": None
        })

        # 全新用户名，两次密码一致 -> 创建成功
        resp = self.post(self.create_user_url, {
            "username": "new_user",
            "password": "new_password",
            "re_password": "new_password",
            "email": "user@cloudwise.com",
        }).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertTrue(resp.get("data", None) is not None)

    def test_list_user(self):
        """ 测试查询用户列表 """

        # 查询用户列表 -> 查询成功
        resp = self.get(self.create_user_url).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertTrue(resp.get("data", None) is not None)

    def test_retrieve_user(self):
        """ 测试查询一个用户 """

        user = self.get_user()

        # 查询不存在用户 -> 查询失败
        resp = self.get(reverse("users-detail", [9999])).json()
        self.assertDictEqual(resp, {
            'code': 1,
            'message': '未找到',
            'data': None
        })

        # 查询存在用户 -> 查询成功
        resp = self.get(reverse("users-detail", [user.id])).json()
        user_info = resp.get("data", None)
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertTrue(user_info is not None)
        self.assertEqual(user_info.get("username"), user.username)
        self.assertNotEqual(user_info.get("password"), user.password)
        self.assertEqual(user_info.get("email"), user.email)

        self.destroy_user()

    def test_update_user(self):
        """ 测试更新一个已有用户 """

        user = self.get_user()

        # 更新不存在用户 -> 更新失败
        resp = self.put(reverse("users-detail", [9999]), {
            "username": user.username,
            "password": "update_user_pass",
            "re_password": "update_user_pass",
            "email": "update_user@cloudwise.com",
        }).json()
        self.assertDictEqual(resp, {
            'code': 1,
            'message': '未找到',
            'data': None
        })

        # 更新已有用户，密码不一致 -> 更新失败
        resp = self.put(reverse("users-detail", [user.id]), {
            "username": user.username,
            "password": "update_user_pass",
            "re_password": "update_user_pass_diff",
            "email": "update_user@cloudwise.com",
        }).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "两次密码不一致",
            "data": None
        })

        # 更新已有用户，两次密码一致 -> 更新成功
        new_email = "update_user_email@cloudwise.com"
        resp = self.put(reverse("users-detail", [user.id]), {
            "username": user.username,
            "password": "update_user_pass",
            "re_password": "update_user_pass",
            "email": new_email,
        }).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertTrue(resp.get("data", None) is not None)

        self.destroy_user()

    def test_partial_update_user(self):
        """ 测试更新一个现有用户的一个或多个字段 """

        user = self.get_user()

        # 更新不存在用户 -> 更新失败
        resp = self.patch(reverse("users-detail", [9999]), {
            "password": "partial_update_user_pass",
            "re_password": "partial_update_user_pass",
            "email": "partial_update_user_email@cloudwise.com",
        }).json()
        self.assertDictEqual(resp, {
            'code': 1,
            'message': '未找到',
            'data': None
        })

        # 更新存在用户 -> 更新成功
        new_email = "partial_update_user_email@cloudwise.com"
        resp = self.patch(reverse("users-detail", [user.id]), {
            "password": "new_password_one",
            "re_password": "new_password_one",
            "email": new_email,
        }).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertTrue(resp.get("data", None) is not None)

        self.destroy_user()

    def test_delete_user(self):
        """ 测试删除一个现有用户 """

        self.get_user()

        # 删除不存在用户 -> 删除失败
        resp = self.delete(reverse("users-detail", [9999])).json()
        self.assertDictEqual(resp, {
            'code': 1,
            'message': '未找到',
            'data': None
        })

        self.destroy_user()


class UserUpdatePasswordTest(AutoLoginTest):
    """ 用户更新密码测试类 """

    def setUp(self):
        super(UserUpdatePasswordTest, self).setUp()
        self.update_password_url = reverse("updatePassword-list")

    def test_update_password(self):
        """ 测试更新密码 """

        # 原密码错误 -> 更新失败
        resp = self.post(self.update_password_url, {
            "username": self.default_user.username,
            "old_password": "error_password",
            "new_password": "new_password"
        }).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "当前密码不正确",
            "data": None
        })

        # 新密码包含中文特殊符号 -> 更新失败
        resp = self.post(self.update_password_url, {
            "username": self.default_user.username,
            "old_password": "error_password",
            "new_password": "zh。～password"
        }).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "新密码格式不合法",
            "data": None
        })

        # 原密码正确 -> 更新成功
        resp = self.post(self.update_password_url, {
            "username": self.default_user.username,
            "old_password": self.default_user.password,
            "new_password": "new_password"
        }).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertTrue(resp.get("data") is not None)
