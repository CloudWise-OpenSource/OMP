# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/11/8 8:00 下午
# Description:
import json
from utils.plugin.salt_client import SaltClient
from utils.prometheus.prometheus import Prometheus


class ServiceZookeeperCrawl(Prometheus):
    """
    查询 prometheus zookeeper 指标
    """
    def __init__(self, env, instance):
        self.ret = {}
        self.basic = []
        self.env = env              # 环境
        self.instance = instance    # 主机ip
        self._obj = SaltClient()
        Prometheus.__init__(self)

    @staticmethod
    def unified_job(is_success, ret, msg):
        """
        实例方法 返回值统一处理
        :ret: 返回值
        :msg: 返回值描述
        :is_success: 请求是否成功
        """
        if is_success:
            if ret.get('result'):
                return ret['result'][0].get('value')[1]
            else:
                return ''
        else:
            return ''

    def service_status(self):
        """运行状态"""
        expr = f"up{{env='{self.env}', instance='{self.instance}', " \
               f"job='zookeeperExporter'}}"
        self.ret['service_status'] = self.unified_job(*self.query(expr))

    def run_time(self):
        """运行时间"""
        self.ret['run_time'] = '-'

    def cpu_usage(self):
        """cpu使用率"""
        self.ret['cpu_usage'] = f"-"

    def mem_usage(self):
        """内存使用率"""
        self.ret['mem_usage'] = f"-"

    def packets_received(self):
        """收包数"""
        expr = f"zk_packets_received{{env='{self.env}', " \
               f"instance=~'{self.instance}', job='zookeeperExporter'}}"
        self.basic.append({
            "name": "packets_received", "name_cn": "收包数",
            "value": self.unified_job(*self.query(expr))}
        )

    def packets_sent(self):
        """发包数"""
        expr = f"zk_packets_sent{{env='{self.env}', " \
               f"instance=~'{self.instance}', job='zookeeperExporter'}}"
        self.basic.append({
            "name": "packets_sent", "name_cn": "发包数",
            "value": self.unified_job(*self.query(expr))}
        )

    def num_alive_connections(self):
        """活跃连接数"""
        expr = f"zk_num_alive_connections{{env='{self.env}', " \
               f"instance=~'{self.instance}', job='zookeeperExporter'}}"
        self.basic.append({
            "name": "num_alive_connections", "name_cn": "活跃连接数",
            "value": self.unified_job(*self.query(expr))}
        )

    def outstanding_requests(self):
        """堆积请求数"""
        expr = f"zk_outstanding_requests{{env='{self.env}', " \
               f"instance=~'{self.instance}', job='zookeeperExporter'}}"
        self.basic.append({
            "name": "outstanding_requests", "name_cn": "堆积请求数",
            "value": self.unified_job(*self.query(expr))}
        )

    def znode_count(self):
        """znode数"""
        expr = f"zk_znode_count{{env='{self.env}', " \
               f"instance=~'{self.instance}', job='zookeeperExporter'}}"
        self.basic.append({
            "name": "znode_count", "name_cn": "znode数",
            "value": self.unified_job(*self.query(expr))}
        )

    def watch_count(self):
        """watch数"""
        expr = f"zk_watch_count{{env='{self.env}', " \
               f"instance=~'{self.instance}', job='zookeeperExporter'}}"
        self.basic.append({
            "name": "watch_count", "name_cn": "watch数",
            "value": self.unified_job(*self.query(expr))}
        )

    def salt_json(self):
        try:
            self._obj.salt_module_update()
            ret = self._obj.fun(self.instance, "zookeeper_check.main")
            if ret and ret[0]:
                ret = json.loads(ret[1])
            else:
                ret = {}
        except:
            ret = {}

        self.ret['cpu_usage'] = ret.get('cpu_usage', '-')
        self.ret['mem_usage'] = ret.get('mem_usage', '-')
        self.ret['run_time'] = ret.get('run_time', '-')
        self.ret['log_level'] = ret.get('log_level', '-')
        self.basic.append({"name": "node_status", "name_cn": "node状态",
                           "value": ret.get('node_status', '-')})
        self.basic.append({"name": "max_memory", "name_cn": "最大内存",
                           "value": ret.get('max_memory', '-')})

    def run(self):
        """统一执行实例方法"""
        target = ['service_status', 'run_time', 'cpu_usage', 'mem_usage',
                  'packets_received', 'packets_sent', 'num_alive_connections',
                  'outstanding_requests', 'znode_count', 'watch_count',
                  'salt_json']
        for t in target:
            if getattr(self, t):
                getattr(self, t)()
