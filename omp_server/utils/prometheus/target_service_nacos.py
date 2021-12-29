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
        self.metric_num = 17
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

    def service_count(self):
        expr = f"max(nacos_monitor{{name='serviceCount',env='{self.env}',instance='{self.instance}'}})"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["service_count"] = val

    def ip_count(self):
        expr = f"max(nacos_monitor{{name='ipCount',env='{self.env}',instance='{self.instance}'}})"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["ip_count"] = val

    def config_count(self):
        expr = f"max(nacos_monitor{{name='configCount',env='{self.env}',instance='{self.instance}'}})"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["config_count"] = val

    def config_push_total(self):
        expr = f"sum(nacos_monitor{{name='getConfig',env='{self.env}',instance='{self.instance}'}}) by (name)"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["config_push_total"] = val

    def threads(self):
        expr = f"max(jvm_threads_daemon_threads{{env='{self.env}',instance='{self.instance}'}})"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["threads"] = val

    def notify_rt(self):
        expr = f"sum(rate(nacos_timer_seconds_sum{{env='{self.env}',instance='{self.instance}'}}[1m]))/sum(rate(nacos_timer_seconds_count{{env='{self.env}',instance='{self.instance}'}}[1m])) * 1000"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["notify_rt"] = val

    def long_polling(self):
        expr = f"sum(nacos_monitor{{name='longPolling', env='{self.env}',instance='{self.instance}'}})"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["long_polling"] = val

    def qps(self):
        expr = f"sum(rate(http_server_requests_seconds_count{{uri='/v1/cs/configs|/nacos/v1/ns/instance|/nacos/v1/ns/health', env='{self.env}',instance='{self.instance}'}}[1m])) by (method,uri)"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["qps"] = val

    def leader_status(self):
        expr = f"sum(nacos_monitor{{name='leaderStatus', env='{self.env}',instance='{self.instance}'}})"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["leader_status"] = val

    def avg_push_cost(self):
        expr = f"sum(nacos_monitor{{name='avgPushCost', env='{self.env}',instance='{self.instance}'}})"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["avg_push_cost"] = val

    def max_push_cost(self):
        expr = f"max(nacos_monitor{{name='maxPushCost', env='{self.env}',instance='{self.instance}'}})"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["max_push_cost"] = val

    def config_statistics(self):
        expr = f"sum(nacos_monitor{{name='publish', env='{self.env}',instance='{self.instance}'}}) by (name)"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["config_statistics"] = val

    def health_check(self):
        expr = f"sum(rate(nacos_monitor{{name='.*HealthCheck', env='{self.env}',instance='{self.instance}'}}[1m])) by (name) * 60"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["health_check"] = val

    def run(self):
        """统一执行实例方法"""
        target = ['service_status', 'run_time', 'cpu_usage', 'mem_usage', 'service_count', 'ip_count',
                  'config_count', 'config_push_total', 'threads', 'notify_rt',
                  'long_polling', 'qps', 'leader_status',
                  'avg_push_cost', 'max_push_cost', 'config_statistics', 'health_check']
        for t in target:
            if getattr(self, t):
                getattr(self, t)()
