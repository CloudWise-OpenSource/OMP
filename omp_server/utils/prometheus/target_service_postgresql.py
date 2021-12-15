# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: lingyang guo
# CreateDate: 2021/12/15 8:00 下午
# Description:
import json
from utils.plugin.salt_client import SaltClient
from utils.prometheus.prometheus import Prometheus


class ServicePostgresqlCrawl(Prometheus):
    """
    查询 prometheus postgresql 指标
    """

    def __init__(self, env, instance):
        self.ret = {}
        self.basic = []
        self.env = env  # 环境
        self.instance = instance  # 主机ip
        self._obj = SaltClient()
        self.metric_num = 6
        Prometheus.__init__(self)

    def salt_json(self):
        try:
            self._obj.salt_module_update()
            ret = self._obj.fun(self.instance, "kafka_check.main")
            if ret and ret[0]:
                ret = json.loads(ret[1])
            else:
                ret = {}
        except Exception:
            ret = {}

        self.ret['cpu_usage'] = ret.get('cpu_usage', '-')
        self.ret['mem_usage'] = ret.get('mem_usage', '-')
        self.ret['run_time'] = ret.get('run_time', '-')
        self.ret['log_level'] = ret.get('log_level', '-')
        self.ret['service_status'] = ret.get('service_status', '-')
        self.basic.append({"name": "max_memory", "name_cn": "最大内存",
                           "value": ret.get('max_memory', '-')})

    def run(self):
        """统一执行实例方法"""
        target = ['service_status', 'run_time', 'cpu_usage', 'mem_usage',
                  'conn_num', 'max_memory', 'salt_json']
        for t in target:
            if getattr(self, t):
                getattr(self, t)()
