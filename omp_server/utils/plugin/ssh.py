"""
ssh相关操作
"""
import os
import logging

import paramiko
from scp import SCPClient

from utils.parse_config import (
    SSH_CMD_TIMEOUT, SSH_CHECK_TIMEOUT
)

logger = logging.getLogger("server")


class SSH(object):
    """ SSH 工具类 """

    def __init__(self, hostname, port, username, password, timeout=SSH_CHECK_TIMEOUT):
        """
        初始化ssh
        :param hostname: 主机名或ip地址
        :param port: 端口
        :param username: 用户名
        :param password: 密码
        :param timeout: 超时时间
        """
        logger.info(
            f"SSH init with params: {hostname}; {port}; {username}; {timeout}")
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout
        # 连接对象
        self.connect = None
        self.ssh_client = None
        self.scp_client = None
        # 错误信息
        self.is_error = None
        self.error_message = None

    def _get_connection(self):
        """ 获取连接对象 """
        if not self.connect:
            try:
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(
                    paramiko.AutoAddPolicy())
                ssh_client.connect(
                    hostname=self.hostname,
                    port=self.port,
                    username=self.username,
                    password=self.password,
                    timeout=self.timeout
                )
                scp_client = SCPClient(ssh_client.get_transport())
            except Exception as error:
                self.is_error = True
                self.error_message = error
                self.close()
                return
            self.ssh_client = ssh_client
            self.scp_client = scp_client

    def check(self):
        """
        检查SSH连接信息
        :return: is_connect, message
        """
        self._get_connection()
        if self.is_error:
            return False, str(self.error_message)
        _, stdout, _ = self.ssh_client.exec_command("whoami")
        who = stdout.readline().strip()
        if who == self.username:
            return True, "check passed"
        return False, f"stdout: {who}"

    def is_sudo(self):
        """
        检查用户是否具有sudo权限
        :return: is_sudo, message
        """
        self._get_connection()
        if self.is_error:
            return False, str(self.error_message)
        _, stdout, _ = self.ssh_client.exec_command(
            "sudo -n echo 'success'", get_pty=True)
        res = stdout.readline().strip()
        if res == "success":
            return True, "is sudo"
        return False, "not sudo"

    def cmd(self, command, timeout=SSH_CMD_TIMEOUT, get_pty=True):
        """
        执行shell命令
        :param command:
        :param timeout:
        :param get_pty:
        :return:
        """
        self._get_connection()
        if self.is_error:
            return False, str(self.error_message)
        _, stdout, stderr = self.ssh_client.exec_command(
            command, get_pty=get_pty, timeout=timeout)
        stdout.channel.recv_exit_status()
        res_stdout = stdout.readlines()
        res_stderr = stderr.readlines()
        if len(res_stderr) != 0:
            return False, res_stderr[0].strip() + " " + str(stdout)
        return True, "\n".join(res_stdout)

    def make_remote_path_exist(self, remote_path):
        """
        mkdir -p remote_path
        :param remote_path: 远程文件夹路径
        :type remote_path str
        :return:
        """
        self._get_connection()
        if self.username == "root":
            command = "test -d {0} || mkdir -p {0}".format(remote_path)
        else:
            is_sudo_flag, _ = self.is_sudo()
            if is_sudo_flag:
                command = f"sudo mkdir -p {remote_path} && " \
                          f"sudo chown -R {self.username}.{self.username} {remote_path}"
            else:
                # 普通用户仅尝试创建文件夹
                command = "test -d {0} || mkdir -p {0}".format(remote_path)
        self.cmd(command)

    def file_push(self, file, remote_path="/tmp"):
        """
        push file to remote directory use scp

        :param str file: file path
        :param str remote_path: remote directory path
        """
        file_name = os.path.basename(file)
        remote_file_full_path = os.path.join(remote_path, file_name)
        self._get_connection()
        if self.is_error:
            return False, str(self.error_message)
        try:
            self.make_remote_path_exist(remote_path)
            self.scp_client.put(file, recursive=True,
                                remote_path=remote_file_full_path)
        except Exception as error:
            import traceback
            logger.error(traceback.format_exc())
            self.close()
            return False, str(error)
        return True, "push success: {}".format(remote_file_full_path)

    def close(self):
        """ 关闭连接对象 """
        if self.ssh_client:
            self.ssh_client.close()
        if self.scp_client:
            self.scp_client.close()
