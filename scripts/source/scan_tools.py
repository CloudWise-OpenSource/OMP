# -*- coding:utf-8 -*-
import os
import sys

import django


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
sys.path.append(os.path.join(PROJECT_DIR, 'omp_server'))
# 加载django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "omp_server.settings")
django.setup()


from tool.find_tools import find_tools_package


if __name__ == '__main__':
    result = find_tools_package()
    if result:
        print("扫描小工具完成！")
        sys.exit(0)
    print("扫描小工具完成,部分工具包校验失败，详细请查看logs/debug.log！")
    sys.exit(1)
