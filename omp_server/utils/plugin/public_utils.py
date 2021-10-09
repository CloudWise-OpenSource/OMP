# -*- coding: utf-8 -*-
# Project: public_utils
# Author: jon.liu@yunzhihui.com
# Create time: 2021-10-09 19:55
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
文件md5值处理模块
"""

import os
import hashlib


def get_file_md5(file_path):
    """
    获取文件的md5值
    :param file_path: 文件路径
    :return:
    """
    if not os.path.exists(file_path):
        return False, "File not exists!"
    m = hashlib.md5()
    with open(file_path, 'rb') as f_obj:
        while True:
            data = f_obj.read(4096)
            if not data:
                break
            m.update(data)
    return True, m.hexdigest()
