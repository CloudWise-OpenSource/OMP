# -*- coding: utf-8 -*-
# Project: mysql
# Author: jon.liu@yunzhihui.com
# Create time: 2021-12-21 20:22
# IDE: PyCharm
# Version: 1.0
# Introduction:


import logging

logger = logging.getLogger("server")


class Mysql(object):
    @staticmethod
    def update_service(service_list):
        """
        分配mysql的角色
        :param service_list: 服务数据列表
        :return:
        """
        mysql_index_lst = list()
        mysql_vip_flag = False
        for index, item in enumerate(service_list):
            logger.info(f"{mysql_vip_flag}; {item}")
            if item.get("name") == "mysql":
                mysql_index_lst.append(index)
            if item.get("roles") == "mysql":
                mysql_vip_flag = True
        if len(mysql_index_lst) == 1:
            service_list[mysql_index_lst[0]]["roles"] = "single"
        elif len(mysql_index_lst) == 2:
            if not mysql_vip_flag:
                service_list[mysql_index_lst[0]]["roles"] = "master"
                service_list[mysql_index_lst[1]]["roles"] = "slave"
            else:
                service_list[mysql_index_lst[0]]["roles"] = "master"
                service_list[mysql_index_lst[1]]["roles"] = "master"
        return service_list
