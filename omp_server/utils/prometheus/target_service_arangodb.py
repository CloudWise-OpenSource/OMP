# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: lingyang guo
# CreateDate: 2021/12/15 8:00 下午
# Description:
from utils.plugin.salt_client import SaltClient
from utils.prometheus.prometheus import Prometheus


class ServiceArangodbCrawl(Prometheus):
    """
    查询 prometheus arangodb 指标
    """

    def __init__(self, env, instance):
        self.ret = {}
        self.basic = []
        self.env = env  # 环境
        self.instance = instance  # 主机ip
        self._obj = SaltClient()
        self.metric_num = 18
        self.service_name = "arangodb"
        Prometheus.__init__(self)

    def service_status(self):
        """运行状态"""
        expr = f"probe_success{{env='{self.env}', instance='{self.instance}', " \
               f"app='{self.service_name}'}}"
        self.ret['service_status'] = self.unified_job(*self.query(expr))

    def run_time(self):
        """arangodb 运行时间"""
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
        """arangodb cpu使用率"""
        expr = f"service_process_cpu_percent{{instance='{self.instance}',app='{self.service_name}'}}"
        val = self.unified_job(*self.query(expr))
        val = round(float(val), 4) if val else '-'
        self.ret['cpu_usage'] = f"{val}%"

    def mem_usage(self):
        """arangodb 内存使用率"""
        expr = f"service_process_memory_percent{{instance='{self.instance}',app='{self.service_name}'}}"
        val = self.unified_job(*self.query(expr))
        val = round(float(val), 4) if val else '-'
        self.ret['mem_usage'] = f"{val}%"

    def rocksdb_base_level(self):
        expr = f"rocksdb_base_level{{env='{self.env}',instance='{self.instance}',job='arangodbExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["rocksdb_base_level"] = val
        self.basic.append({
            "name": "rocksdb_base_level",
            "name_cn": "rocksdb基本等级",
            "value": val
        })

    def client_connections(self):
        expr = f"arangodb_client_connection_statistics_client_connections{{env='{self.env}',instance='{self.instance}',job='arangodbExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["client_connections"] = val
        self.basic.append({
            "name": "client_connections",
            "name_cn": "客户端连接数",
            "value": val
        })

    def rocksdb_background_errors(self):
        expr = f"rocksdb_background_errors{{env='{self.env}',instance='{self.instance}',job='arangodbExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["rocksdb_background_errors"] = val
        self.basic.append({
            "name": "rocksdb_background_errors",
            "name_cn": "rocksdb_background_errors",
            "value": val
        })

    def arangodb_transactions_started(self):
        expr = f"arangodb_transactions_started{{env='{self.env}',instance='{self.instance}',job='arangodbExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["arangodb_transactions_started"] = val
        self.basic.append({
            "name": "arangodb_transactions_started",
            "name_cn": "事务开启数",
            "value": val
        })

    def thread_numbers(self):
        expr = f"arangodb_process_statistics_number_of_threads{{env='{self.env}',instance='{self.instance}',job='arangodbExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["thread_numbers"] = val
        self.basic.append({
            "name": "thread_numbers",
            "name_cn": "线程数",
            "value": val
        })

    def rocksdb_cache_limit(self):
        expr = f"rocksdb_cache_limit{{env='{self.env}',instance='{self.instance}',job='arangodbExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["rocksdb_cache_limit"] = val
        self.basic.append({
            "name": "rocksdb_cache_limit",
            "name_cn": "缓存限制",
            "value": val
        })

    def rocksdb_size_all_mem_tables(self):
        expr = f"rocksdb_size_all_mem_tables{{env='{self.env}',instance='{self.instance}',job='arangodbExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["rocksdb_size_all_mem_tables"] = val
        self.basic.append({
            "name": "rocksdb_size_all_mem_tables",
            "name_cn": "表占用内存总字节数",
            "value": val
        })

    def rocksdb_cache_allocated(self):
        expr = f"rocksdb_cache_allocated{{env='{self.env}',instance='{self.instance}',job='arangodbExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["rocksdb_cache_allocated"] = val
        self.basic.append({
            "name": "rocksdb_cache_allocated",
            "name_cn": "rocksdb_cache_allocated",
            "value": val
        })

    def rocksdb_num_snapshots(self):
        expr = f"rocksdb_num_snapshots{{env='{self.env}',instance='{self.instance}',job='arangodbExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["rocksdb_num_snapshots"] = val
        self.basic.append({
            "name": "rocksdb_num_snapshots",
            "name_cn": "快照数",
            "value": val
        })

    def arangodb_transactions_committed(self):
        expr = f"arangodb_transactions_committed{{env='{self.env}',instance='{self.instance}',job='arangodbExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["arangodb_transactions_committed"] = val
        self.basic.append({
            "name": "arangodb_transactions_committed",
            "name_cn": "已提交事务数",
            "value": val
        })

    def rocksdb_estimate_num_keys(self):
        expr = f"rocksdb_estimate_num_keys{{env='{self.env}',instance='{self.instance}',job='arangodbExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["rocksdb_estimate_num_keys"] = val
        self.basic.append({
            "name": "rocksdb_estimate_num_keys",
            "name_cn": "预测key数",
            "value": val
        })

    def rocksdb_actual_delayed_write_rate(self):
        expr = f"rocksdb_actual_delayed_write_rate{{env='{self.env}',instance='{self.instance}',job='arangodbExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["rocksdb_actual_delayed_write_rate"] = val
        self.basic.append({
            "name": "rocksdb_actual_delayed_write_rate",
            "name_cn": "延迟写入率",
            "value": val
        })

    def rocksdb_cache_hit_rate_recent(self):
        expr = f"rocksdb_cache_hit_rate_recent{{env='{self.env}',instance='{self.instance}',job='arangodbExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["rocksdb_cache_hit_rate_recent"] = val
        self.basic.append({
            "name": "rocksdb_cache_hit_rate_recent",
            "name_cn": "当前缓存命中率",
            "value": val
        })

    def arangodb_transactions_aborted(self):
        expr = f"arangodb_transactions_aborted{{env='{self.env}',instance='{self.instance}',job='arangodbExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["arangodb_transactions_aborted"] = val
        self.basic.append({
            "name": "arangodb_transactions_aborted",
            "name_cn": "已中断事务数",
            "value": val
        })

    def run(self):
        """统一执行实例方法"""
        target = ['service_status', 'run_time', 'cpu_usage', 'mem_usage', 'rocksdb_base_level', 'client_connections',
                  'rocksdb_background_errors', 'arangodb_transactions_started',
                  'thread_numbers',
                  'rocksdb_cache_limit', 'rocksdb_size_all_mem_tables', 'rocksdb_cache_allocated',
                  'rocksdb_num_snapshots',
                  'arangodb_transactions_committed', 'rocksdb_estimate_num_keys', 'rocksdb_actual_delayed_write_rate',
                  'rocksdb_cache_hit_rate_recent', 'arangodb_transactions_aborted']
        for t in target:
            if getattr(self, t):
                getattr(self, t)()
