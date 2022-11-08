# -*- coding: utf-8 -*-
# Project: salt_client
# Author: jon.liu@yunzhihui.com
# Create time: 2020-12-31 14:46
# IDE: PyCharm
# Version: 1.0
# Introduction: 定义与salt交互过程中使用的某些类及方法。

"""
salt 封装的相关模块或方法
"""

import os
import logging
import traceback
import salt.client

from omp_server.settings import PROJECT_DIR

salt_master_config = os.path.join(PROJECT_DIR, "config/salt/master")

logger = logging.getLogger('server')

SALT_ERROR_MSG = "Salt 执行错误，请检查相关配置是否正确！"
AGENT_OFFLINE_MSG = "当前目标主机不在线或该目标主机未纳管！"


class SaltClient(object):
    """本地salt管理接口"""

    def __init__(self, config_path=salt_master_config):
        """
        salt管理客户端初始化操作
        :param config_path: salt-master的配置文件绝对路径
        """
        self.config_path = config_path
        # logger.info(
        #     f"Init salt client with config path: {self.config_path}!")
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
                f"Execute by salt fun_for_multi: {target}|{fun}|{arg}|{kwarg}|{timeout}")
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
            logger.info(f"Execute by salt fun_for_multi res: {cmd_res}!")
            return cmd_res
        except Exception as e:
            logger.error(
                f"Execute by salt fun_for_multi with Exception: {traceback.format_exc()}")
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
                f"Execute by salt fun: {target}|{fun}|{arg}|{kwarg}|{timeout}")
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
            logger.info(f"Execute by salt fun res: {cmd_res}!")
            if not isinstance(cmd_res, dict):
                return False, SALT_ERROR_MSG
            if target not in cmd_res:
                return False, AGENT_OFFLINE_MSG
            if target in cmd_res and cmd_res[target] is False:
                return False, "当前主机agent状态异常!"
            if 'retcode' not in cmd_res[target]:
                return False, f"当前执行未出现预期结果，详情如下: {cmd_res[target]}"
            if cmd_res[target]["retcode"] != 0:
                return False, cmd_res[target]["ret"]
            return True, cmd_res[target]["ret"]
        except Exception as e:
            logger.error(
                f"Execute by salt fun_for_multi with Exception: {traceback.format_exc()}")
            return False, f"执行{str(fun)}过程中出现错误: {str(e)}"

    def cmd(self, target, command, timeout, real_timeout=None):
        """
        执行shell命令接口
        :param target: 目标agent的id，一般为ip
        :param command: 将要执行的shell命令
        :param timeout: salt连接超时时间
        :param real_timeout: cmd命令执行超时时间
        :return: 命令执行结果
        """
        try:
            logger.info(
                f"Execute by salt cmd: {target}|{command}|{timeout}")
            cmd_res = self.client.cmd(
                tgt=target,
                fun="cmd.run",
                arg=(command,),
                timeout=timeout,
                full_return=True,
                kwarg={"timeout": real_timeout}
            )
            logger.info(f"Execute by salt cmd res: {cmd_res}")
            if not isinstance(cmd_res, dict):
                return False, SALT_ERROR_MSG
            if target not in cmd_res:
                return False, AGENT_OFFLINE_MSG
            if cmd_res[target] is False:
                return False, AGENT_OFFLINE_MSG
            if 'retcode' not in cmd_res[target]:
                return False, f"当前执行未出现预期结果，详情如下: {cmd_res[target]}"
            if cmd_res[target]["retcode"] != 0:
                return False, cmd_res[target]["ret"]
            if "Timed out after" in cmd_res[target]["ret"]:
                return False, cmd_res[target]["ret"]
            return True, cmd_res[target]["ret"]
        except Exception as e:
            logger.error(f"Execute by salt cmd with Exception: {str(e)}")
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
            logger.info(
                f"Execute by salt cp_file: {target}|{source_path}|{target_path}|{makedirs}")
            source_path = "salt://" + source_path
            cmd_res = self.client.cmd(
                tgt=target,
                fun="cp.get_file",
                arg=(source_path, target_path),
                kwarg={"makedirs": makedirs},
                timeout=60 * 10
            )
            logger.info(f"Execute by salt cp_file res: {cmd_res}")
            if not isinstance(cmd_res, dict):
                return False, SALT_ERROR_MSG
            if target not in cmd_res:
                return False, AGENT_OFFLINE_MSG
            if "PermissionError" in cmd_res[target] and "Permission denied" in cmd_res[target]:
                return False, "当前目标主机上此用户无法在目标路径下创建目录或文件！"
            if str(cmd_res[target]).startswith(target_path) or \
                    not cmd_res[target]:
                return True, cmd_res[target]
            return False, f"当前出现未知错误: {cmd_res[target]}"
        except Exception as e:
            logger.error(
                f"Execute by salt cp_file with Exception: {traceback.format_exc()}")
            return False, f"发送文件过程中出现错误: {str(e)}"

    def cp_push(self, target, source_path, upload_path):
        """
        salt-master从目标服务器拉取文件
        拉取过来的文件存放路径为：/data/omp/data/salt/var/cache/salt/master/minions/10.0.3.24/files
        :param target: 目标主机
        :param source_path: 目标主机上源文件路径，/data/backup
        :param upload_path: 目标主机上文件名
        :return:
        """
        try:
            cmd_res = self.client.cmd(
                tgt=target,
                fun="cp.push",
                arg=(source_path,),
                kwarg={"upload_path": upload_path, "remove_source": True},
                timeout=60 * 10
            )
            logger.info(f"执行拉取文件的接口，获取到的返回结果是: {cmd_res}")
            if not isinstance(cmd_res, dict):
                return False, "Salt 执行错误，请检查相关配置是否正确！"
            if target not in cmd_res:
                return False, "当前目标主机不在线或该目标主机未纳管！"
            if cmd_res[target] is True:
                return True, "success"
            return False, f"当前出现未知错误: {cmd_res[target]}"
        except Exception as e:
            print(traceback.format_exc())
            logger.error(f"拉取文件过程中程序出现错误: {traceback.format_exc()}")
            return False, f"拉取文件过程中出现错误: {str(e)}"
