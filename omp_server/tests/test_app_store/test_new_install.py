# -*- coding: utf-8 -*-
# Project: test_new_install
# Author: jon.liu@yunzhihui.com
# Create time: 2021-11-25 16:37
# IDE: PyCharm
# Version: 1.0
# Introduction:

import json

from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from db_models.models import (
    UserProfile
)

from tests.base import BaseTest
from tests.test_app_store.install_data_source import (
    create_product, create_host
)


class BatchInstallEntranceTest(BaseTest):
    def setUp(self):
        create_host()
        create_product()
        user = UserProfile.objects.create(username="admin")
        self.client = APIClient()
        self.client.force_authenticate(user)
        self.batchInstallEntrance_url = reverse("batchInstallEntrance-list")

    def test_success_1(self, *args, **kwargs):
        res = self.client.get(
            path=self.batchInstallEntrance_url
        )
        data = res.json().get("data")
        self.assertTrue(len(data) != 0)
        self.client.get(
            path=self.batchInstallEntrance_url,
            data={"product_name": "test"}
        )


class CreateInstallInfoTest(BaseTest):
    def setUp(self):
        create_host()
        create_product()
        user = UserProfile.objects.create(username="admin")
        self.client = APIClient()
        self.client.force_authenticate(user)
        self.createInstallInfo_url = reverse("createInstallInfo-list")

    def test_success_1(self, *args, **kwargs):
        res = self.client.get(
            path=reverse("batchInstallEntrance-list")
        )
        data = res.json().get("data")
        unique_key = data["unique_key"]
        res = self.client.post(
            path=self.createInstallInfo_url,
            data=json.dumps({
                "high_availability": False,
                "install_product": [
                    {
                        "name": "test",
                        "version": "1.0.0"
                    }
                ],
                "unique_key": unique_key
            }),
            content_type="application/json"
        )
        data = res.json().get("data")
        is_continue = data.get("is_continue")
        self.assertFalse(is_continue)
