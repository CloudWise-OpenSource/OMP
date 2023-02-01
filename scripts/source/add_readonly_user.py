# -*- coding:utf-8 -*-
# Project: add_readonly_user
# Create time: 2023/1/10 3:36 下午

import django
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
PYTHON_PATH = os.path.join(PROJECT_DIR, "component/env/bin/python3")
sys.path.append(os.path.join(PROJECT_DIR, "omp_server"))

# 加载Django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "omp_server.settings")
django.setup()

from db_models.models import UserProfile


def add_read_only_user():
    """增加只读用户"""
    read_only_username = "omp"
    read_only_password = "Yunweiguanli@OMP_123"
    if UserProfile.objects.filter(username=read_only_username).count() == 0:
        UserProfile.objects.create_user(
            username=read_only_username,
            password=read_only_password,
            email="omp@cloudwise.com",
            role="ReadOnlyUser"
        )
    admin_user = UserProfile.objects.get(username="admin")
    admin_user.role = "SuperUser"
    admin_user.save()


if __name__ == '__main__':
    add_read_only_user()
