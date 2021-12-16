# -*- coding: utf-8 -*-
# Project: __init__.py
# Author: jerry.zhang@yunzhihui.com
# Create time: 2021-12-16 10:10
# IDE: PyCharm
# Version: 1.0
# Introduction:

import logging

logger = logging.getLogger("server")


class Hadoop(object):
    @staticmethod
    def update_service(service_list):
        """
        分配hadoop服务角色
        :param service_list: 服务数据列表
        :return:
        """
        need_distribution = ["namenode", "namenode", "resourcemanager"]
        base_role = "datanode,nodemanager,journalnode"
        if len(service_list) == 1:
            service_list[0]['roles'] = "journalnode,namenode,DFSZKFailoverController," \
                "datanode,resourcemanager,nodemanager"
            return service_list
        for index, i in enumerate(service_list):
            if index == len(service_list) - 1 and len(need_distribution) > 1:
                i['roles'] = "{},{}".format(
                    base_role, ",".join(need_distribution))
            else:
                role = need_distribution.pop()
                i['roles'] = "{},{}".format(base_role, role)
        return service_list
