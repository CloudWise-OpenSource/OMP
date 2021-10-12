# -*- coding: utf-8 -*-
# Project: test_grafana_views
# Author: jon.liu@yunzhihui.com
# Create time: 2021-10-12 10:55
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
grafana views测试类
"""

import requests

from unittest import mock

from tests.base import BaseTest
from db_models.models import MonitorUrl


class MockResponse(object):
    """
    自定义mock response类
    """

    def __init__(self, headers=None):
        self.content = "success"
        self.headers = headers
        self.status_code = 200


class TestGrafanaViews(BaseTest):

    def setUp(self):
        super(TestGrafanaViews, self).setUp()
        MonitorUrl.objects.create(
            name='grafana', monitor_url='127.0.0.1:19014')

    @mock.patch.object(
        requests, "request", return_value=MockResponse(headers=dict()))
    def test_success(self, request):
        res = self.get(url="/proxy/v1/grafana/")
        self.assertEqual(res.status_code, 200)

    @mock.patch.object(
        requests, "request", return_value=MockResponse(headers=None))
    def test_failed_connected(self, request):
        res = self.get(url="/proxy/v1/grafana/")
        self.assertEqual(res.status_code, 200)
