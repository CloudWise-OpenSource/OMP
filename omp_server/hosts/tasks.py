# -*- coding: utf-8 -*-
# Project: tasks
# Author: jon.liu@yunzhihui.com
# Create time: 2021-09-12 11:54
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
主机相关异步任务
"""

import os
import time
import logging
import traceback
import subprocess
import requests
import json

from django.conf import settings
from celery import shared_task
from celery.utils.log import get_task_logger
from promemonitor.alertmanager import Alertmanager
from promemonitor.prometheus_utils import PrometheusUtils

from db_models.models import (
    Host, Service,
    HostOperateLog,
    Alert
)
from utils.plugin.ssh import SSH
from utils.plugin.monitor_agent import MonitorAgentManager
from utils.plugin.crypto import AESCryptor
from utils.plugin.agent_util import Agent
from app_store.tasks import add_prometheus
from utils.parse_config import HOSTNAME_PREFIX
from utils.plugin.install_ntpdate import InstallNtpdate
from omp_server.settings import PROJECT_DIR
from concurrent.futures import ThreadPoolExecutor

# 屏蔽celery任务日志中的paramiko日志
logging.getLogger("paramiko").setLevel(logging.WARNING)
logger = get_task_logger("celery_log")


def deploy_monitor_agent(host_obj, salt_flag=True):
    """
    部署监控Agent
    :param host_obj: 主机对象
    :param salt_flag: 部署主机Agent成功或失败标志
    :return:
    """
    logger.info(f"Deploy monitor agent for {host_obj.ip}")
    if not salt_flag:
        Host.objects.filter(ip=host_obj.ip).update(
            monitor_agent=4,
            monitor_agent_error="主机salt-agent部署失败!"
        )
        logger.error(
            "Deploy monitor agent failed because salt agent deploy failed")
        return
    monitor_manager = MonitorAgentManager(host_objs=[host_obj])
    install_flag, install_msg = monitor_manager.install()
    logger.info(
        f"Deploy monitor agent, "
        f"install_flag: {install_flag}; install_msg: {install_msg}")
    if not install_flag:
        Host.objects.filter(ip=host_obj.ip).update(
            monitor_agent=4,
            monitor_agent_error=install_msg if len(
                install_msg) < 200 else install_flag[:200]
        )
    else:
        Host.objects.filter(ip=host_obj.ip).update(monitor_agent=0)


def real_deploy_agent(host_obj, need_monitor=True):
    """
    部署主机Agent
    :param host_obj: 主机对象
    :type host_obj Host
    :param need_monitor: 是否部署monitor
    :type need_monitor bool
    :return:
    """
    logger.info(
        f"Deploy Agent for {host_obj.ip}, Params: "
        f"username: {host_obj.username}; "
        f"port: {host_obj.port}; "
        f"install_dir: {host_obj.agent_dir}!")
    _obj = Agent(
        host=host_obj.ip,
        port=host_obj.port,
        username=host_obj.username,
        password=AESCryptor().decode(host_obj.password),
        install_dir=host_obj.agent_dir
    )
    flag, message = _obj.agent_deploy()
    logger.info(
        f"Deploy Agent for {host_obj.ip}, "
        f"Res Flag: {flag}; Res Message: {message}")
    # 更新主机Agent状态，0 正常；4 部署失败
    # 使用filter查询然后使用update方法进行处理，防止多任务环境
    if flag:
        Host.objects.filter(ip=host_obj.ip).update(host_agent=0)
    else:
        Host.objects.filter(ip=host_obj.ip).update(
            host_agent=4,
            host_agent_error=str(message)[:200] if len(
                str(message)) > 200 else str(message)
        )
    # 部署监控agent
    if need_monitor:
        deploy_monitor_agent(host_obj=host_obj, salt_flag=flag)


@shared_task
def deploy_agent(host_id, need_monitor=True):
    """
    部署主机Agent
    :param host_id:
    :param need_monitor: 是否部署monitor
    :type need_monitor bool
    :return:
    """
    try:
        # edit by vum:
        # obj.save 在异步任务并发读写下存在数值覆盖问题
        host_query = Host.objects.filter(id=host_id)
        host_query.update(host_agent=3)
        real_deploy_agent(
            host_obj=host_query.first(),
            need_monitor=need_monitor
        )
    except Exception as e:
        logger.error(
            f"Deploy Host Agent For {host_id} Failed with error: {str(e)};\n"
            f"detail: {traceback.format_exc()}"
        )
        Host.objects.filter(id=host_id).update(
            host_agent=4, host_agent_error=str(e))


def real_host_agent_restart(host_obj):
    """
    重启主机Agent
    :param host_obj: 主机对象
    :type host_obj Host
    :return:
    """
    logger.info(
        f"Restart Agent for {host_obj.ip}, Params: "
        f"username: {host_obj.username}; "
        f"port: {host_obj.port}; "
        f"install_dir: {host_obj.agent_dir}!")
    _obj = SSH(
        hostname=host_obj.ip,
        port=host_obj.port,
        username=host_obj.username,
        password=AESCryptor().decode(host_obj.password),
    )
    _script_path = os.path.join(
        host_obj.agent_dir, "omp_salt_agent/bin/omp_salt_agent")
    flag, message = _obj.cmd(f"bash {_script_path} restart")
    logger.info(
        f"Restart host agent for {host_obj.ip}: "
        f"get flag: {flag}; get res: {message}")
    # 使用filter查询然后使用update方法进行处理，防止多任务环境
    if flag:
        # host_obj.host_agent = 0
        Host.objects.filter(ip=host_obj.ip).update(host_agent=0)
    else:
        # host_obj.host_agent = 2
        # host_obj.host_agent_error = \
        #     str(message)[:200] if len(str(message)) > 200 else str(message)
        Host.objects.filter(ip=host_obj.ip).update(
            host_agent=2,
            host_agent_error=str(message)[:200] if len(
                str(message)) > 200 else str(message)
        )


@shared_task
def host_agent_restart(host_id):
    """
    主机Agent的重启操作
    :param host_id: 主机的id
    :return:
    """
    try:
        host_obj = Host.objects.get(id=host_id)
        real_host_agent_restart(host_obj=host_obj)
    except Exception as e:
        logger.error(
            f"Restart Host Agent For {host_id} Failed with error: {str(e)};\n"
            f"detail: {traceback.format_exc()}"
        )
        Host.objects.filter(id=host_id).update(
            host_agent=2, host_agent_error=str(e))


def real_init_host(host_obj):
    """
    初始化主机
    :param host_obj: 主机对象
    :type host_obj Host
    :return:
    """
    logger.info(f"init host Begin [{host_obj.id}]")
    _ssh = SSH(
        hostname=host_obj.ip,
        port=host_obj.port,
        username=host_obj.username,
        password=AESCryptor().decode(host_obj.password),
    )
    # 验证用户权限
    is_sudo, _ = _ssh.is_sudo()
    if not is_sudo:
        logger.error(f"init host [{host_obj.id}] failed: permission failed")
        raise Exception("permission failed")

    # 发送脚本
    init_script_name = "init_host.py"
    init_script_path = os.path.join(
        settings.BASE_DIR.parent,
        "package_hub", "_modules", init_script_name)
    script_push_state, script_push_msg = _ssh.file_push(
        file=init_script_path,
        remote_path="/tmp",
    )
    if not script_push_state:
        logger.error(f"init host [{host_obj.id}] failed: send script failed, "
                     f"detail: {script_push_msg}")
        raise Exception("send script failed")
    modified_host_name = str(HOSTNAME_PREFIX) + "".join(
        item.zfill(3) for item in host_obj.ip.split("."))
    # 执行初始化
    is_success, script_msg = _ssh.cmd(
        f"python /tmp/{init_script_name} init_valid {modified_host_name} {host_obj.ip}")
    if not (is_success and "init success" in script_msg and "valid success" in script_msg):
        logger.error(f"init host [{host_obj.id}] failed: execute init failed, "
                     f"detail: {script_push_msg}")
        raise Exception("execute failed")
    Host.objects.filter(
        id=host_obj.id
    ).update(init_status=Host.INIT_SUCCESS)
    logger.info("init host Success")


@shared_task
def init_host(host_id):
    """ 初始化主机 """
    try:
        # edit by vum:
        # obj.save 在异步任务并发读写下存在数值覆盖问题
        host_query = Host.objects.filter(id=host_id)
        host_query.update(init_status=Host.INIT_EXECUTING)
        real_init_host(host_obj=host_query.first())
    except Exception as e:
        print(e)
        logger.error(
            f"Init Host For {host_id} Failed with error: {str(e)};\n"
            f"detail: {traceback.format_exc()}"
        )
        Host.objects.filter(id=host_id).update(
            init_status=Host.INIT_FAILED)


@shared_task
def insert_host_celery_task(host_id, init=False):
    """ 添加主机 celery 任务 """
    # 执行主机初始化
    if init:
        try:
            num = 0
            host_obj = Host.objects.filter(id=host_id).first()
            while host_obj is None and num < 10:
                host_obj = Host.objects.filter(id=host_id).first()
                time.sleep(2)
                num += 1
            if host_obj is None:
                raise Exception("Host Object not found")
            # edit by vum:
            # obj.save 在异步任务并发读写下存在数值覆盖问题
            host_query = Host.objects.filter(id=host_id)
            host_query.update(init_status=Host.INIT_EXECUTING)
            real_init_host(host_obj=host_query.first())
        except Exception as e:
            print(e)
            logger.error(
                f"Init Host For {host_id} Failed with error: {str(e)};\n"
                f"detail: {traceback.format_exc()}"
            )
            Host.objects.filter(id=host_id).update(
                init_status=Host.INIT_FAILED)
    # 部署 agent
    try:
        num = 0
        host_obj = Host.objects.filter(id=host_id).first()
        while host_obj is None and num < 10:
            host_obj = Host.objects.filter(id=host_id).first()
            time.sleep(2)
            num += 1
        if host_obj is None:
            raise Exception("Host Object not found")
        host_query = Host.objects.filter(id=host_id)
        host_query.update(host_agent=Host.AGENT_DEPLOY_ING)
        real_deploy_agent(host_obj=host_query.first())
    except Exception as e:
        logger.error(
            f"Deploy Host Agent For {host_id} Failed with error: {str(e)};\n"
            f"detail: {traceback.format_exc()}"
        )
        Host.objects.filter(id=host_id).update(
            host_agent=Host.AGENT_DEPLOY_ERROR,
            host_agent_error=str(e))
    # 部署ntpdate
    try:
        host_obj = Host.objects.filter(id=host_id).first()
        host_id = host_obj.id
        if host_obj.use_ntpd:
            InstallNtpdate(host_obj_list=[host_obj]).install()
    except Exception as e:
        logger.error(
            f"Deplot ntpdate for {id} Failed with error: {str(e)};\n"
            f"detail: {traceback.format_exc()}"
        )
        Host.objects.filter(id=host_id).update(
            ntpdate_install_status=Host.NTPDATE_INSTALL_FAILED)


def write_host_log(host_queryset, status, result, username):
    """ 写入主机日志 """
    log_ls = []
    for host in host_queryset:
        log_ls.append(HostOperateLog(
            username=username,
            description=f"{status}[维护模式]",
            result=result,
            host=host))
    HostOperateLog.objects.bulk_create(log_ls)


def maintenance(host_obj, entry, username):
    """ 进入 / 退出维护模式 """
    # 根据 is_maintenance 判断主机进入 / 退出维护模式
    status = "开启" if entry else "关闭"
    en_status = "open" if entry else "close"
    alert_manager = Alertmanager()
    host_ls = [{"ip": host_obj.ip}]
    if entry:
        res_ls = alert_manager.set_maintain_by_host_list(host_ls)
    else:
        res_ls = alert_manager.revoke_maintain_by_host_list(host_ls)
    # 操作失败
    if not res_ls:
        logger.error(f"host {en_status} maintain failed: {host_obj.ip}")
        # 操作失败记录写入
        write_host_log([host_obj], status, "failed", username)
    Host.objects.filter(
        id=host_obj.id
    ).update(is_maintenance=entry)
    logger.info(f"host {en_status} maintain success: {host_obj.ip}")
    # 操作成功记录写入
    write_host_log([host_obj], status, "success", username)


@shared_task
def reinstall_monitor_celery_task(host_id, username):
    """ 重新安装主机监控 celery 任务 """
    host_obj = Host.objects.filter(id=host_id).first()
    maintenance(host_obj, True, username)
    logger.info(
        f"Restart Agent for {host_obj.ip}, Params: "
        f"username: {host_obj.username}; "
        f"port: {host_obj.port}; "
        f"install_dir: {host_obj.agent_dir}!")
    _obj = SSH(
        hostname=host_obj.ip,
        port=host_obj.port,
        username=host_obj.username,
        password=AESCryptor().decode(host_obj.password),
    )
    flag, message = _obj.cmd(
        "ps -ef | grep omp_monitor_agent | grep -v grep | awk -F ' ' '{print $2}' | xargs kill -9")
    logger.info(
        f"Stop monitor agent for {host_obj.ip}: "
        f"get flag: {flag}; get res: {message}")
    # 删除目录，防止agent_dir异常保护系统
    if host_obj.agent_dir:
        monitor_dir = os.path.join(host_obj.agent_dir, "omp_monitor_agent")
        flag, message = _obj.cmd(f"/bin/rm -rf {monitor_dir}")
    logger.info(
        f"Stop monitor agent for {host_obj.ip}: "
        f"get flag: {flag}; get res: {message}")
    deploy_monitor_agent(host_obj=host_obj, salt_flag=flag)
    host_obj.refresh_from_db()
    if host_obj.monitor_agent == 4:
        maintenance(host_obj, False, username)
        return
    # 刷新prometheus服务列表监控配置,优化功能
    service_obj_list = Service.objects.filter(ip=host_obj.ip)
    detail_obj_list = []
    for service_obj in service_obj_list:
        detail_obj = service_obj.detailinstallhistory_set.first()
        if detail_obj:
            detail_obj_list.append(detail_obj)
    if len(detail_obj_list) != 0:
        add_prometheus(9999, detail_obj_list)
    maintenance(host_obj, False, username)


class UninstallHosts(object):
    def __init__(self, all_host):
        self.is_success = True
        self.all_host = all_host

    @staticmethod
    def cmd(command):
        """执行本地shell命令"""
        p = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )
        stdout, stderr = p.communicate()
        _out, _err, _code = stdout.decode(
            "utf8"), stderr.decode("utf8"), p.returncode
        return _out, _err, _code

    def delete_salt_key(self, key_list):
        """删除所有的salt-key"""
        python_path = os.path.join(PROJECT_DIR, 'component/env/bin/python3')
        salt_key_path = os.path.join(PROJECT_DIR, "component/env/bin/salt-key")
        salt_config_path = os.path.join(PROJECT_DIR, "config/salt")
        for item in key_list:
            _out, _err, _code = self.cmd(
                f"{python_path} {salt_key_path} -y -d '{item}' -c {salt_config_path}"
            )
            if _code != 0:
                print(f"删除{item}获取到stdout: {_out}; stderr: {_err}")
                self.is_success = False
            logger.info(f"删除{item}获取到哦的stdout: {_out}; stderr: {_err}")

    @staticmethod
    def del_single_agent(obj):
        """
        删除单个节点的agent（salt and monitor）
        """
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
        delete_cmd_str = f"rm -rf {data_dir}/omp_packages; " \
                         f"/bin/rm -rf {data_dir}/app/bash_profile; /bin/rm -rf /tmp/upgrade_openssl"
        cmd_res, msg = _ssh_obj.cmd(
            delete_cmd_str,
            timeout=120
        )
        logger.info(f"执行{ip} [delete] package and tmp 操作 {cmd_res}, 原因: {msg}")

        # 卸载salt agent
        salt_agent_dir = os.path.join(agent_dir, "omp_salt_agent")
        _delete_cron_cmd = "crontab -l|grep -v omp_salt_agent 2>/dev/null | crontab -;"
        _stop_agent = (
            f"bash {salt_agent_dir}/bin/omp_salt_agent stop; /bin/rm -rf {salt_agent_dir}"
        )
        final_cmd = f"{_delete_cron_cmd} {_stop_agent}"
        salt_res_flag, salt_res_msg = _ssh_obj.cmd(final_cmd, timeout=60)
        logger.info(f"卸载{ip}上的omp_salt_agent的命令为: {final_cmd}")
        logger.info(
            f"卸载{ip}上的omp_salt_agent的结果为: {salt_res_flag} {salt_res_msg}")
        # 卸载monitor agent
        monitor_agent_dir = os.path.join(agent_dir, "omp_monitor_agent")
        _delete_monitor_cron_cmd = "crontab -l|grep -v omp_monitor_agent " \
                                   "2>/dev/null | crontab -;"
        _uninstall_monitor_agent_cmd = f"cd {monitor_agent_dir} &&" \
                                       f" ./manage stop_all &&" \
                                       f" bash monitor_agent.sh stop &&" \
                                       f" cd {agent_dir} &&" \
                                       f" /bin/rm -rf omp_monitor_agent"
        monitor_res_flag, monitor_res_msg = _ssh_obj.cmd(
            _uninstall_monitor_agent_cmd, timeout=120)
        res, msg = _ssh_obj.cmd(
            _delete_monitor_cron_cmd, timeout=120)

        cmd_ntpd_uninstall = "/bin/rm -rf {0}/app/ntpdate &&" \
                             "crontab -l| grep -v {0}/app/ntpdate 2>/dev/null" \
                             " | crontab -;".format(data_dir)
        if obj.username != "root":
            cmd_ntpd_uninstall = "sudo /bin/rm -rf {0}/app/ntpdate &&" \
                                 "sudo crontab -l| grep -v {0}/app/ntpdate 2>/dev/null" \
                                 " | sudo crontab -;".format(data_dir)
        ntpd_res, ntpd_msg = _ssh_obj.cmd(
            cmd_ntpd_uninstall, timeout=120)
        logger.info(
            f"卸载{ip}上的ntpd的结果为: {ntpd_res} {ntpd_msg}")
        logger.info(
            f"卸载{ip}上的omp_monitor_agent的命令为: {_uninstall_monitor_agent_cmd}")
        logger.info(
            f"卸载{ip}上的omp_monitor_agent的结果为: {monitor_res_flag} {monitor_res_msg}")
        if not all([cmd_res, salt_res_flag, monitor_res_flag]):
            return False, f"({ip}上卸载文件清除：{cmd_res}-{msg};\n salt:{salt_res_flag}-{salt_res_msg};\n monitor:{monitor_res_flag}-{monitor_res_msg};\n)"
        return True, "success"

    @staticmethod
    def execute_uninstall(host_obj_list, thread_name_prefix, function, max_num=8):
        """卸载执行函数"""
        thread_p = ThreadPoolExecutor(
            max_workers=max_num,
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
                                                                 function=self.del_single_agent)
        ips = self.all_host.values_list("ip", flat=True)
        pro_obj = PrometheusUtils()
        write_str = []
        node_path = os.path.join(
            pro_obj.prometheus_targets_path, "nodeExporter_all.json")
        for node in pro_obj.get_dic_from_yaml(node_path):
            if node.get("targets", [""])[0].split(":")[0] in ips:
                continue
            write_str.append(node)
        with open(node_path, "w") as f2:
            json.dump(write_str, f2, ensure_ascii=False, indent=4)
        time.sleep(2)
        reload_prometheus_url = "http://localhost:19011/-/reload"
        requests.post(reload_prometheus_url,
                      auth=pro_obj.basic_auth)

        if not _uninstall_flag:
            print(_uninstall_msg)
            self.is_success = False
        self.delete_salt_key([item.ip for item in self.all_host])
        return self.is_success


@shared_task()
def delete_hosts(host_ids):
    """
    执行删除异步任务
    """
    host_objs = Host.objects.filter(ip__in=host_ids)
    uninstall_objs = UninstallHosts(host_objs)
    uninstall_objs.delete_all_omp_agent()
    host_objs.delete()
    Service.objects.filter(ip__in=host_ids).delete()
    Alert.objects.filter(alert_host_ip__in=host_ids).delete()
