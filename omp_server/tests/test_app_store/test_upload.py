# -*- coding:utf-8 -*-
# Project: test_upload
# Author:Times.niu@yunzhihui.com
# Create time: 2021/10/13 5:13 下午

import os

from django.conf import settings
from rest_framework.reverse import reverse

from tests.base import AutoLoginTest


class UploadPackageTest(AutoLoginTest):
    """创建上传文件测试类"""

    def setUp(self):
        super(UploadPackageTest, self).setUp()
        self.upload_url = reverse("upload-list")

    def create_fake_file(self, file_end):
        """根据传入的文件后缀（file_end）创建"""
        fake_data = "hello world"
        file_name = "test" + file_end
        file_path = os.path.join(settings.PROJECT_DIR,
                                 "package_hub", file_name)
        with open(file_path, "w+") as f:
            f.write(fake_data)
        return file_path

    def test_error_field(self):
        # 不提供uuid
        file_path = self.create_fake_file(".tar.gz")
        with open(file_path, "rb") as f:
            resp = self.client.post(
                self.upload_url,
                data={"operation_user": "admin", "file": f}
            ).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "必须包含[uuid]字段",
            "data": None
        })

        # 不提供operation_user
        with open(file_path, "rb") as f:
            resp = self.client.post(
                self.upload_url,
                data={"uuid": "63ece2802559e7a37d01daa686d10c4b", "file": f}
            ).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "必须包含[operation_user]字段",
            "data": None
        })

        # 不提供file
        resp = self.post(
            self.upload_url,
            data={"uuid": "63ece2802559e7a37d01daa686d10c4b",
                  "operation_user": "admin"}
        ).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "必须包含[file]字段",
            "data": None
        })

        # 提供非tar tar.gz文件
        file_path_err = self.create_fake_file(".dmg")
        with open(file_path_err, "rb") as f:
            resp = self.client.post(
                self.upload_url,
                data={"uuid": "63ece2802559e7a37d01daa686d10c4b",
                      "operation_user": "admin", "file": f}
            ).json()
            self.assertDictEqual(resp, {
                "code": 1,
                "message": "上传文件名仅支持.tar或.tar.gz",
                "data": None
            })

    def test_correct_field(self):
        # file_path = self.create_fake_file(".tar.gz")
        # with open(file_path, "rb") as f:
        #     resp = self.client.post(
        #         self.upload_url,
        #         data={"uuid": "63ece2802559e7a37d01daa686d10c4b", "operation_user": "admin", "file": f}
        #     ).json()
        #     self.assertDictEqual(resp, {
        #         "code": 0,
        #         "message": "success",
        #         "data": {
        #             "uuid": "63ece280-2559-e7a3-7d01-daa686d10c4b",
        #             "operation_user": "admin",
        #             "file": None
        #         }
        #     })
        pass

    def tearDown(self):
        super(UploadPackageTest, self).tearDown()
        try:
            os.remove(os.path.join(
                settings.PROJECT_DIR, "package_hub", "test.tar.gz"))
            os.remove(os.path.join(
                settings.PROJECT_DIR, "package_hub", "test.dmg"))
        except Exception:
            pass
