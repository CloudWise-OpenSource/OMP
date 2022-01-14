# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: lingyang guo
# CreateDate: 2021/12/15 8:00 下午
# Description:
from utils.plugin.salt_client import SaltClient
from utils.prometheus.prometheus import Prometheus


class ServiceIgniteCrawl(Prometheus):
    """
    查询 prometheus ignite 指标
    """

    def __init__(self, env, instance):
        self.ret = {}
        self.basic = []
        self.env = env  # 环境
        self.instance = instance  # 主机ip
        self._obj = SaltClient()
        self.metric_num = 19
        self.service_name = "ignite"
        Prometheus.__init__(self)

    def service_status(self):
        """运行状态"""
        expr = f"probe_success{{env='{self.env}', instance='{self.instance}', " \
               f"app='{self.service_name}'}}"
        self.ret['service_status'] = self.unified_job(*self.query(expr))

    def run_time(self):
        """ignite 运行时间"""
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
        """ignite cpu使用率"""
        expr = f"service_process_cpu_percent{{instance='{self.instance}',app='{self.service_name}'}}"
        val = self.unified_job(*self.query(expr))
        val = round(float(val), 4) if val else '-'
        self.ret['cpu_usage'] = f"{val}%"

    def mem_usage(self):
        """ignite 内存使用率"""
        expr = f"service_process_memory_percent{{instance='{self.instance}',app='{self.service_name}'}}"
        val = self.unified_job(*self.query(expr))
        val = round(float(val), 4) if val else '-'
        self.ret['mem_usage'] = f"{val}%"

    def ignite_started_thread_count(self):
        expr = f"ignite_started_thread_count{{env='{self.env}',instance='{self.instance}',job='igniteExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["ignite_started_thread_count"] = val
        self.basic.append({
            "name": "ignite_started_thread_count",
            "name_cn": "开启线程数",
            "value": val
        })

    def sent_messages_count(self):
        expr = f"sent_messages_count{{env='{self.env}',instance='{self.instance}',job='igniteExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["sent_messages_count"] = val
        self.basic.append({
            "name": "sent_messages_count",
            "name_cn": "发送message数",
            "value": val
        })

    def ignite_received_messages_count(self):
        expr = f"ignite_received_messages_count{{env='{self.env}',instance='{self.instance}',job='igniteExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["ignite_received_messages_count"] = val
        self.basic.append({
            "name": "ignite_received_messages_count",
            "name_cn": "收到message数",
            "value": val
        })

    def average_job_wait_time(self):
        expr = f"average_job_wait_time{{env='{self.env}',instance='{self.instance}',job='igniteExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["average_job_wait_time"] = val
        self.basic.append({
            "name": "average_job_wait_time",
            "name_cn": "任务平均等待时间",
            "value": val
        })

    def current_job_wait_time(self):
        expr = f"current_job_wait_time{{env='{self.env}',instance='{self.instance}',job='igniteExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["current_job_wait_time"] = val
        self.basic.append({
            "name": "current_job_wait_time",
            "name_cn": "当前任务等待时间",
            "value": val
        })

    def maximum_job_wait_time(self):
        expr = f"maximum_job_wait_time{{env='{self.env}',instance='{self.instance}',job='igniteExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["maximum_job_wait_time"] = val
        self.basic.append({
            "name": "maximum_job_wait_time",
            "name_cn": "最大任务等待时间",
            "value": val
        })

    def average_job_execute_time(self):
        expr = f"average_job_execute_time{{env='{self.env}',instance='{self.instance}',job='igniteExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["average_job_execute_time"] = val
        self.basic.append({
            "name": "average_job_execute_time",
            "name_cn": "任务平均执行时间",
            "value": val
        })

    def current_job_execute_time(self):
        expr = f"current_job_execute_time{{env='{self.env}',instance='{self.instance}',job='igniteExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["current_job_execute_time"] = val
        self.basic.append({
            "name": "current_job_execute_time",
            "name_cn": "当前任务执行时间",
            "value": val
        })

    def maximum_job_execute_time(self):
        expr = f"maximum_job_execute_time{{env='{self.env}',instance='{self.instance}',job='igniteExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["maximum_job_execute_time"] = val
        self.basic.append({
            "name": "current_job_execute_time",
            "name_cn": "任务最大执行时间",
            "value": val
        })

    def busy_time_percentage(self):
        expr = f"busy_time_percentage{{env='{self.env}',instance='{self.instance}',job='igniteExporter'}}*100"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["busy_time_percentage"] = val
        self.basic.append({
            "name": "busy_time_percentage",
            "name_cn": "忙碌时间占比",
            "value": val
        })

    def ignite_busy_time_total(self):
        expr = f"rate(total_busy_time{{env='{self.env}',instance='{self.instance}',job='igniteExporter'}}[5m])"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["ignite_busy_time_total"] = val
        self.basic.append({
            "name": "ignite_busy_time_total",
            "name_cn": "忙碌态总时间",
            "value": val
        })

    def ignite_idle_time_total(self):
        expr = f"rate(ignite_idle_time_total{{env='{self.env}',instance='{self.instance}',job='igniteExporter'}}[5m])"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["ignite_idle_time_total"] = val
        self.basic.append({
            "name": "ignite_idle_time_total",
            "name_cn": "空闲态总时间",
            "value": val
        })

    def current_daemon_thread_count(self):
        expr = f"current_daemon_thread_count{{env='{self.env}',instance='{self.instance}',job='igniteExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["current_daemon_thread_count"] = val
        self.basic.append({
            "name": "current_daemon_thread_count",
            "name_cn": "当前后台线程数",
            "value": val
        })

    def maximum_thread_count(self):
        expr = f"maximum_thread_count{{env='{self.env}',instance='{self.instance}',job='igniteExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["maximum_thread_count"] = val
        self.basic.append({
            "name": "maximum_thread_count",
            "name_cn": "最大线程数",
            "value": val
        })

    def current_thread_count(self):
        expr = f"current_thread_count{{env='{self.env}',instance='{self.instance}',job='igniteExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["current_thread_count"] = val
        self.basic.append({
            "name": "current_thread_count",
            "name_cn": "当前线程数",
            "value": val
        })

    def run(self):
        """统一执行实例方法"""
        target = ['service_status', 'run_time', 'cpu_usage', 'mem_usage', 'ignite_started_thread_count',
                  'sent_messages_count', 'ignite_received_messages_count', 'average_job_wait_time',
                  'current_job_wait_time',
                  'maximum_job_wait_time', 'average_job_execute_time', 'current_job_execute_time',
                  'maximum_job_execute_time',
                  'busy_time_percentage', 'ignite_busy_time_total', 'ignite_idle_time_total',
                  'current_daemon_thread_count',
                  'maximum_thread_count', 'current_thread_count']
        for t in target:
            if getattr(self, t):
                getattr(self, t)()
