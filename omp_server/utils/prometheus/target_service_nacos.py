# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/11/8 8:00 下午
# Description:
from utils.prometheus.prometheus import Prometheus


class ServiceNacosCrawl(Prometheus):
    """
    查询 prometheus Nacos 指标
    """

    def __init__(self, env, instance):
        self.ret = {}
        self.basic = []
        self.env = env  # 环境
        self.instance = instance  # 主机ip
        self.metric_num = 6
        self.service_name = "nacos"
        Prometheus.__init__(self)

    def service_status(self):
        """运行状态"""
        expr = f"count(nacos_monitor{{name='configCount',env=~'{self.env}'," \
               f"instance=~'{self.instance}'}})"
        self.ret['service_status'] = self.unified_job(*self.query(expr))

    def run_time(self):
        """nacos 运行时间"""
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
        """nacos cpu使用率"""
        expr = f"service_process_cpu_percent{{instance='{self.instance}',app='{self.service_name}'}}"
        val = self.unified_job(*self.query(expr))
        val = round(float(val), 4) if val else '0.00'
        self.ret['cpu_usage'] = f"{val}%"

    def mem_usage(self):
        """nacos 内存使用率"""
        expr = f"service_process_memory_percent{{instance='{self.instance}',app='{self.service_name}'}}"
        val = self.unified_job(*self.query(expr))
        val = round(float(val), 4) if val else '0.00'
        self.ret['mem_usage'] = f"{val}%"

    def thread_num(self):
        """进程数量"""
        expr = f"max(jvm_threads_daemon_threads{{env=~'{self.env}'," \
               f"instance=~'{self.instance}'}})"
        self.basic.append({
            "name": "thread_num", "name_cn": "进程数量",
            "value": self.unified_job(*self.query(expr))}
        )

    def max_memory(self):
        """最大内存"""
        expr = f"sum(jvm_memory_max_bytes{{area='heap', " \
               f"env=~'{self.env}',instance=~'{self.instance}'}})"
        val = self.unified_job(*self.query(expr))
        val = round(int(val) / 1048576, 2) if val else '-'
        self.basic.append({
            "name": "max_memory", "name_cn": "最大内存",
            "value": f"{val}m"}
        )

    def run(self):
        """统一执行实例方法"""
        target = ['service_status', 'run_time', 'cpu_usage', 'mem_usage',
                  'thread_num', 'max_memory']
        for t in target:
            if getattr(self, t):
                getattr(self, t)()
