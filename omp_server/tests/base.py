import json

from django.test import TestCase

from rest_framework.reverse import reverse

from db_models.models import UserProfile


class BaseTest(TestCase):
    """ 测试基础类 """

    def setUp(self):
        self.login_url = reverse("login")
        self.username = "admin"
        self.password = "adminPassword"
        self.email = "admin@cloudwise.com"
        self.user = UserProfile.objects.create_user(
            username=self.username,
            password=self.password,
            email=self.email,
        )

    def get(self, url, data=None):
        return self.client.get(
            url,
            data=json.dumps(data) if data else None,
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
            "username": self.username,
            "password": self.password,
        }
        if remember:
            login_data["remember"] = True
        resp = self.post(self.login_url, login_data)
        return resp

    def logout(self):
        """ 退出登录，清除 cookies 中的 token 令牌 """
        self.client.cookies.pop("jwtToken")
