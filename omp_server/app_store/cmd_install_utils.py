# -*- coding: utf-8 -*-
# Project: cmd_install_utils
# Author: jon.liu@yunzhihui.com
# Create time: 2022-01-07 15:10
# IDE: PyCharm
# Version: 1.0
# Introduction:

import os

import xlrd


class ReadDeploymentExcel(object):
    """ 读取部署表格使用类 """

    def __init__(self, excel_path):
        """
        :param excel_path: 表格文件绝对路径
        """
        self.excel_path = excel_path

    @staticmethod
    def _read(start_row=1, keys=None, table=None):
        """
        真正读取表格数据，返回tuple (True, list) or (False, str)
        :param start_row:
        :param keys:
        :param table:
        :return:
        """
        # 获取总行数 总列数
        row_num = table.nrows
        col_num = table.ncols

        _res = []
        # 这是第一行数据，作为字典的key值
        key = table.row_values(0)

        if row_num <= start_row:
            return False, "所需要数据行数下无数据"
        # 读取行数的控制逻辑
        for i in range(row_num - 1):
            # 行数据字典
            row_data = {}
            # 如果当前获取到的数据的行数小于想要的行数时，则跳过，不留存
            if i < start_row:
                continue
            values = table.row_values(i + 1)
            # 循环每列获取数据
            for x in range(col_num):
                _key = None
                if key[x] not in keys:
                    continue
                _key = keys[key[x]]
                # 提取真正的值
                value = int(values[x]) if isinstance(values[x], float) \
                    else values[x]
                row_data[_key] = str(value).strip()
                row_data["row"] = i + 1
            if not row_data:
                continue
            # 把字典加到列表中
            _res.append(row_data)
        return _res

    def read_host_info(self, table):
        """
        获取节点信息
        :param table: 节点信息页对象
        :return:
        """
        keys_map = {
            "实例名[必填]": "instance_name",
            "IP[必填]": "ip",
            "端口[必填]": "port",
            "用户名[必填]": "username",
            "密码[必填]": "password",
            "数据分区[必填]": "data_folder",
            "操作系统[必填]": "operate_system",
            "是否执行初始化": "init_host",
            "运行用户": "run_user",
            "时间同步服务器": "ntpd_server"
        }
        return self._read(start_row=4, keys=keys_map, table=table)

    def read_service_info(self, table):
        """
        获取服务分布表格信息
        :param table: 服务分布页对象
        :return:
        """
        keys_map = {
            "主机实例名[必填]": "instance_name",
            "服务名[必填]": "service_name",
            "运行内存": "memory",
            "虚拟IP": "vip",
            "角色": "role",
            "模式": "mode"
        }
        return self._read(start_row=3, keys=keys_map, table=table)

    def read_excel(self):
        """
        读取表格数据
        :return:
        """
        if not os.path.exists(self.excel_path) or \
                not os.path.isfile(self.excel_path):
            return False, f"无法找到此文件: {self.excel_path}"
        # 打开excel表，填写路径
        book = xlrd.open_workbook(self.excel_path)
        # 找到sheet页
        host_table = book.sheet_by_name("节点信息")
        host_info = self.read_host_info(table=host_table)
        for item in host_info:
            if "init_host" in item and item["init_host"] == "是":
                item["init_host"] = True
            else:
                item["init_host"] = False
            if "ntpd_server" in item and item["ntpd_server"] != "":
                item["use_ntpd"] = True
            else:
                item["use_ntpd"] = False
                item.pop("ntpd_server", "")
        service_table = book.sheet_by_name("服务分布")
        service_info = self.read_service_info(table=service_table)
        return True, {
            "host": host_info,
            "service": {
                "instance_name_ls": [el["instance_name"] for el in host_info],
                "service_data_ls": service_info
            }
        }
