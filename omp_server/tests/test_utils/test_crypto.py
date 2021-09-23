# -*- coding: utf-8 -*-
# Project: test_crypto
# Author: jon.liu@yunzhihui.com
# Create time: 2021-09-23 20:00
# IDE: PyCharm
# Version: 1.0
# Introduction:

from tests.base import BaseTest
from utils.plugin.crypto import AESCryptor


class CryptoUtilTest(BaseTest):
    """ 主机Agent的测试类 """

    def setUp(self):
        super(CryptoUtilTest, self).setUp()
        self.aes_obj = AESCryptor()
        self.test_str = "testStrings"
        self.encode_str = "uea_xeU_d_6YHCCY7Q-e2xZolSw2z2C3KGhLY6iMdnI"

    def test_encode_success(self):
        """
        测试加密
        :return:
        """
        self.assertEqual(self.encode_str, self.aes_obj.encode(self.test_str))

    def test_decode_success(self):
        """
        测试解密
        :return:
        """
        self.assertEqual(self.test_str, self.aes_obj.decode(self.encode_str))
