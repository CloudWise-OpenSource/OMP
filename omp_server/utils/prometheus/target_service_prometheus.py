# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: lingyang guo
# CreateDate: 2021/12/15 8:00 下午
# Description:
from utils.plugin.salt_client import SaltClient
from utils.prometheus.prometheus import Prometheus


class ServicePrometheusCrawl(Prometheus):
    """
    查询 prometheus prometheus 指标
    """

    def __init__(self, env, instance):
        self.ret = {}
        self.basic = []
        self.env = env  # 环境
        self.instance = instance  # 主机ip
        self._obj = SaltClient()
        self.metric_num = 4
        self.service_name = "prometheus"
        Prometheus.__init__(self)

    def service_status(self):
        """运行状态"""
        expr = f"probe_success{{env='{self.env}', instance='{self.instance}', " \
               f"app='{self.service_name}'}}"
        self.ret['service_status'] = self.unified_job(*self.query(expr))

    def run_time(self):
        """prometheus 运行时间"""
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
        """prometheus cpu使用率"""
        expr = f"service_process_cpu_percent{{instance='{self.instance}',app='{self.service_name}'}}"
        val = self.unified_job(*self.query(expr))
        val = round(float(val), 4) if val else '-'
        self.ret['cpu_usage'] = f"{val}%"

    def mem_usage(self):
        """prometheus 内存使用率"""
        expr = f"service_process_memory_percent{{instance='{self.instance}',app='{self.service_name}'}}"
        val = self.unified_job(*self.query(expr))
        val = round(float(val), 4) if val else '-'
        self.ret['mem_usage'] = f"{val}%"

    def run(self):
        """统一执行实例方法"""
        target = ['service_status', 'run_time',
                  'cpu_usage', 'mem_usage', 'test_test']
        for t in target:
            if getattr(self, t):
                getattr(self, t)()
