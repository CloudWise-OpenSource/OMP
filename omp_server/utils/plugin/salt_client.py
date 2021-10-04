# -*- coding: utf-8 -*-
# Project: salt_client
# Author: jon.liu@yunzhihui.com
# Create time: 2020-12-31 14:46
# IDE: PyCharm
# Version: 1.0
# Introduction: 定义与salt交互过程中使用的某些类及方法。

import os
import logging
import traceback
import salt.client

from omp_server.settings import PROJECT_DIR

salt_master_config = os.path.join(PROJECT_DIR, "config/salt/master")

logger = logging.getLogger('server')


class SaltClient(object):
    """本地salt管理接口"""

    def __init__(self, config_path=salt_master_config):
        """
        salt管理客户端初始化操作
        :param config_path: salt-master的配置文件绝对路径
        """
        self.config_path = config_path
        logger.info(f"根据配置文件路径: {self.config_path} 初始化salt客户端")
        self.client = salt.client.LocalClient(
            c_path=self.config_path, auto_reconnect=True)

    def salt_module_update(self):
        """
        用于更新salt的自定义模块
        :return:
        """
        try:
            cmd_res = self.client.cmd(
                tgt="*",
                fun="saltutil.sync_modules",
            )
            """
            # {'192.168.175.149': {'ret': [], 'retcode': 0, 'jid': '20210113213356939481'}, 'ruban-dev': False}
            # {'192.168.175.149': [], 'ruban-dev': False}
            """
            ret_dic = dict()
            for key, value in cmd_res.items():
                if isinstance(value, dict) and value.get("retcode", 1000) == 0:
                    ret_dic.update({key: True})
                elif isinstance(value, list):
                    ret_dic.update({key: True})
                else:
                    ret_dic.update({key: False})
            return True, ret_dic
        except Exception as e:
            return False, f"在同步salt模块的过程中出错: {str(e)}"

    def fun_for_multi(self, target, fun, arg=(), kwarg=None, timeout=None, tgt_type="glob"):
        """
        可自行执行模块的命令，适用于批量执行操作，需要自行判断函数执行结果
        :param target: 目标主机
        :param fun: 执行模块，如cmd.run
        :param arg: 位置参数信息
        :param kwarg: 关键字参数信息
        :param timeout: 超时时间
        :param tgt_type: 匹配target的格式，glob正则匹配 or list匹配
        :return: 返回的执行结果
        """
        try:
            logger.info(
                f"通过salt执行function: {target}|{fun}|{arg}|{kwarg}|{timeout}")
            if kwarg is None:
                kwarg = {}
            cmd_res = self.client.cmd(
                tgt=target,
                fun=fun,
                arg=arg,
                kwarg=kwarg,
                tgt_type=tgt_type,
                timeout=timeout,
                full_return=True
            )
            logger.debug(f"salt fun执行结束获取到的结果为: {cmd_res}!")
            return cmd_res
        except Exception as e:
            logger.error(f"通过salt执行模块报错: {traceback.format_exc()}")
            return False, f"执行{str(fun)}过程中出现错误: {str(e)}"

    def fun(self, target, fun, arg=(), kwarg=None, timeout=None):
        """
        可自行执行模块的命令，适用于单个主机的部分模块
        :param target: 目标主机
        :param fun: 执行模块，如cmd.run
        :param arg: 位置参数信息
        :param kwarg: 关键字参数信息
        :param timeout: 超时时间
        :return: 返回的执行结果
        """
        try:
            logger.info(
                f"通过salt执行function: {target}|{fun}|{arg}|{kwarg}|{timeout}")
            if kwarg is None:
                kwarg = {}
            cmd_res = self.client.cmd(
                tgt=target,
                fun=fun,
                arg=arg,
                kwarg=kwarg,
                timeout=timeout,
                full_return=True
            )
            # logger.info(f"salt fun执行结束获取到的结果为: {cmd_res}!")
            if not isinstance(cmd_res, dict):
                return False, "Salt 执行错误，请检查相关配置是否正确！"
            if target not in cmd_res:
                return False, "当前目标主机不在线或该目标主机未纳管！"
            if target in cmd_res and cmd_res[target] is False:
                return False, "当前主机agent状态异常!"
            if 'retcode' not in cmd_res[target]:
                return False, f"当前执行未出现预期结果，详情如下: {cmd_res[target]}"
            if cmd_res[target]["retcode"] != 0:
                return False, cmd_res[target]["ret"]
            return True, cmd_res[target]["ret"]
        except Exception as e:
            logger.error(f"通过salt执行模块报错: {traceback.format_exc()}")
            return False, f"执行{str(fun)}过程中出现错误: {str(e)}"

    def cmd(self, target, command, timeout):
        """
        执行shell命令接口
        :param target: 目标agent的id，一般为ip
        :param command: 将要执行的shell命令
        :param timeout: 超时时间
        :return: 命令执行结果
        """
        try:
            cmd_res = self.client.cmd(
                tgt=target,
                fun="cmd.run",
                arg=(command,),
                timeout=timeout,
                full_return=True
            )
            if not isinstance(cmd_res, dict):
                return False, "Salt 执行错误，请检查相关配置是否正确！"
            if target not in cmd_res:
                return False, "当前目标主机不在线或该目标主机未纳管！"
            if 'retcode' not in cmd_res[target]:
                return False, f"当前执行未出现预期结果，详情如下: {cmd_res[target]}"
            if cmd_res[target]["retcode"] != 0:
                return False, cmd_res[target]["ret"]
            return True, cmd_res[target]["ret"]
        except Exception as e:
            return False, f"执行命令的过程中出现错误: {str(e)}"

    def cp_file(self, target, source_path, target_path, makedirs=True):
        """
        salt-master发送文件到目标服务器
        :param target: 目标主机
        :param source_path: 源文件路径，salt://
        :param target_path: 目标主机上存放路径
        :param makedirs: 当文件夹不存在时，是否在目标主机上创建文件夹
        :return:
        """
        try:
            source_path = "salt://" + source_path
            cmd_res = self.client.cmd(
                tgt=target,
                fun="cp.get_file",
                arg=(source_path, target_path),
                kwarg={"makedirs": makedirs},
                timeout=60 * 10
            )
            logger.info(f"执行发送文件的接口，获取到的返回结果是: {cmd_res}")
            if not isinstance(cmd_res, dict):
                return False, "Salt 执行错误，请检查相关配置是否正确！"
            if target not in cmd_res:
                return False, "当前目标主机不在线或该目标主机未纳管！"
            if "PermissionError" in cmd_res[target] and "Permission denied" in cmd_res[target]:
                return False, "当前目标主机上此用户无法在目标路径下创建目录或文件！"
            if str(cmd_res[target]).startswith(target_path):
                return True, cmd_res[target]
            return False, f"当前出现未知错误: {cmd_res[target]}"
        except Exception as e:
            logger.error(f"发送文件过程中程序出现错误: {traceback.format_exc()}")
            return False, f"发送文件过程中出现错误: {str(e)}"
