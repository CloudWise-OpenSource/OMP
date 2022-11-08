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
import uuid
from unittest import mock

from rest_framework.reverse import reverse

from tests.base import AutoLoginTest
from db_models.models import UploadPackageHistory


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
                "package_names": []
            }
        })


class LocalPackageScanResultTest(AutoLoginTest):
    def setUp(self):
        super(LocalPackageScanResultTest, self).setUp()
        self.localPackageScanResult_url = reverse(
            "localPackageScanResult-list")
        self.operation_uuid = str(uuid.uuid4())
        self.operation_user = "admin"
        self.package_name_pre = "test_"
        self.package_path = "/tmp"
        self.package_names_lst = list()
        upload_package_history = list()
        for i in range(10):
            _obj = UploadPackageHistory(
                operation_uuid=self.operation_uuid,
                operation_user=self.operation_user,
                package_name=self.package_name_pre + f"{str(i)}.tar.gz",
                package_md5=str(uuid.uuid4())
            )
            self.package_names_lst.append(
                self.package_name_pre + f"{str(i)}.tar.gz")
            upload_package_history.append(_obj)
        UploadPackageHistory.objects.bulk_create(upload_package_history)

    def test_get_failed_1(self):
        resp = self.get(url=self.localPackageScanResult_url)
        self.assertEqual(resp.json().get("code"), 1)
        self.assertEqual(
            resp.json().get("message"), "请求参数中必须包含 [uuid] 字段")

    def test_get_failed_2(self):
        resp = self.get(
            url=self.localPackageScanResult_url,
            data={
                "uuid": self.operation_uuid
            }
        )
        self.assertEqual(
            resp.json().get("message"), "请求参数中必须包含 [package_names] 字段")

    def get_success_resp(self):
        """
        获取响应值
        :return:
        """
        return self.get(
            url=self.localPackageScanResult_url,
            data={
                "uuid": self.operation_uuid,
                "package_names": ",".join(self.package_names_lst)
            }
        )

    def test_get_success(self):
        self.assertEqual(self.get_success_resp().json().get("code"), 0)

    def test_checking_status(self):
        res_dic = self.get_success_resp().json()
        status = res_dic.get("data", {}).get("stage_status")
        self.assertEqual(status, "checking")

    def test_check_all_failed_status(self):
        UploadPackageHistory.objects.filter(
            operation_uuid=self.operation_uuid).update(
            package_status=1)
        res_dic = self.get_success_resp().json()
        status = res_dic.get("data", {}).get("stage_status")
        self.assertEqual(status, "check_all_failed")

    def test_published_status(self):
        UploadPackageHistory.objects.filter(
            operation_uuid=self.operation_uuid).update(
            package_status=3)
        res_dic = self.get_success_resp().json()
        status = res_dic.get("data", {}).get("stage_status")
        self.assertEqual(status, "published")

    def test_publishing_status(self):
        UploadPackageHistory.objects.filter(
            operation_uuid=self.operation_uuid).update(
            package_status=5)
        res_dic = self.get_success_resp().json()
        status = res_dic.get("data", {}).get("stage_status")
        self.assertEqual(status, "publishing")
