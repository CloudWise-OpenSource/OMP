# -*- coding: utf-8 -*-
# Project: test_execute_package_scan
# Author: jon.liu@yunzhihui.com
# Create time: 2021-10-19 21:04
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
服务端本地扫描测试方法
"""

from unittest import mock

from rest_framework.reverse import reverse

from tests.base import AutoLoginTest


class ExecutePackageScanTest(AutoLoginTest):
    def setUp(self):
        super(ExecutePackageScanTest, self).setUp()
        self.executeLocalPackageScan_url = reverse(
            "executeLocalPackageScan-list")

    @mock.patch(
        "app_store.tmp_exec_back_task.back_end_verified_init",
        return_value=("uuid", []))
    def test_request_success(self, mock_obj):
        resp = self.post(
            url=self.executeLocalPackageScan_url, data=None).json()
        self.assertDictEqual(resp, {
            "code": 0,
            "message": "success",
            "data": {
                "uuid": "uuid",
                "package_name_lst": []
            }
        })
