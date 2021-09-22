# -*- coding: utf-8 -*-
# Project: agent_util
# Author: jon.liu@yunzhihui.com
# Create time: 2021-05-10 20:13
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
安装主机Agent的方法
"""

import os
import logging

import yaml

from utils.plugin.ssh import SSH
from omp_server.settings import PROJECT_DIR
from utils.parse_config import LOCAL_IP
from utils.parse_config import SALT_RET_PORT

logger = logging.getLogger("server")


class Agent(object):
    """agent安装管理"""

    def __init__(self, host, port, username, password, install_dir):
        """
        agent管理需要的初始化文件
        :param host: 主机ip
        :param port: 主机端口
        :param username: 主机用户名
        :param password: 主机密码
        :param install_dir: 安装路径
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.run_user = username
        self.master_ip = LOCAL_IP
        self.master_port = SALT_RET_PORT
        self.install_dir = install_dir
        self.agent_name = "omp_salt_agent"
        self.package_hub = os.path.join(PROJECT_DIR, "package_hub")
        self.agent_file_path = os.path.join(
            self.package_hub, "omp_salt_agent.tar.gz")
        self.ssh = SSH(
            hostname=self.host,
            port=int(self.port),
            username=self.username,
            password=self.password
        )

    def generate_conf(self):
        """
        生成agent的配置文件
        :return:
        """
        try:
            agent_conf_dic = {
                "master": self.master_ip,
                "master_port": self.master_port,
                "user": self.run_user,
                "id": self.host,
                "root_dir": os.path.join(self.install_dir, f"{self.agent_name}/data/"),
                "conf_file": os.path.join(self.install_dir, f"{self.agent_name}/conf/minion"),
                "rejected_retry": True
            }
            with open(os.path.join(self.package_hub, self.host, "minion"), "w") as fp:
                yaml.dump(agent_conf_dic, fp, Dumper=yaml.SafeDumper)
            return True, "generate success."
        except Exception as error:
            return False, str(error)

    def agent_deploy(self):
        """
        安装agent
        :return:
        """
        # step1: 判断是否可连接
        ssh_state, _ = self.ssh.check()
        if not ssh_state:
            return False, "ssh connect failed"

        # 删除原有omp_salt_agent
        omp_salt = os.path.join(self.install_dir, "omp_salt_agent")
        _delete_cron_cmd = f"sed -i '/omp_salt_agent/d' /var/spool/cron/{self.username}; "
        # OMP-v1.3.0 防止误删除，不删除这个文件夹
        # _stop_agent = f"bash {omp_salt}/bin/omp_salt_agent stop; rm -rf {omp_salt}"
        _stop_agent = f"bash {omp_salt}/bin/omp_salt_agent stop; rm -rf {omp_salt}/data/*"
        final_cmd = f"{_delete_cron_cmd} {_stop_agent}"
        self.ssh.cmd(final_cmd, timeout=60)

        # step2: push agent.tar.gz to remote host and install
        tar_push_state, tar_push_msg = self.ssh.file_push(
            self.agent_file_path, self.install_dir)
        if not tar_push_state:
            logger.error(
                f"file push to {self.host} with error: {tar_push_msg}")
            return False, tar_push_msg

        # step3: install agent
        command = "cd {0} && tar xf {1}.tar.gz && chown -R {2}:{2} {1} && rm -f {1}.tar.gz".format(
            self.install_dir, self.agent_name, self.run_user)
        cmd_exec_state, cmd_exec_msg = self.ssh.cmd(command)
        if not cmd_exec_state:
            logger.error(
                f"Error while install agent for {self.host}: {cmd_exec_msg}")
            return False, cmd_exec_msg

        # step4: make package_hub/host_ip/
        config_tmp_dir = os.path.join(self.package_hub, self.host)
        if not os.path.isdir(config_tmp_dir):
            os.makedirs(config_tmp_dir)
        config_tmp = os.path.join(config_tmp_dir, 'minion')
        config_gen_state, config_gen_msg = self.generate_conf()
        if not config_gen_state:
            logger.error(
                f"Error while generate conf file for agent {self.host}: {config_gen_msg}")
            return False, config_gen_msg

        # step5: push config file to remote host
        config_push_state, config_push_msg = self.ssh.file_push(
            config_tmp,
            os.path.join(self.install_dir, f'{self.agent_name}/conf/')
        )
        if not config_push_state:
            logger.error(
                f"Error while send agent config to {self.host}: {config_push_msg}")
            return False, config_push_msg

        # step6: make and push scripts
        with open(os.path.join(PROJECT_DIR, "scripts/source/omp_salt_agent"), "r") as fp:
            _script_content = fp.read()
        with open(os.path.join(config_tmp_dir, "omp_salt_agent"), "w") as fp:
            _content = _script_content.replace(
                "UNIQUE_INSTALL_DIR_FLAG", self.install_dir)
            # OMP-v1.3.0 解决root安装时出现的权限问题
            _content = _content.replace("RUNUSER", self.run_user)
            fp.write(_content)
        script_push_state, script_push_msg = self.ssh.file_push(
            os.path.join(config_tmp_dir, "omp_salt_agent"),
            os.path.join(self.install_dir, '{}/bin/'.format(self.agent_name))
        )
        if not script_push_state:
            logger.error(
                f"Error while send agent script for {self.host}: {script_push_msg}")
            return False, script_push_msg
        # shutil.rmtree(config_tmp_dir)

        # step7: start and init agent
        # OMP-v1.3.0 增加agent文件夹整体赋权问题
        command = f"cd {self.install_dir} && " \
                  f"chown -R {self.run_user}.{self.run_user} {self.agent_name} && " \
                  f"bash {self.agent_name}/bin/{self.agent_name} init"
        cmd_exec_state, cmd_exec_msg = self.ssh.cmd(command, timeout=120)
        if not cmd_exec_state:
            if "INIT_OMP_SALT_AGENT_SUCCESS" in cmd_exec_msg:
                return True, "agent deploy success"
            logger.error(
                f"Error while start agent for {self.host}: {cmd_exec_msg}")
            return False, cmd_exec_msg
        return True, "agent deploy success."

    def agent_manage(self, action, install_app_dir):
        """
        manage salt agent, start stop status

        :param str action: [start|stop|status]
        :param str install_app_dir:  e.g. /data/app

        :return:
            the (state, status) , as a 2-tuple
        """
        if action == "start":
            command = "cd {}/{} && bash ./bin/omp_salt_agent start".format(
                install_app_dir, self.agent_name)
        elif action == "stop":
            command = "cd {}/{} && bash ./bin/omp_salt_agent stop".format(
                install_app_dir, self.agent_name)
        elif action == "status":
            command = "cd {}/{} && bash ./bin/omp_salt_agent status".format(
                install_app_dir, self.agent_name)
        else:
            return False, "start|stop|status"
        cmd_exec_state, cmd_exec_msg = self.ssh.cmd(command)
        if cmd_exec_state:
            return True, cmd_exec_msg[0].strip()
        else:
            return False, cmd_exec_msg


if __name__ == '__main__':
    # test_agent = Agent(
    #     host="10.0.7.146",
    #     port=36000,
    #     username="root",
    #     password="yunzhihui123",
    #     run_user="root",
    #     install_dir="/data/app"
    # )
    # flag, message = test_agent.agent_deploy()
    # print(flag, message)
    pass
