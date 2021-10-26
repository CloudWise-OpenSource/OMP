# -*- coding: utf-8 -*-
# Project: test_get_application_template
# Author: jon.liu@yunzhihui.com
# Create time: 2021-10-26 11:33
# IDE: PyCharm
# Version: 1.0
# Introduction:

from rest_framework.reverse import reverse
from django.http.response import FileResponse

from tests.base import AutoLoginTest


class ApplicationTemplateTest(AutoLoginTest):
    """ 主机批量校验测试类 """

    def setUp(self):
        super(ApplicationTemplateTest, self).setUp()
        self.get_template_url = reverse("applicationTemplate-list")

    def test_get_application_template(self):
        """ 获取应用商店导入模板 """

        # 获取应用商店导入模板 -> 返回文件
        resp = self.get(self.get_template_url)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(isinstance(resp, FileResponse))
        self.assertTrue(resp.streaming)
        self.assertTrue(resp.streaming_content is not None)
