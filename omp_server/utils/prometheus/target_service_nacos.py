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
        self.env = env              # 环境
        self.instance = instance    # 主机ip
        Prometheus.__init__(self)

    @staticmethod
    def unified_job(is_success, ret):
        """
        实例方法 返回值统一处理
        :ret: 返回值
        :is_success: 请求是否成功
        """
        if is_success:
            if ret.get('result'):
                return ret['result'][0].get('value')[1]
            else:
                return 0
        else:
            return 0

    def service_status(self):
        """运行状态"""
        expr = f"count(nacos_monitor{{name='configCount',env=~'{self.env}'," \
               f"instance=~'{self.instance}'}})"
        self.ret['service_status'] = self.unified_job(*self.query(expr))

    def run_time(self):
        """运行时间"""
        self.ret['run_time'] = '-'

    def cpu_usage(self):
        """cpu使用率"""
        expr = f"system_cpu_usage{{env=~'{self.env}'," \
               f"instance=~'{self.instance}', job='nacosExporter'}} * 100"
        val = self.unified_job(*self.query(expr))
        val = round(float(val), 2) if val else 0
        self.ret['cpu_usage'] = f"{val}%"

    def mem_usage(self):
        """内存使用率"""
        expr = f"sum(jvm_memory_used_bytes{{area='heap', env='{self.env}'," \
               f"instance=~'{self.instance}'}}) / " \
               f"sum(jvm_memory_max_bytes{{area='heap', env=~'{self.env}'," \
               f"instance=~'{self.instance}'}}) * 100"
        val = self.unified_job(*self.query(expr))
        val = round(float(val), 2) if val else 0
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
        self.basic.append({
            "name": "max_memory", "name_cn": "最大内存",
            "value": self.unified_job(*self.query(expr))}
        )

    def run(self):
        """统一执行实例方法"""
        target = ['service_status', 'run_time', 'cpu_usage', 'mem_usage',
                  'thread_num', 'max_memory']
        for t in target:
            if getattr(self, t):
                getattr(self, t)()
