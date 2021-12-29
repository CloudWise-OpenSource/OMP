# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/11/8 8:00 下午
# Description:
from utils.plugin.salt_client import SaltClient
from utils.prometheus.prometheus import Prometheus


class ServiceZookeeperCrawl(Prometheus):
    """
    查询 prometheus zookeeper 指标
    """

    def __init__(self, env, instance):
        self.ret = {}
        self.basic = []
        self.env = env  # 环境
        self.instance = instance  # 主机ip
        self._obj = SaltClient()
        self.metric_num = 10
        self.service_name = "zookeeper"
        Prometheus.__init__(self)

    def service_status(self):
        """运行状态"""
        expr = f"probe_success{{env='{self.env}', instance='{self.instance}', " \
               f"app='{self.service_name}'}}"
        self.ret['service_status'] = self.unified_job(*self.query(expr))

    def run_time(self):
        """zookeeper 运行时间"""
        expr = f"process_uptime_seconds{{env='{self.env}', instance='{self.instance}', app='{self.service_name}'}}"
        _ = self.unified_job(*self.query(expr))
        _ = float(_) if _ else 0
        minutes, seconds = divmod(_, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        if int(days) > 0:
            self.ret['run_time'] = \
                f"{int(days)}天{int(hours)}小时{int(minutes)}分钟{int(seconds)}秒"
        elif int(hours) > 0:
            self.ret['run_time'] = \
                f"{int(hours)}小时{int(minutes)}分钟{int(seconds)}秒"
        else:
            self.ret['run_time'] = f"{int(minutes)}分钟{int(seconds)}秒"

    def cpu_usage(self):
        """zookeeper cpu使用率"""
        expr = f"service_process_cpu_percent{{instance='{self.instance}',app='{self.service_name}'}}"
        val = self.unified_job(*self.query(expr))
        val = round(float(val), 4) if val else '0.00'
        self.ret['cpu_usage'] = f"{val}%"

    def mem_usage(self):
        """zookeeper 内存使用率"""
        expr = f"service_process_memory_percent{{instance='{self.instance}',app='{self.service_name}'}}"
        val = self.unified_job(*self.query(expr))
        val = round(float(val), 4) if val else '0.00'
        self.ret['mem_usage'] = f"{val}%"

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
            "name": "znode_count", "name_cn": "节点数",
            "value": self.unified_job(*self.query(expr))}
        )

    def watch_count(self):
        """watch数"""
        expr = f"zk_watch_count{{env='{self.env}', " \
               f"instance=~'{self.instance}', job='zookeeperExporter'}}"
        self.basic.append({
            "name": "watch_count", "name_cn": "监测点数",
            "value": self.unified_job(*self.query(expr))}
        )

    def run(self):
        """统一执行实例方法"""
        target = ['service_status', 'run_time', 'cpu_usage', 'mem_usage',
                  'packets_received', 'packets_sent', 'num_alive_connections',
                  'outstanding_requests', 'znode_count', 'watch_count']
        for t in target:
            if getattr(self, t):
                getattr(self, t)()
