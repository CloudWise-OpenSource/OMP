# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: lingyang guo
# CreateDate: 2021/12/15 8:00 下午
# Description:
from utils.plugin.salt_client import SaltClient
from utils.prometheus.prometheus import Prometheus


class ServiceHttpdCrawl(Prometheus):
    """
    查询 prometheus httpd 指标
    """

    def __init__(self, env, instance):
        self.ret = {}
        self.basic = []
        self.env = env  # 环境
        self.instance = instance  # 主机ip
        self._obj = SaltClient()
        self.metric_num = 14
        self.service_name = "httpd"
        Prometheus.__init__(self)

    def run_time(self):
        """httpd 运行时间"""
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
        """httpd cpu使用率"""
        expr = f"service_process_cpu_percent{{instance='{self.instance}',app='{self.service_name}'}}"
        val = self.unified_job(*self.query(expr))
        val = round(float(val), 4) if val else '-'
        self.ret['cpu_usage'] = f"{val}%"

    def mem_usage(self):
        """httpd 内存使用率"""
        expr = f"service_process_memory_percent{{instance='{self.instance}',app='{self.service_name}'}}"
        val = self.unified_job(*self.query(expr))
        val = round(float(val), 4) if val else '-'
        self.ret['mem_usage'] = f"{val}%"

    def process_max_fds(self):
        expr = f"process_max_fds{{env='{self.env}',instance='$host',job='httpdExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["process_max_fds"] = val
        self.basic.append({
            "name": "process_max_fds",
            "name_cn": "进程打开文件最大数",
            "value": val
        })

    def process_cpu_seconds_total(self):
        expr = f"process_cpu_seconds_total{{env='{self.env}',instance='$host',job='httpdExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["process_cpu_seconds_total"] = val
        self.basic.append({
            "name": "process_cpu_seconds_total",
            "name_cn": "进程占用cpu总时间",
            "value": val
        })

    def apache_accesses_total(self):
        expr = f"apache_accesses_total{{env='{self.env}',instance='$host'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["apache_accesses_total"] = val
        self.basic.append({
            "name": "apache_accesses_total",
            "name_cn": "access总数",
            "value": val
        })

    def apache_cpuload(self):
        expr = f"apache_cpuload{{env='{self.env}',instance='$host'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["apache_cpuload"] = val
        self.basic.append({
            "name": "apache_cpuload",
            "name_cn": "cpu负载",
            "value": val
        })

    def apache_workers(self):
        expr = f"apache_workers{{env='{self.env}',instance='$host'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["apache_workers"] = val
        self.basic.append({
            "name": "apache_workers",
            "name_cn": "worker数",
            "value": val
        })

    def http_request_size_bytes(self):
        expr = f"http_request_size_bytes{{env='{self.env}',instance='$host'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["http_request_size_bytes"] = val
        self.basic.append({
            "name": "http_request_size_bytes",
            "name_cn": "http请求字节数",
            "value": val
        })

    def apache_scoreboard(self):
        expr = f"apache_scoreboard{{env='{self.env}',instance='$host'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["apache_scoreboard"] = val
        self.basic.append({
            "name": "apache_scoreboard",
            "name_cn": "scoreboard值",
            "value": val
        })

    def run(self):
        """统一执行实例方法"""
        target = ['service_status', 'run_time', 'cpu_usage', 'mem_usage', 'process_max_fds',
                  'process_cpu_seconds_total', 'apache_accesses_total', 'apache_cpuload', 'apache_workers',
                  'http_request_size_bytes', 'http_request_size_bytes',
                  'apache_scoreboard']
        for t in target:
            if getattr(self, t):
                getattr(self, t)()
