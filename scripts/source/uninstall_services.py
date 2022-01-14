# -*- coding:utf-8 -*-
# Project: uninstall_services
# Author:Times.niu@yunzhihui.com
# Create time: 2022/1/7 2:37 下午

import os
import sys
import django
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
PYTHON_PATH = os.path.join(PROJECT_DIR, 'component/env/bin/python3')
SALT_KEY_PATH = os.path.join(PROJECT_DIR, "component/env/bin/salt-key")
SALT_CONFIG_PATH = os.path.join(PROJECT_DIR, "config/salt")
sys.path.append(os.path.join(PROJECT_DIR, 'omp_server'))
MAX_NUM = 8

# 加载django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "omp_server.settings")
django.setup()

import logging
from db_models.models import (Service, ApplicationHub, Host, HostOperateLog, PreInstallHistory, DetailInstallHistory,
                              PostInstallHistory, MainInstallHistory, Alert)
from utils.parse_config import BASIC_ORDER
from services.tasks import exec_action as uninstall_exec_action
from utils.plugin.salt_client import SaltClient
from utils.plugin.ssh import SSH
from utils.plugin.crypto import AESCryptor

logger = logging.getLogger("server")


class UninstallServices(object):
    def __init__(self, env_id):
        self.env_id = env_id
        self.salt_obj = SaltClient()
        self.is_success = True
        self.all_host = Host.objects.filter(env_id=self.env_id)
        self.service_num = Service.objects.filter(env_id=self.env_id).count()

    @staticmethod
    def cmd(command):
        """执行本地shell命令"""
        p = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )
        stdout, stderr = p.communicate()
        _out, _err, _code = stdout.decode("utf8"), stderr.decode("utf8"), p.returncode
        return _out, _err, _code

    def delete_salt_key(self, key_list):
        """删除所有的salt-key"""
        for item in key_list:
            _out, _err, _code = self.cmd(
                f"{PYTHON_PATH} {SALT_KEY_PATH} -y -d '{item}' -c {SALT_CONFIG_PATH}"
            )
            if _code != 0:
                print(f"删除{item}获取到stdout: {_out}; stderr: {_err}")
                self.is_success = False
            logger.info(f"删除{item}获取到哦的stdout: {_out}; stderr: {_err}")

    def get_all_services(self):
        """通过环境名找到所有的服务"""
        services = Service.objects.filter(env_id=self.env_id)
        if not services:
            return []
        return services

    def del_singel_agent(self, obj):
        """删除单个节点的agent（salt and monitor）"""
        ip = obj.ip
        agent_dir = obj.agent_dir
        data_dir = obj.data_folder
        _ssh_obj = SSH(
            hostname=ip,
            port=obj.port,
            username=obj.username,
            password=AESCryptor().decode(obj.password)
        )
        # 删除目录
        if not data_dir:
            raise Exception(f"主机{ip}无数据目录")
        # TODO /app/bash_profile目前是指定目录
        delete_cmd_str = f"rm -rf {data_dir}/omp_packages; rm -rf {data_dir}/app/bash_profile; rm -rf /tmp/upgrade_openssl; rm -rf /tmp/hadoop"
        cmd_res, msg = _ssh_obj.cmd(
            delete_cmd_str,
            timeout=120
        )
        logger.info(f"执行{ip} [delete] package and tmp 操作 {cmd_res}, 原因: {msg}")

        # 卸载salt agent
        salt_agent_dir = os.path.join(agent_dir, "omp_salt_agent")
        _delete_cron_cmd = "crontab -l|grep -v omp_salt_agent 2>/dev/null | crontab -;"
        _stop_agent = (
            f"bash {salt_agent_dir}/bin/omp_salt_agent stop; rm -rf {salt_agent_dir}"
        )
        final_cmd = f"{_delete_cron_cmd} {_stop_agent}"
        salt_res_flag, salt_res_msg = _ssh_obj.cmd(final_cmd, timeout=60)
        logger.info(f"卸载{ip}上的omp_salt_agent的命令为: {final_cmd}")
        logger.info(f"卸载{ip}上的omp_salt_agent的结果为: {salt_res_flag} {salt_res_msg}")
        # 卸载monitor agent
        monitor_agent_dir = os.path.join(agent_dir, "omp_monitor_agent")
        _uninstall_monitor_agent_cmd = f"cd {monitor_agent_dir} &&" \
                                       f" ./manage stop_all &&" \
                                       f" bash monitor_agent.sh stop &&" \
                                       f" cd {agent_dir} &&" \
                                       f" rm -rf omp_monitor_agent"
        monitor_res_flag, monitor_res_msg = _ssh_obj.cmd(_uninstall_monitor_agent_cmd, timeout=120)
        logger.info(f"卸载{ip}上的omp_monitor_agent的命令为: {_uninstall_monitor_agent_cmd}")
        logger.info(f"卸载{ip}上的omp_monitor_agent的结果为: {monitor_res_flag} {monitor_res_msg}")
        if not all([cmd_res, salt_res_flag, monitor_res_flag]):
            return False, f"({ip}上卸载文件清除：{cmd_res}-{msg};\n salt:{salt_res_flag}-{salt_res_msg};\n monitor:{monitor_res_flag}-{monitor_res_msg};\n)"
        return True, "success"

    @staticmethod
    def execute_uninstall(host_obj_list, thread_name_prefix, function):
        """卸载执行函数"""
        thread_p = ThreadPoolExecutor(
            max_workers=MAX_NUM,
            thread_name_prefix=thread_name_prefix
        )
        # future_list: [(ip, future),..]
        future_list = list()
        # result_list:[(ip, res_bool, res_msg), ...]
        result_list = list()
        for obj in host_obj_list:
            future = thread_p.submit(function, obj)
            future_list.append((obj.ip, future))
        for f in future_list:
            result_list.append((f[0], f[1].result()[0], f[1].result()[1]))
        thread_p.shutdown(wait=True)
        failed_msg = ""
        for item in result_list:
            if not item[1]:
                failed_msg += f"{item[0]}: (execute_flag: {item[1]}; execute_msg: {item[2]})"
        if failed_msg:
            return False, failed_msg
        return True, "success"

    def delete_all_omp_agent(self):
        """清理所有omp agent(salt and monitor)"""
        _uninstall_flag, _uninstall_msg = self.execute_uninstall(host_obj_list=self.all_host,
                                                                 thread_name_prefix="uninstall_agent_",
                                                                 function=self.del_singel_agent)

        if not _uninstall_flag:
            print(_uninstall_msg)
            self.is_success = False
        self.delete_salt_key([item.ip for item in self.all_host])

    def get_uninstall_order(self, service_list):
        """卸载服务排序（与安装顺序相反）"""
        uninstall_list = list()

        # 过滤出自研服务
        self_service = [
            item for item in service_list
            if item.service.app_type == ApplicationHub.APP_TYPE_SERVICE
        ]
        # level不为0 自研服务
        uninstall_list.append(
            [
                item for item in self_service
                if str(item.service.extend_fields.get('level')) != "0"
            ]
        )
        # level为0 自研服务
        uninstall_list.append(
            [
                item for item in self_service
                if str(item.service.extend_fields.get('level')) == "0"
            ]
        )
        # 基础组件
        basic_lists = list()
        for m in range(10):
            if m not in BASIC_ORDER:
                break
            basic_list = [
                item for item in service_list
                if item.service.app_name in BASIC_ORDER[m]
            ]
            basic_lists.append(basic_list)
        basic_lists.reverse()
        uninstall_list.extend(basic_lists)
        return uninstall_list

    def uninstall_service(self, item_list):
        """调用卸载函数执行卸载"""
        ids_uninstall_list = [item.id for item in item_list]
        for id in ids_uninstall_list:
            uninstall_exec_action.delay(action="4", instance=id, operation_user="command_line", del_file=True)

    def uninstall_all_services(self, uninstall_list):
        """卸载所有的服务"""
        for item_list in uninstall_list:
            if not item_list:
                continue
            self.uninstall_service(item_list)

    def clean_db(self):
        """清理数据库"""
        HostOperateLog.objects.all().delete()
        self.all_host.delete()
        PreInstallHistory.objects.all().delete()
        DetailInstallHistory.objects.all().delete()
        PostInstallHistory.objects.all().delete()
        MainInstallHistory.objects.all().delete()
        # TODO Alert.objects.filter(env_id=self.env_id).delete()
        Alert.objects.all().delete()

    def run(self):
        """卸载的总控制函数"""
        service_list = self.get_all_services()
        uninstall_list = self.get_uninstall_order(service_list=service_list)
        self.uninstall_all_services(uninstall_list=uninstall_list)
        time.sleep(int(self.service_num))
        self.delete_all_omp_agent()
        self.clean_db()
        if not self.is_success:
            raise Exception("本次卸载失败，请按照上述打印信息手动进行卸载")


if __name__ == '__main__':
    env_id = 1
    UninstallServices(env_id).run()
