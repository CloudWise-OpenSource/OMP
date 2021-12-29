# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: lingyang guo
# CreateDate: 2021/12/8 8:00 下午
# Description:
from utils.plugin.salt_client import SaltClient
from utils.prometheus.prometheus import Prometheus


class ServiceTengineCrawl(Prometheus):
    """
    查询 prometheus tengine 指标
    """

    def __init__(self, env, instance):
        self.ret = {}
        self.basic = []
        self.env = env  # 环境
        self.instance = instance  # 主机ip
        self._obj = SaltClient()
        self.metric_num = 11
        self.service_name = "tengine"
        Prometheus.__init__(self)

    def service_status(self):
        """运行状态"""
        expr = f"probe_success{{env='{self.env}', instance='{self.instance}', " \
               f"app='{self.service_name}'}}"
        self.ret['service_status'] = self.unified_job(*self.query(expr))

    def run_time(self):
        """tengine 运行时间"""
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
        """tengine cpu使用率"""
        expr = f"service_process_cpu_percent{{instance='{self.instance}',app='{self.service_name}'}}"
        val = self.unified_job(*self.query(expr))
        val = round(float(val), 4) if val else '0.00'
        self.ret['cpu_usage'] = f"{val}%"

    def mem_usage(self):
        """tengine 内存使用率"""
        expr = f"service_process_memory_percent{{instance='{self.instance}',app='{self.service_name}'}}"
        val = self.unified_job(*self.query(expr))
        val = round(float(val), 4) if val else '0.00'
        self.ret['mem_usage'] = f"{val}%"

    def server_connections(self):
        expr = f"nginx_server_connections{{env='{self.env}',instance='{self.instance}',status='active|writing|reading|waiting'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["server_connections"] = val

    def server_cache(self):
        expr = f"sum(irate(nginx_server_cache{{env='{self.env}',instance='{self.instance}'}}[5m])) by (status)"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["server_cache"] = val

    def server_requests(self):
        expr = f"sum(irate(nginx_server_requests{{env='{self.env}',instance='{self.instance}', code!='total'}}[5m])) by (code)"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["server_requests"] = val

    def server_bytes(self):
        expr = f"sum(irate(nginx_server_bytes{{env='{self.env}',instance='{self.instance}'}}[5m])) by (direction)"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["server_bytes"] = val

    def upstream_requests(self):
        expr = f"sum(irate(nginx_upstream_requests{{env='{self.env}',instance='{self.instance}', upstream='^$upstream$',code!='total'}}[5m])) by (code)"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["upstream_requests"] = val

    def upstream_bytes(self):
        expr = f"sum(irate(nginx_upstream_bytes{{env='{self.env}',instance='{self.instance}', upstream='^$upstream$'}}[5m])) by (direction)"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["upstream_bytes"] = val

    def upstream_backend_response(self):
        expr = f"sum(nginx_upstream_responseMsec{{env='{self.env}',instance='{self.instance}', upstream='^$upstream$'}}) by (backend)"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["upstream_backend_response"] = val

    def run(self):
        """统一执行实例方法"""
        target = ['service_status', 'run_time', 'cpu_usage', 'mem_usage', 'server_connections', 'server_cache',
                  'server_requests',
                  'server_bytes', 'upstream_requests', 'upstream_bytes', 'upstream_backend_response']
        for t in target:
            if getattr(self, t):
                getattr(self, t)()
