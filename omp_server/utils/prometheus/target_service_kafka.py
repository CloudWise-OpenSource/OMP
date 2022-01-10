# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/11/8 8:00 下午
# Description:
from utils.plugin.salt_client import SaltClient
from utils.prometheus.prometheus import Prometheus


class ServiceKafkaCrawl(Prometheus):
    """
    查询 prometheus kafka 指标
    """

    def __init__(self, env, instance):
        self.ret = {}
        self.basic = []
        self.env = env  # 环境
        self.instance = instance  # 主机ip
        self._obj = SaltClient()
        self.metric_num = 4
        self.service_name = "kafka"
        Prometheus.__init__(self)

    def service_status(self):
        """运行状态"""
        expr = f"probe_success{{env='{self.env}', instance='{self.instance}', " \
               f"app='{self.service_name}'}}"
        self.ret['service_status'] = self.unified_job(*self.query(expr))

    def run_time(self):
        """kafka 运行时间"""
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
        """kafka cpu使用率"""
        expr = f"service_process_cpu_percent{{instance='{self.instance}',app='{self.service_name}'}}"
        val = self.unified_job(*self.query(expr))
        val = round(float(val), 4) if val else '-'
        self.ret['cpu_usage'] = f"{val}%"

    def mem_usage(self):
        """kafka 内存使用率"""
        expr = f"service_process_memory_percent{{instance='{self.instance}',app='{self.service_name}'}}"
        val = self.unified_job(*self.query(expr))
        val = round(float(val), 4) if val else '-'
        self.ret['mem_usage'] = f"{val}%"

    def kafka_brokers(self):
        """kafka brokers"""
        expr = f"kafka_brokers{{env='{self.env}',instance='{self.instance}'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["kafka_brokers"] = val
        self.basic.append({
            "name": "kafka_brokers",
            "name_cn": "broker数",
            "value": val
        })

    def process_open_fds(self):
        """kafka brokers"""
        expr = f"process_open_fds{{env='{self.env}',instance='{self.instance}'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["process_open_fds"] = val
        self.basic.append({
            "name": "process_open_fds",
            "name_cn": "打开文件描述符数",
            "value": val
        })

    def process_resident_memory_bytes(self):
        """kafka brokers"""
        expr = f"process_resident_memory_bytes{{env='{self.env}',instance='{self.instance}'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["process_resident_memory_bytes"] = val
        self.basic.append({
            "name": "process_resident_memory_bytes",
            "name_cn": "resident memory",
            "value": val
        })

    def run(self):
        """统一执行实例方法"""
        target = ['service_status', 'run_time', 'cpu_usage', 'mem_usage', 'kafka_brokers', 'process_open_fds',
                  'process_resident_memory_bytes']
        for t in target:
            if getattr(self, t):
                getattr(self, t)()
