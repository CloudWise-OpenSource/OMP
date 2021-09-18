import paramiko
from scp import SCPClient


class SSH:
    """ SSH 工具类 """

    def __init__(self, hostname, port, username, password, timeout=10):
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
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
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
        else:
            return False, f"stdout: {who}"

    def close(self):
        """ 关闭连接对象 """
        if self.ssh_client:
            self.ssh_client.close()
        if self.scp_client:
            self.scp_client.close()
