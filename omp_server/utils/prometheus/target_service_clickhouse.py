# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: lingyang guo
# CreateDate: 2021/12/15 8:00 下午
# Description:
from utils.plugin.salt_client import SaltClient
from utils.prometheus.prometheus import Prometheus


class ServiceClickhouseCrawl(Prometheus):
    """
    查询 prometheus clickhouse 指标
    """

    def __init__(self, env, instance):
        self.ret = {}
        self.basic = []
        self.env = env  # 环境
        self.instance = instance  # 主机ip
        self._obj = SaltClient()
        self.metric_num = 12
        self.service_name = "clickhouse"
        Prometheus.__init__(self)

    def service_status(self):
        """运行状态"""
        expr = f"probe_success{{env='{self.env}', instance='{self.instance}', " \
               f"app='{self.service_name}'}}"
        self.ret['service_status'] = self.unified_job(*self.query(expr))

    def run_time(self):
        """clickhouse 运行时间"""
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
        """clickhouse cpu使用率"""
        expr = f"service_process_cpu_percent{{instance='{self.instance}',app='{self.service_name}'}}"
        val = self.unified_job(*self.query(expr))
        val = round(float(val), 4) if val else '0.00'
        self.ret['cpu_usage'] = f"{val}%"

    def mem_usage(self):
        """clickhouse 内存使用率"""
        expr = f"service_process_memory_percent{{instance='{self.instance}',app='{self.service_name}'}}"
        val = self.unified_job(*self.query(expr))
        val = round(float(val), 4) if val else '0.00'
        self.ret['mem_usage'] = f"{val}%"

    def query_nums(self):
        expr = f"clickhouse_query{{env='{self.env}',instance='{self.instance}',job='clickhouseExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["query"] = val

    def merge_nums(self):
        expr = f"clickhouse_merge{{env='{self.env}',instance='{self.instance}',job='clickhouseExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["merge"] = val

    def read_only_replica(self):
        expr = f"sum(clickhouse_readonly_replica{{env='{self.env}',instance='{self.instance}',job='clickhouseExporter'}})"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["read_only_replica"] = val

    def replication(self):
        expr = f"clickhouse_replicated_checks{{env='{self.env}',instance='{self.instance}',job='clickhouseExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["replication"] = val

    def clickhouse_read(self):
        expr = f"clickhouse_read{{env='{self.env}',instance='{self.instance}',job='clickhouseExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["clickhouse_read"] = val

    def clickhouse_write(self):
        expr = f"clickhouse_write{{env='{self.env}',instance='{self.instance}',job='clickhouseExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["clickhouse_write"] = val

    def pool_tasks(self):
        expr = f"clickhouse_background_pool_task{{env='{self.env}',instance='{self.instance}',job='clickhouseExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["pool_tasks"] = val

    def connections(self):
        expr = f"clickhouse_tcp_connection{{env='{self.env}',instance='{self.instance}',job='clickhouseExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["connections"] = val

    def clickhouse_memory_tracking(self):
        expr = f"clickhouse_memory_tracking{{env='{self.env}',instance='{self.instance}',job='clickhouseExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["memory"] = val

    def run(self):
        """统一执行实例方法"""
        target = ['service_status', 'run_time', 'cpu_usage', 'mem_usage', 'query_nums', 'merge_nums',
                  'read_only_replica', 'replication',
                  'clickhouse_read', 'clickhouse_write', 'pool_tasks', 'connections', 'clickhouse_memory_tracking']
        for t in target:
            if getattr(self, t):
                getattr(self, t)()
