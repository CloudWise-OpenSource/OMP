import json

from django.test import TestCase
from django.urls import reverse

from db_models.models import UserProfile


class BaseTest(TestCase):
    """ 测试基础类 """

    def setUp(self):
        self.login_url = reverse("login")
        self.username = "admin"
        self.password = "adminPassword"
        self.user = UserProfile.objects.create_user(
            username=self.username,
            password=self.password,
            email="admin@cloudwise.com",
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

    def delete(self, url, data):
        return self.client.delete(
            url,
            data=json.dumps(data),
            content_type="application/json; charset=utf-8",
        )

    def put(self, url, data):
        return self.client.put(
            url,
            data=json.dumps(data),
            content_type="application/json; charset=utf-8",
        )
