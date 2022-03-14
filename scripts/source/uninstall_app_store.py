# -*- coding:utf-8 -*-
# Project: uninstall_app_store
# Author:Jerry.zhang@yunzhihui.com
# Create time: 2022/3/13 11:23 上午

import os
import sys
import time

import django
import subprocess
import argparse

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
PACKAGE_DIR = os.path.join(PROJECT_DIR, "package_hub")
PYTHON_PATH = os.path.join(PROJECT_DIR, 'component/env/bin/python3')
SALT_KEY_PATH = os.path.join(PROJECT_DIR, "component/env/bin/salt-key")
SALT_CONFIG_PATH = os.path.join(PROJECT_DIR, "config/salt")
sys.path.append(os.path.join(PROJECT_DIR, 'omp_server'))
MAX_NUM = 8

# 加载django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "omp_server.settings")
django.setup()

import logging
from db_models.models import (ApplicationHub, ProductHub, Service)


class UninstallServices(object):
    def __init__(self, app_name=None, product=None, version=None):
        self.app_name = app_name
        self.version = version
        self.product = product
        self._app_obj = None
        self.product_all = False
        self.del_dir = set()

    def check_database(self):
        """
        支持服务开头匹配,服务版本开头匹配，但不支持产品开头匹配，测试中产品暂时不存在多版本情况
        """
        if not self.app_name and not self.product:
            print("请输入卸载产品名或服务名称")
            sys.exit(1)

        # 服务存在，产品不存在，当产品为基础组建时则认为正常
        if self.app_name and not self.product:
            app_obj = ApplicationHub.objects.filter(app_name__startswith=self.app_name)
            if app_obj and 1 not in app_obj.values_list("app_type", flat=True):
                self._app_obj = app_obj
            else:
                print("存在服务为产品，请输入服务名对应的产品名")
                sys.exit(1)
        # 产品存在 服务不存在
        if not self.app_name and self.product:
            self._app_obj = ApplicationHub.objects.filter(product__pro_name=self.product)
            self.product_all = True
        # 产品服务均存在
        if self.app_name and self.product:
            app_obj = ApplicationHub.objects.filter(app_name__startswith=self.app_name,
                                                    product__pro_name=self.product)
            if not app_obj:
                print(f"{self.product}产品下无此服务")
                sys.exit(1)
            self._app_obj = app_obj
        # 版本筛选
        if self.version and self._app_obj:
            self._app_obj = self._app_obj.filter(app_version__startswith=self.version)
        # 检查是否存在已安装的应用
        have_app = False
        for obj in self._app_obj:
            if obj.service_set.count() != 0:
                have_app = True
        return have_app

    def sys_cmd(self, cmd, ignore_exception=True):
        """
        shell脚本输出
        :param cmd: linux命令
        :param ignore_exception: 默认不抛出异常
        :return:
        """
        shell = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = shell.communicate()
        stdout, stderr = bytes.decode(stdout), bytes.decode(stderr)
        if ignore_exception:
            print(stderr)
            return stdout
        if not ignore_exception:
            if shell.poll() != 0:
                print("执行cmd命令失败，执行cmd命令:{0},结果退出码:{1},执行详情:{2}".format(cmd, shell.poll(), stderr))
                sys.exit(shell.poll())
            else:
                print(stdout)
        else:
            return stdout

    def delete_database(self):
        try:
            for obj in self._app_obj:
                upload_obj = obj.app_package
                if self.product_all:
                    self.del_dir.add(os.path.join(PACKAGE_DIR, upload_obj.package_path))
                    pro_obj = ProductHub.objects.filter(pro_name=self.product).first()
                    ApplicationHub.objects.filter(product=pro_obj).delete()
                    pro_obj.delete()
                    break
                else:
                    self.del_dir.add(os.path.join(PACKAGE_DIR, upload_obj.package_path, upload_obj.package_name))
                    obj.delete()
            if not self._app_obj and self.product and not self.app_name:
                pro_obj = ProductHub.objects.filter(pro_name=self.product).first()
                if pro_obj:
                    self.del_dir.add(os.path.join(PACKAGE_DIR, "verified", f"{pro_obj.pro_name}-{pro_obj.pro_version}"))
                    pro_obj.delete()

        except Exception as e:
            print(f"数据库异常:{e}")
            sys.exit(1)

    def delete_file(self):
        need_dir = " ".join(self.del_dir)
        if need_dir and len(need_dir) > 28:
            self.sys_cmd(f"/bin/rm -rf {need_dir}", ignore_exception=False)


def parameters():
    """
    传递参数
    :return: 脚本接收到的参数
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--app_name", "-app_name",
                        help="开头匹配的服务名称")
    parser.add_argument("--product", "-product", help="完全匹配的产品名")
    parser.add_argument("--version", "-version", help="开头匹配的服务名")
    param = parser.parse_args()
    return param


if __name__ == '__main__':
    para = parameters()
    uninstall_obj = UninstallServices(app_name=para.app_name,
                                      product=para.product,
                                      version=para.version
                                      )
    result = uninstall_obj.check_database()
    if result:
        print("应用商店的服务存在已安装实例，是否确认删除 yes or no")
        result = input()
        if result not in ["yes", "no"]:
            print("请输入正确的参数")
            sys.exit(1)
    if result != "no":
        uninstall_obj.delete_database()
        time.sleep(5)
        uninstall_obj.delete_file()
        print("删除完成")
