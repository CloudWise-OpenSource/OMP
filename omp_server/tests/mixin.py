"""
单元测试混入类
"""
import random
from db_models.models import (Host, Env)
from utils.plugin.crypto import AESCryptor


class HostsResourceMixin:
    """ 创建主机资源混入类 """

    INSTANCE_NAME_START = "t_host"
    IP_START = "127"

    def get_hosts(self, number, env_id=None):
        """
        获取主机
        :param number: 创建主机数量
        :param env_id: 环境实例
        """
        # 获取环境信息
        env = None
        if env_id:
            env = Env.objects.filter(id=env_id).first()
        if not env:
            env = Env.objects.filter(id=1).first()
        # 创建主机
        aes_crypto = AESCryptor()
        host_obj_ls = []
        for index in range(number):
            index += 1
            host_obj = Host.objects.create(
                instance_name=f"{self.INSTANCE_NAME_START}_{index}",
                ip=f"{self.IP_START}.0.0.{index}",
                port=36000,
                username=f"root{index}",
                password=aes_crypto.encode(f"password_{index}"),
                data_folder="/data",
                operate_system="CentOS",
                env=env,
            )
            host_obj_ls.append(host_obj)
        return host_obj_ls

    def destroy_hosts(self):
        """ 销毁主机 """
        Host.objects.filter(
            instance_name__startswith=self.INSTANCE_NAME_START).delete()


class HostBatchRequestMixin:
    """ 主机批量请求混入类 """

    @staticmethod
    def get_host_batch_request(number):
        """ 模拟请求信息 """
        host_list = []
        for i in range(number):
            host_list.append({
                "instance_name": f"host_new_{i}",
                "ip": f"10.10.10.{i}",
                "port": 36000,
                "username": "root",
                "password": "root_password",
                "data_folder": "/data",
                "operate_system": random.choice(("CentOS", "RedHat"))
            })
        return {"host_list": host_list}
