# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: lingyang guo
# CreateDate: 2021/12/15 8:00 下午
# Description:
from utils.plugin.salt_client import SaltClient
from utils.prometheus.prometheus import Prometheus


class ServicePostgresqlCrawl(Prometheus):
    """
    查询 prometheus postgresql 指标
    """

    def __init__(self, env, instance):
        self.ret = {}
        self.basic = []
        self.env = env  # 环境
        self.instance = instance  # 主机ip
        self._obj = SaltClient()
        self.metric_num = 16
        self.service_name = "postgresql"
        Prometheus.__init__(self)

    def service_status(self):
        """运行状态"""
        expr = f"probe_success{{env='{self.env}', instance='{self.instance}', " \
               f"app='{self.service_name}'}}"
        self.ret['service_status'] = self.unified_job(*self.query(expr))

    def run_time(self):
        """postgresql 运行时间"""
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
        """postgresql cpu使用率"""
        expr = f"service_process_cpu_percent{{instance='{self.instance}',app='{self.service_name}'}}"
        val = self.unified_job(*self.query(expr))
        val = round(float(val), 4) if val else '0.00'
        self.ret['cpu_usage'] = f"{val}%"

    def mem_usage(self):
        """postgresql 内存使用率"""
        expr = f"service_process_memory_percent{{instance='{self.instance}',app='{self.service_name}'}}"
        val = self.unified_job(*self.query(expr))
        val = round(float(val), 4) if val else '0.00'
        self.ret['mem_usage'] = f"{val}%"

    def current_fetch_data(self):
        expr = f"SUM(pg_stat_database_tup_fetched{{env='{self.env}',instance='{self.instance}'}})"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["current_fetch_data"] = val

    def current_insert_data(self):
        expr = f"SUM(pg_stat_database_tup_inserted{{release='$release', env='{self.env}',instance='{self.instance}'}})"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["current_insert_data"] = val

    def current_update_data(self):
        expr = f"SUM(pg_stat_database_tup_updated{{env='{self.env}',instance='{self.instance}'}})"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["current_update_data"] = val

    def max_connections(self):
        expr = f"pg_settings_max_connections{{release='$release', env='{self.env}',instance='{self.instance}'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["max_connections"] = val

    def open_file_descriptors(self):
        expr = f"process_open_fds{{release='$release', env='{self.env}',instance='{self.instance}'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["open_file_descriptors"] = val

    def shared_buffers(self):
        expr = f"pg_settings_shared_buffers_bytes{{env='{self.env}',instance='{self.instance}'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["shared_buffers"] = val

    def effective_cache(self):
        expr = f"pg_settings_effective_cache_size_bytes{{env='{self.env}',instance='{self.instance}'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["effective_cache"] = val

    def max_wal_size(self):
        expr = f"pg_settings_max_wal_size_bytes{{env='{self.env}',instance='{self.instance}'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["max_wal_size"] = val

    def random_page_cost(self):
        expr = f"pg_settings_random_page_cost{{env='{self.env}',instance='{self.instance}'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["random_page_cost"] = val

    def seq_page_cost(self):
        expr = f"pg_settings_seq_page_cost{{env='{self.env}',instance='{self.instance}'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["seq_page_cost"] = val

    def max_worker_processes(self):
        expr = f"pg_settings_max_worker_processes{{env='{self.env}',instance='{self.instance}'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["max_worker_processes"] = val

    def max_parallel_workers(self):
        expr = f"pg_settings_max_parallel_workers{{env='{self.env}',instance='{self.instance}'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["max_parallel_workers"] = val

    def run(self):
        """统一执行实例方法"""
        target = ['service_status', 'run_time', 'cpu_usage', 'mem_usage', 'current_fetch_data',
                  'current_insert_data', 'current_update_data', 'max_connections',
                  'open_file_descriptors', 'shared_buffers', 'effective_cache',
                  'max_wal_size',
                  'random_page_cost', 'seq_page_cost', 'max_worker_processes', 'max_parallel_workers']
        for t in target:
            if getattr(self, t):
                getattr(self, t)()
