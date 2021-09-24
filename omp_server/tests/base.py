import json

from django.test import TestCase

from rest_framework.reverse import reverse

from db_models.models import UserProfile, Env


class BaseTest(TestCase):
    """ 测试基础类 """

    def setUp(self):
        self.login_url = reverse("login")
        # 创建默认用户
        self.default_user = self.create_default_user()
        self.default_env = self.create_default_env()

    def get(self, url, data=None):
        return self.client.get(
            url,
            data=data if data else None,
        )

    def post(self, url, data):
        return self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json; charset=utf-8",
        )

    def delete(self, url, data=None):
        return self.client.delete(
            url,
            data=json.dumps(data) if data else None,
            content_type="application/json; charset=utf-8",
        )

    def put(self, url, data):
        return self.client.put(
            url,
            data=json.dumps(data),
            content_type="application/json; charset=utf-8",
        )

    def patch(self, url, data):
        return self.client.patch(
            url,
            data=json.dumps(data),
            content_type="application/json; charset=utf-8",
        )

    def login(self, remember=False):
        """ 登录，签发 token 令牌 """
        login_data = {
            "username": self.default_user.username,
            "password": self.default_user.password,
        }
        if remember:
            login_data["remember"] = True
        resp = self.post(self.login_url, login_data)
        return resp

    def logout(self):
        """ 退出登录，清除 cookies 中的 token 令牌 """
        self.client.cookies.pop("jwtToken")

    @staticmethod
    def create_default_user():
        """ 创建默认用户 """
        queryset = UserProfile.objects.filter(username="admin")
        if queryset.exists():
            return
        user_obj = UserProfile.objects.create_user(
            username="admin",
            password="adminPassword",
            email="admin@cloudwise.com",
        )
        user_obj.password = "adminPassword"
        return user_obj

    @staticmethod
    def create_default_env():
        """ 创建默认环境 """
        queryset = Env.objects.filter(id=1)
        if queryset.exists():
            return
        return Env.objects.create(id=1, name="default")


class AutoLoginTest(BaseTest):
    """ 自动登录测试基类 """

    def setUp(self):
        super(AutoLoginTest, self).setUp()
        self.login()

    def tearDown(self):
        super(AutoLoginTest, self).tearDown()
        self.logout()
