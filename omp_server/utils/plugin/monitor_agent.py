# -*- coding: utf-8 -*-
# Project: monitor_agent
# Author: jon.liu@yunzhihui.com
# Create time: 2021-10-07 13:45
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
安装、卸载、更新monitor agent
"""

import os
import logging
from concurrent.futures import ThreadPoolExecutor

from omp_server.settings import PROJECT_DIR
from utils.plugin.salt_client import SaltClient

logger = logging.getLogger("server")


class MonitorAgentManager(object):
    """ 监控Agent的管理类 """

    def __init__(self, host_objs=None):
        """
        初始化方法
        :param host_objs: 主机对象组成的列表
        """
        if not host_objs or not isinstance(host_objs, list):
            raise TypeError("host_objs must be a list of host objs!")
        self.name = "omp_monitor_agent"
        self.host_objs = host_objs
        self.package_hub_dir = os.path.join(PROJECT_DIR, "package_hub")
        self.monitor_agent_package_name = ""
        self.check_monitor_agent_package()

    def check_monitor_agent_package(self):
        """
        检查monitor agent的源码包是否存在
        :return:
        """
        # 判断monitor agent源码包文件是否存在
        for item in os.listdir(self.package_hub_dir):
            if item.startswith(self.name) and item.endswith("tar.gz"):
                self.monitor_agent_package_name = item
                break

    @staticmethod
    def execute(host_obj_lst, thread_name_prefix, func):
        """
        执行函数
        :param host_obj_lst: 主机对象组成的列表
        :param thread_name_prefix: 线程前缀
        :param func: 执行函数对象, 仅接收host主机对象参数
        :return:
        """
        thread_p = ThreadPoolExecutor(
            max_workers=20, thread_name_prefix=thread_name_prefix)
        # futures_list:[(ip, future)]
        futures_list = list()
        for item in host_obj_lst:
            future = thread_p.submit(func, item)
            futures_list.append((item.ip, future))
        # result_list:[(ip, res_bool, res_msg), ...]
        result_list = list()
        for f in futures_list:
            result_list.append((f[0], f[1].result()[0], f[1].result()[1]))
        thread_p.shutdown(wait=True)
        error_msg = ""
        for el in result_list:
            if not el[1]:
                error_msg += f"{el[0]}: (execute_flag: {el[1]}; execute_msg: {el[2]});"
        if error_msg:
            return False, error_msg
        return True, "success!"

    def _install(self, obj):
        """
        安装函数
        :param obj: 主机对象
        :type obj: Host
        :return:
        """
        # step1: 判断源码包是否存在
        if not self.monitor_agent_package_name:
            return False, "omp_monitor_agent package does not exist!"
        # step2: 发送源码包文件
        salt_obj = SaltClient()
        send_flag, send_msg = salt_obj.cp_file(
            target=obj.ip,
            source_path=self.monitor_agent_package_name,
            target_path=obj.agent_dir,
            makedirs=False)
        logger.info(
            f"Send omp_monitor_agent, "
            f"send_flag: {send_flag}; send_msg: {send_msg}")
        if not send_flag:
            return send_flag, send_msg
        # step3: 解压源码包并启动服务
        cmd_flag, cmd_res = salt_obj.cmd(
            target=obj.ip,
            command=f"cd {obj.agent_dir} && "
                    f"tar -xf {self.monitor_agent_package_name} && "
                    f"rm -rf {self.monitor_agent_package_name} && "
                    f"cd {self.name} && bash monitor_agent.sh start",
            timeout=120)
        logger.info(
            f"Install omp_monitor_agent cmd, "
            f"cmd_flag: {cmd_flag}; cmd_res: {cmd_res}")
        if not cmd_flag:
            return cmd_flag, cmd_res
        return True, "success"

    def install(self):
        """
        安装monitor agent
        :return:
        """
        return self.execute(
            host_obj_lst=self.host_objs,
            thread_name_prefix="install_",
            func=self._install)

    def _uninstall(self, obj):
        """
        卸载函数
        :param obj: 主机对象
        :type obj: Host
        :return:
        """
        salt_obj = SaltClient()
        monitor_agent_home = os.path.join(obj.agent_dir, self.name)
        cmd_flag, cmd_res = salt_obj.cmd(
            target=obj.ip,
            command=f"cd {monitor_agent_home} && "
                    f"./manage stop_all && bash monitor_agent.sh stop && "
                    f"cd {obj.agent_dir} && rm -rf {self.name}",
            timeout=120)
        logger.info(
            f"Uninstall monitor_agent, cmd_flag: {cmd_flag}; cmd_res: {cmd_res}")
        if not cmd_flag:
            return cmd_flag, cmd_res
        return True, "success"

    def uninstall(self):
        """
        卸载monitor agent
        :return:
        """
        # TODO 需要确定exporter停止脚本使用参数情况
        return self.execute(
            host_obj_lst=self.host_objs,
            thread_name_prefix="uninstall_",
            func=self._uninstall)