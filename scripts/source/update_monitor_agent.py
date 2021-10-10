# -*- coding: utf-8 -*-
# Project: update_monitor_agent
# Author: jon.liu@yunzhihui.com
# Create time: 2021-10-09 18:39
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
更新监控Agent使用的方法
"""

import os
import sys
import shutil

import django

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
sys.path.append(os.path.join(PROJECT_DIR, "omp_server"))
PACKAGE_HUB = os.path.join(PROJECT_DIR, "package_hub")
UPDATE_HOME = os.environ.get("OMP_UPDATE_HOME_PATH", "")
if not UPDATE_HOME:
    UPDATE_HOME = os.path.join(os.path.dirname(PROJECT_DIR), "omp_update")

# 加载Django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "omp_server.settings")
django.setup()

from db_models.models import Host
from utils.plugin.public_utils import get_file_md5
from utils.plugin.monitor_agent import MonitorAgentManager


def make_backups(pack_md5):
    """
    备份监控Agent文件
    :param pack_md5: md5值
    :return:
    """
    old_pack_path = ""
    for item in os.listdir(PACKAGE_HUB):
        if item.startswith("omp_monitor_agent") and item.endswith("tar.gz"):
            old_pack_path = os.path.join(PACKAGE_HUB, item)
    if not old_pack_path:
        return
    backup_path = os.path.join(UPDATE_HOME, pack_md5)
    if not os.path.exists(backup_path):
        os.makedirs(backup_path)
    shutil.copyfile(
        old_pack_path,
        os.path.join(backup_path, os.path.basename(old_pack_path))
    )
    os.remove(old_pack_path)


def update(pack_path, pack_md5):
    """
    更新监控Agent
    :param pack_path: 新包的路径
    :param pack_md5: 新包的md5值
    :return:
    """
    # step1: 备份原文件
    make_backups(pack_md5=pack_md5)
    # step2: 复制新文件到目标路径
    shutil.copyfile(
        pack_path,
        os.path.join(PACKAGE_HUB, os.path.basename(pack_path))
    )
    # step3: 查询所有主机，更新监控Agent
    host_obj_lst = Host.objects.all()
    if not host_obj_lst.exists():
        return
    # 利用封装好的方法先卸载，再安装
    agent_manager = MonitorAgentManager(host_objs=list(host_obj_lst))
    agent_manager.uninstall()
    install_flag, install_message = agent_manager.install()
    print(
        f"Update new omp_monitor_agent: "
        f"install_flag: {install_flag}; install_message: {install_message}")


def main(pack_path=None, pack_md5=None):
    """
    更新主流程方法
    :param pack_path: 安装包路径
    :param pack_md5: 安装包md5值
    :return:
    """
    update(pack_path, pack_md5)
    # TODO 如果有服务的配置可能需要有额外的更新操作！！


if __name__ == '__main__':
    sys_args = sys.argv[1:]
    if len(sys_args) != 1:
        print("Please use: python update_monitor_agent.py package_path")
    package_path = sys_args[0]
    if not os.path.exists(package_path):
        print("{0} Package Not Exist!".format(package_path))
        exit(1)
    flag, package_md5 = get_file_md5(package_path)
    main(pack_path=package_path, pack_md5=package_md5)
