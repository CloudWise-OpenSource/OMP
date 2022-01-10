# -*- coding: utf-8 -*-
# Project: cmd_install_entrance
# Author: jon.liu@yunzhihui.com
# Create time: 2022-01-07 15:16
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
通过命令行安装应用、产品的主体逻辑
"""

import os
import sys
import json
import datetime
import argparse
import time

import django

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
sys.path.append(os.path.join(PROJECT_DIR, "omp_server"))

# 加载Django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "omp_server.settings")
django.setup()

from rest_framework.test import APIClient

from db_models.models import UserProfile
from db_models.models import MainInstallHistory
from db_models.models import DetailInstallHistory
from app_store.cmd_install_utils import ReadDeploymentExcel

HOST_AGENT_WAIT_TIME = 60 * 10
INFO_FRESH_SECOND = 5


class DjangoClient(object):
    """ 模拟请求到Django的客户端 """

    def __init__(self):
        """ 初始化 """
        user = UserProfile.objects.filter(username="admin").last()
        self.client = APIClient()
        self.client.force_authenticate(user)

    def get(self, url, data=None):
        """
        通过client发送get请求
        :param url: 请求url
        :param data: 请求参数
        :return:
        """
        return self.client.get(url, data=data).json()

    def post(self, url, data):
        """
        通过client发送post请求
        :param url: 请求url
        :param data: 请求数据
        :return:
        """
        res = self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json"
        ).json()
        return res


class MainProcess(object):
    """ 命令行主体安装执行类 """

    def __init__(self, excel_path):
        self.excel_path = excel_path
        self.operation_uuid = None
        self.host = list()
        self.service = dict()
        self.client = DjangoClient()

    @staticmethod
    def print_log(msg, error=False):
        """
        打印输出日志，后续会结合log进行操作
        :param msg:
        :param error: 是否为错误信息，打印时增加颜色显示
        :return:
        """
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if error:
            print(f"\033[0;31;47m{now} {msg}\033[0m")
        else:
            print(f"{now} {msg}")

    def step_1(self):
        """
        解析excel数据
        :return:
        """
        _flag, _data = ReadDeploymentExcel(
            excel_path=self.excel_path
        ).read_excel()
        if not _flag:
            return False, _data
        self.host = _data["host"]
        self.service = _data["service"]
        return True, "成功解析表格数据"

    def step_2(self):
        """
        调用主机校验接口
        :return:
        """
        data = {"host_list": self.host}
        res = self.client.post(url="/api/hosts/batchValidate/", data=data)
        if res.get("code") != 0:
            return False, res.get("message")
        error_lst = res.get("data", {}).get("error", [])
        if not error_lst:
            return True, "success"
        for item in error_lst:
            self.print_log(
                f"主机 [{item.get('ip')}] 校验失败 [{item.get('validate_error')}]",
                error=True
            )
        return False, "主机数据存在异常, 请查看上述错误信息进行排查后重试"

    def step_3(self):
        """
        调用服务分布校验接口
        :return:
        """
        res = self.client.post(
            url="/api/appStore/deploymentPlanValidate/",
            data=self.service
        )
        if res.get("code") != 0:
            return False, res.get("message")
        error_lst = res.get("data", {}).get("error", [])
        if not error_lst:
            return True, "success"
        for item in error_lst:
            self.print_log(
                f"服务分布信息校验失败 [{item.get('validate_error')}]",
                error=True
            )
        return False, "服务分布信息校验失败, 请查看上述错误信息进行排查后重试"

    def step_4(self):
        """
        调用主机批量添加接口
        :return:
        """
        data = {"host_list": self.host}
        res = self.client.post(url="/api/hosts/batchImport/", data=data)
        if res.get("code") != 0:
            return False, res.get("message")
        return True, "批量添加主机成功"

    def step_5(self):
        """
        调用服务入库接口
        :return:
        """
        instance_info_ls = list()
        for item in self.host:
            instance_info_ls.append({
                "instance_name": item.get("instance_name"),
                "run_user": item.get("run_user")
            })
        data = {
            "instance_info_ls": instance_info_ls,
            "service_data_ls": self.service.get("service_data_ls")
        }
        res = self.client.post(
            url="/api/appStore/deploymentPlanImport/",
            data=data
        )
        if res.get("code") != 0:
            return False, res.get("message")
        self.operation_uuid = res.get("data", {}).get("operation_uuid")
        return True, "服务分布信息入库成功"

    def step_6(self):
        """
        调用Agent状态监控接口
        :return:
        """
        data = {"ip_list": [el["ip"] for el in self.host]}
        step_count = 0
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        while True:
            step_count += 1
            _msg = "." * step_count
            if step_count == 1:
                print(f"{now} 等待Agent安装成功{_msg}", end="", flush=True)
            else:
                print(".", end="", flush=True)
            res = self.client.post(
                url="/api/hosts/hostsAgentStatus/",
                data=data
            )
            if res.get("code") != 0:
                return False, res.get("message")
            agent_status = res.get("data")
            if agent_status is False:
                time.sleep(INFO_FRESH_SECOND)
                continue
            break
        print()
        if agent_status is True:
            return True, "主机Agent状态已恢复正常"
        return False, f"主机Agent状态经{HOST_AGENT_WAIT_TIME}s后仍处于不可用状态"

    def step_7(self):
        """
        调用安装部署执行接口
        :return:
        """
        data = {"unique_key": self.operation_uuid}
        res = self.client.post(
            url="/api/appStore/retryInstall/",
            data=data
        )
        if res.get("code") != 0:
            return False, res.get("message")
        return True, "执行安装操作成功"

    def step_8(self):
        """
        调用安装进度显示接口
        :return:
        """
        status_dic = self.get_service_install_status()
        status_map = {
            DetailInstallHistory.INSTALL_STATUS_READY: "待安装",
            DetailInstallHistory.INSTALL_STATUS_INSTALLING: "安装中",
            DetailInstallHistory.INSTALL_STATUS_SUCCESS: "安装成功",
            DetailInstallHistory.INSTALL_STATUS_FAILED: "安装失败",
        }
        break_flag = False
        continue_flag = True
        # 第一次获取状态，并输出状态
        for key, value in status_dic.items():
            if value == DetailInstallHistory.INSTALL_STATUS_FAILED:
                self.check_failed_status(key)
                break_flag = True
            else:
                self.print_log(f"{key} 当前状态为: {status_map[value]}")

        while continue_flag:
            time.sleep(INFO_FRESH_SECOND)
            _status_dic = self.get_service_install_status()
            for key, value in _status_dic.items():
                if status_dic[key] == value:
                    continue
                if value == DetailInstallHistory.INSTALL_STATUS_FAILED:
                    self.check_failed_status(key)
                    break_flag = True
                else:
                    self.print_log(
                        f"{key} 当前状态为: {status_map[value]}"
                    )
            status_dic = _status_dic
            if all(
                    value == DetailInstallHistory.INSTALL_STATUS_SUCCESS
                    for value in status_dic.values()
            ):
                self.print_log("***** 所有服务安装成功 *****")
                break
            if break_flag and not MainInstallHistory.objects.filter(
                operation_uuid=self.operation_uuid,
                install_status=MainInstallHistory.INSTALL_STATUS_INSTALLING
            ).exists():
                continue_flag = False
        if break_flag:
            self.print_log("安装失败, 请查看上述报错信息")
            return False, "安装过程出现问题，请查看上述报错信息"
        return True, "安装进度显示成功"

    def check_failed_status(self, service_instance_name):
        """
        检查安装错误的服务的信息
        :param service_instance_name: 服务实例名称
        :return:
        """
        detail_obj = DetailInstallHistory.objects.filter(
            main_install_history__operation_uuid=self.operation_uuid,
            service__service_instance_name=service_instance_name
        ).first()
        self.print_log(
            f"{service_instance_name} 当前状态为: 安装失败, 详情如下:",
            error=True
        )
        error_msg = \
            detail_obj.send_msg + \
            detail_obj.unzip_msg + \
            detail_obj.install_msg + \
            detail_obj.init_msg + \
            detail_obj.start_msg
        self.print_log(error_msg, error=True)

    def get_service_install_status(self):
        """
        获取服务的安装状态
        :return:
        """
        queryset = DetailInstallHistory.objects.filter(
            main_install_history__operation_uuid=self.operation_uuid
        ).values("install_step_status", "service__service_instance_name")
        status_dic = {
            el["service__service_instance_name"]:
                el["install_step_status"] for el in queryset
        }
        return status_dic

    def run(self):
        """
        安装主体程序运行入口
        :return:
        """
        step_map_dic = {
            "step_1": "解析excel数据",
            "step_2": "调用主机校验接口",
            "step_3": "调用服务分布校验接口",
            "step_4": "调用主机批量添加接口",
            "step_5": "调用服务入库接口",
            "step_6": "调用Agent状态监控接口",
            "step_7": "调用安装部署执行接口",
            "step_8": "调用安装进度显示接口"
        }
        self.print_log("开始进入安装流程")
        for i in range(1, 20):
            if not hasattr(self, f"step_{i}"):
                break
            step_pre_msg = step_map_dic[f"step_{i}"]
            self.print_log(f"开始执行[{step_pre_msg}]")
            flag, msg = getattr(self, f"step_{i}")()
            if not flag:
                self.print_log(
                    f"[{step_pre_msg}]执行失败, 原因为: {msg}", error=True)
                self.print_log("安装失败, 程序结束!")
                sys.exit(1)
            self.print_log(f"[{step_pre_msg}]执行成功")
        self.print_log("安装成功, 程序结束!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--excel_path", "-data_json",
        required=False, help="excel文件位置",
        default=os.path.join(os.path.dirname(PROJECT_DIR), "deployment.xlsx")
    )
    param = parser.parse_args()
    excel_path_arg = param.excel_path
    MainProcess(excel_path=excel_path_arg).run()
