# -*- coding:utf-8 -*-
# Project: test_upload_package
# Author:Times.niu@yunzhihui.com
# Create time: 2021/10/13 5:13 下午

import os
import time

from django.conf import settings
from rest_framework.reverse import reverse

from tests.base import AutoLoginTest
from tests.mixin import UploadPackageHistoryMixin
from db_models.models import UploadPackageHistory


class UploadPackageTest(AutoLoginTest):
    """ 创建上传文件测试类 """

    def setUp(self):
        super(UploadPackageTest, self).setUp()
        self.upload_url = reverse("upload-list")

    def create_fake_file(self, file_end):
        """ 根据传入的文件后缀（file_end）创建 """
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
                data={"operation_user": "admin", "file": f,
                      "md5": "dfasdfafadfadfagagate"}
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
                data={"uuid": "63ece2802559e7a37d01daa686d10c4b",
                      "file": f, "md5": "dfasdfafadfadfagagate"}
            ).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "必须包含[operation_user]字段",
            "data": None
        })

        # 不提供md5
        with open(file_path, "rb") as f:
            resp = self.client.post(
                self.upload_url,
                data={"operation_user": "admin",
                      "uuid": "63ece2802559e7a37d01daa686d10c4b", "file": f}
            ).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "必须包含[md5]字段",
            "data": None
        })

        # 不提供file
        resp = self.post(
            self.upload_url,
            data={"uuid": "63ece2802559e7a37d01daa686d10c4b",
                  "operation_user": "admin", "md5": "dfasdfafadfadfagagate"}
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
                      "operation_user": "admin", "file": f, "md5": "dfasdfafadfadfagagate"}
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


class RemovePackageTest(AutoLoginTest, UploadPackageHistoryMixin):
    """ 移除安装包测试类 """

    def setUp(self):
        super(RemovePackageTest, self).setUp()
        self.remove_package_url = reverse("remove-list")

    def test_error_field(self):
        """ 测试错误字段 """

        history_objs = self.get_upload_package_history(number=1)
        operation_uuid = history_objs[0].operation_uuid
        package_name_ls = list(
            history_objs.values_list("package_name", flat=True))

        # 不提供 uuid -> 移除失败
        resp = self.post(self.remove_package_url, {
            "package_names": package_name_ls
        }).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "必须包含[uuid]字段",
            "data": None
        })

        # 提供无效 uuid -> 移除失败
        resp = self.post(self.remove_package_url, {
            "uuid": str(int(round(time.time() * 1000))),
            "package_names": package_name_ls
        }).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "该 uuid 未找到有效的操作记录",
            "data": None
        })

        # 不提供 package_names -> 移除失败
        resp = self.post(self.remove_package_url, {
            "uuid": operation_uuid,
        }).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "必须包含[package_names]字段",
            "data": None
        })

        # 提供无效 package_names -> 移除失败
        resp = self.post(self.remove_package_url, {
            "uuid": operation_uuid,
            "package_names": ["111", "222", "333"]
        }).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "该 uuid 未找到有效的操作记录",
            "data": None
        })

        self.destroy_upload_package_history()

    def test_correct_field(self):
        """ 测试正确字段 """

        history_objs = self.get_upload_package_history(number=1)
        operation_uuid = history_objs[0].operation_uuid
        package_name_ls = list(
            history_objs.values_list("package_name", flat=True))

        # 正确参数 -> 移除成功
        resp = self.post(self.remove_package_url, {
            "uuid": operation_uuid,
            "package_names": package_name_ls
        }).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        # 安装包历史记录标记软删除
        queryset = UploadPackageHistory.objects.filter(
            operation_uuid=operation_uuid, package_name__in=package_name_ls)
        for history in queryset:
            self.assertTrue(history.is_deleted)

        self.destroy_upload_package_history()
