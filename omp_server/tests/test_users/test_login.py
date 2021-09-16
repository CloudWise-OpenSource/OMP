import datetime

from rest_framework.reverse import reverse

from tests.base import BaseTest


class LoginTest(BaseTest):
    """ 登录功能测试类 """

    def setUp(self):
        super(LoginTest, self).setUp()
        self.login_url = reverse("login")
        self.users_list_url = reverse("users-list")

    def test_login(self):
        """ 测试用户登录 """

        # 用户名错误 -> 登录失败
        resp = self.post(self.login_url, {
            "username": "wrong_user",
            "password": self.password,
        }).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "Unable to log in with provided credentials. ",
            "data": None,
        })

        # 密码错误 -> 登录失败
        resp = self.post(self.login_url, {
            "username": self.username,
            "password": "wrong_password",
        }).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "Unable to log in with provided credentials. ",
            "data": None,
        })

        # 用户名、密码错误 -> 登录失败
        resp = self.post(self.login_url, {
            "username": "wrong_user",
            "password": "wrong_password",
        }).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "Unable to log in with provided credentials. ",
            "data": None,
        })

        # 用户名、密码正确 -> 登录成功，生成 token 令牌
        resp = self.post(self.login_url, {
            "username": self.username,
            "password": self.password,
        }).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertIn("token", resp.get("data"))

    def test_access_api(self):
        """ 测试访问 API """

        # 未登录用户 -> 无法访问，提示 "未认证"
        resp = self.get(self.users_list_url).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "未认证",
            "data": None,
        })

        # 已登录用户 -> 允许访问
        self.login()
        resp = self.get(self.users_list_url).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")

        # 退出登录 -> 无法访问，提示 "未认证"
        self.logout()
        resp = self.get(self.users_list_url).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "未认证",
            "data": None,
        })

    def test_jwt_expiration(self):
        """ 测试 jwt 过期时间 """

        # 登录 (默认) -> jwt 过期时间 1 天
        self.login()
        gmt_time = self.client.cookies.get("jwtToken").get("expires")
        expiration_time = datetime.datetime.strptime(
            gmt_time, "%a, %d %b %Y %H:%M:%S GMT"
        ) + datetime.timedelta(hours=8)
        expiration_day = expiration_time.day - datetime.datetime.now().day
        self.assertEqual(expiration_day, 1)
        self.logout()

        # 登录 (记住密码) -> jwt 过期时间 7 天
        self.login(remember=True)
        gmt_time = self.client.cookies.get("jwtToken").get("expires")
        expiration_time = datetime.datetime.strptime(
            gmt_time, "%a, %d %b %Y %H:%M:%S GMT"
        ) + datetime.timedelta(hours=8)
        expiration_day = expiration_time.day - datetime.datetime.now().day
        self.assertEqual(expiration_day, 7)
        self.logout()
