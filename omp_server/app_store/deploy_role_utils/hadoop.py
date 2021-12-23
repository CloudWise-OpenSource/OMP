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
        need_distribution = [
            "namenode,zkfc", "resourcemanager", "namenode,zkfc", "resourcemanager"]
        base_role = "datanode,nodemanager,journalnode"
        # worker_role = "datanode,nodemanager" 后期优化分配
        if len(service_list) == 1:
            service_list[0]['roles'] = "journalnode,namenode,secondarynamenode," \
                                       "datanode,resourcemanager,nodemanager"
            return service_list
        for index, i in enumerate(service_list):
            if i.get('roles'):
                continue
            if index == len(service_list) - 1 and len(need_distribution) > 1:
                i['roles'] = "{0},{1}".format(
                    base_role, ",".join(need_distribution))
            elif index == 0 and len(service_list) == 2:
                i['roles'] = "{0},{1}".format(
                    base_role, ",".join(need_distribution[:2]))
                need_distribution = need_distribution[2:]
            elif len(service_list) >= 5 and need_distribution[0] == "namenode,zkfc":
                role = need_distribution.pop(0)
                i['roles'] = f"journalnode,{role}"
            else:
                role = need_distribution.pop(0)
                i['roles'] = f"{base_role},{role}"
        return service_list
