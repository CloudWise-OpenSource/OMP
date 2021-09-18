# -*- coding: utf-8 -*-
# Project: update_data
# Author: jon.liu@yunzhihui.com
# Create time: 2021-09-18 10:36
# IDE: PyCharm
# Version: 1.0
# Introduction:

from django.contrib.auth.hashers import make_password
from db_models.models import UserProfile
import os
import sys

import django

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
PYTHON_PATH = os.path.join(PROJECT_DIR, "component/env/bin/python3")
MANAGE_PATH = os.path.join(PROJECT_DIR, "omp_server/manage.py")
sys.path.append(os.path.join(PROJECT_DIR, "omp_server"))

# 加载Django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "omp_server.settings")
django.setup()


def create_default_user():
    """
    创建基础用户
    :return:
    """
    username = "admin"
    password = "Common@123"
    if UserProfile.objects.filter(username=username).count() != 0:
        return
    UserProfile(
        username=username,
        password=make_password(password),
        email="admin@yunzhihui.com"
    ).save()


def main():
    """
    基础数据创建流程
    :return:
    """
    # 创建默认用户
    create_default_user()


if __name__ == '__main__':
    main()
