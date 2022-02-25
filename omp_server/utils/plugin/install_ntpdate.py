# -*- coding:utf-8 -*-
# Project: instanll_ntpdate
# Create time: 2022/2/23 1:32 下午
import os
import yaml
import logging
from utils.plugin.salt_client import SaltClient
from concurrent.futures import ThreadPoolExecutor
from omp_server.settings import PROJECT_DIR

logger = logging.getLogger("server")


class InstallNtpdate(object):
    def __init__(self, host_obj_list=None):
        if not host_obj_list or not isinstance(host_obj_list, list):
            logger.error("host_obj_list must be type of list")
            raise TypeError("host_obj_list must be type of list!")
        self.host_obj_list = host_obj_list
        self.salt_client = SaltClient()
        self.name = "ntpdate"
        self.ntpdate_package_name = ""
        self.config_path = os.path.join(PROJECT_DIR, "config/omp.yaml")
        self.package_hub_dir = os.path.join(PROJECT_DIR, "package_hub")
        self.check_ntpdate_package()

    def check_ntpdate_package(self):
        """检查ntpdate源码包是否存在"""
        for file in os.listdir(self.package_hub_dir):
            if file.startswith(self.name) and file.endswith("tar.gz"):
                self.ntpdate_package_name = file
                break

    def get_config_dic(self):
        """
        获取配置文件详细信息
        :return:
        """
        with open(self.config_path, "r", encoding="utf8") as fp:
            return yaml.load(fp, Loader=yaml.FullLoader)

    def get_run_user(self):
        """获取run_user"""
        return self.get_config_dic().get("global_user")

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
                error_msg += \
                    f"{el[0]}: (execute_flag: {el[1]}; execute_msg: {el[2]});"
        if error_msg:
            return False, error_msg
        return True, "success!"

    def _install_ntpdate(self, host_obj):
        """安装ntpdate"""
        if not self.ntpdate_package_name:
            logger.error("ntpdate_package not existed!")
            return False, "ntpdate_package not existed!"
        host_obj.ntpdate_install_status = 2
        host_obj.save()
        agent_dir = host_obj.agent_dir
        app_dir = os.path.join(agent_dir, "app")
        data_dir = os.path.join(agent_dir, "appData")
        log_dir = os.path.join(agent_dir, "logs")
        ntpdate_cron_path = os.path.join(app_dir, f"{self.name}/scripts/{self.name}_cron.sh")
        scripts_path = os.path.join(app_dir, f"{self.name}/scripts/{self.name}")
        # 1.发包
        send_flag, send_msg = self.salt_client.cp_file(
            target=host_obj.ip,
            source_path=self.ntpdate_package_name,
            target_path=app_dir,
            makedirs=True
        )
        logger.info(
            f"send ntpdate packages,send_flag: {send_flag}; send_msg: {send_msg}"
        )
        if not send_flag:
            return send_flag, send_msg
        # 2.解压缩与安装、启动
        cmd_flag, cmd_msg = self.salt_client.cmd(
            target=host_obj.ip,
            command=f"cd {app_dir} &&"
                    f" tar -xf {self.ntpdate_package_name} &&"
                    f" rm -rf {self.ntpdate_package_name} &&"
                    f"(test -d {app_dir}|| mkdir -p {app_dir})&&"
                    f"(test -d {data_dir}|| mkdir -p {data_dir})&&"
                    f"(test -d {log_dir}|| mkdir -p {log_dir})&&"
                    f"sed -i -e \"s#\${{CW_INSTALL_APP_DIR}}#{app_dir}#g\" -e 's#\${{CW_NTP_ADDRESS}}#{host_obj.ntpd_server}#g' {ntpdate_cron_path} &&"
                    f"sed -i -e 's#\${{CW_INSTALL_APP_DIR}}#{app_dir}#g' -e 's#\${{CW_INSTALL_LOGS_DIR}}#{log_dir}#g' -e 's#\${{CW_INSTALL_DATA_DIR}}#{data_dir}#g' -e's#\${{CW_RUN_USER}}#{self.get_run_user()}#g' {scripts_path};"
                    f"bash {scripts_path} start",
            timeout=120
        )
        logger.info(f"install ntpdate cmd, cmd_flag: {cmd_flag};cmd_msg: {cmd_msg}")
        if not cmd_flag:
            host_obj.ntpdate_install_status = 3
            host_obj.save()
            return cmd_flag, cmd_msg
        host_obj.ntpdate_install_status = 0
        host_obj.save()
        return True, "success"

    def install(self):
        return self.execute(host_obj_lst=self.host_obj_list, thread_name_prefix="install_", func=self._install_ntpdate)
