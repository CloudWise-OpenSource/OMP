# -*- coding: utf-8 -*-
# Project: test_public_utils
# Author: jon.liu@yunzhihui.com
# Create time: 2021-10-09 21:24
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
测试公共工具类
"""

import os
import uuid
from tests.base import BaseTest
from utils.plugin.public_utils import get_file_md5


class GetFileMd5Test(BaseTest):
    """ 获取文件md5值测试 """

    def setUp(self):
        super(GetFileMd5Test, self).setUp()
        self.file_path = os.path.realpath(__file__)

    def test_get_md5_failed_file_not_exist(self):
        """
        测试文件不存在时现象
        :return:
        """
        file_path = self.file_path + str(uuid.uuid4())
        flag, message = get_file_md5(file_path)
        self.assertEqual(flag, False)

    def test_get_md5_success(self):
        """
        测试正常解析时现象
        :return:
        """
        flag, message = get_file_md5(self.file_path)
        self.assertEqual(flag, True)
