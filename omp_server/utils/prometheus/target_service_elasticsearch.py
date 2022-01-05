# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: lingyang guo
# CreateDate: 2021/12/15 8:00 下午
# Description:
from utils.plugin.salt_client import SaltClient
from utils.prometheus.prometheus import Prometheus


class ServiceElasticsearchCrawl(Prometheus):
    """
    查询 prometheus elasticsearch 指标
    """

    def __init__(self, env, instance):
        self.ret = {}
        self.basic = []
        self.env = env  # 环境
        self.instance = instance  # 主机ip
        self._obj = SaltClient()
        self.metric_num = 25
        self.service_name = "elasticsearch"
        Prometheus.__init__(self)

    def service_status(self):
        """运行状态"""
        expr = f"probe_success{{env='{self.env}', instance='{self.instance}', " \
               f"app='{self.service_name}'}}"
        self.ret['service_status'] = self.unified_job(*self.query(expr))

    def run_time(self):
        """elasticsearch 运行时间"""
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
        """elasticsearch cpu使用率"""
        expr = f"service_process_cpu_percent{{instance='{self.instance}',app='{self.service_name}'}}"
        val = self.unified_job(*self.query(expr))
        val = round(float(val), 4) if val else '0.00'
        self.ret['cpu_usage'] = f"{val}%"

    def mem_usage(self):
        """elasticsearch 内存使用率"""
        expr = f"service_process_memory_percent{{instance='{self.instance}',app='{self.service_name}'}}"
        val = self.unified_job(*self.query(expr))
        val = round(float(val), 4) if val else '0.00'
        self.ret['mem_usage'] = f"{val}%"

    def running_nodes(self):
        expr = f"sum(elasticsearch_cluster_health_number_of_nodes{{env='{self.env}',cluster='cw-es'}})/count(elasticsearch_cluster_health_number_of_nodes{{env='{self.env}',cluster='cw-es'}})"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["running_nodes"] = val

    def active_data_nodes(self):
        expr = f"elasticsearch_cluster_health_number_of_data_nodes{{env='{self.env}',cluster='cw-es'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["active_data_nodes"] = val

    def pending_tasks(self):
        expr = f"elasticsearch_cluster_health_number_of_pending_tasks{{env='{self.env}',cluster='cw-es'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["pending_tasks"] = val

    def active_shards(self):
        expr = f"elasticsearch_cluster_health_active_shards{{env='{self.env}',cluster='cw-es'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["active_shards"] = val

    def active_primary_shards(self):
        expr = f"elasticsearch_cluster_health_active_primary_shards{{env='{self.env}',cluster='cw-es'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["active_primary_shards"] = val

    def initializing_shards(self):
        expr = f"elasticsearch_cluster_health_initializing_shards{{env='{self.env}',cluster='cw-es'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["initializing_shards"] = val

    def relocating_shards(self):
        expr = f"elasticsearch_cluster_health_relocating_shards{{env='{self.env}',cluster='cw-es'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["relocating_shards"] = val

    def unassigned_shards(self):
        expr = f"elasticsearch_cluster_health_unassigned_shards{{env='{self.env}',cluster='cw-es'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["unassigned_shards"] = val

    def delayed_unassigned_shards(self):
        expr = f"elasticsearch_cluster_health_delayed_unassigned_shards{{env='{self.env}',cluster='cw-es'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["delayed_unassigned_shards"] = val

    def documents_indexed(self):
        expr = f"sum(elasticsearch_indices_docs{{env='{self.env}',cluster='cw-es'}})"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["documents_indexed"] = val

    def index_size(self):
        expr = f"sum(elasticsearch_indices_store_size_bytes{{env='{self.env}',cluster='cw-es'}})"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["index_size"] = val

    def documents_indexed_rate(self):
        expr = f"rate(elasticsearch_indices_indexing_index_total{{env='{self.env}',cluster='cw-es'}}[1h])"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["documents_indexed_rate"] = val

    def query_rate(self):
        expr = f"rate(elasticsearch_indices_search_fetch_total{{env='{self.env}',cluster='cw-es'}}[1h])"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["query_rate"] = val

    def queue_count(self):
        expr = f"sum(elasticsearch_thread_pool_queue_count{{env='{self.env}',cluster='cw-es', type!='management'}}) by (type)"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["queue_count"] = val

    def gc_seconds(self):
        expr = f"irate(elasticsearch_jvm_gc_collection_seconds_sum{{env='{self.env}',cluster='cw-es'}}[1m])"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["gc_seconds"] = val

    def thread_pool_rejections(self):
        expr = f"rate(elasticsearch_thread_pool_rejected_count{{env='{self.env}',cluster='cw-es', type!='management'}}[5m])"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["thread_pool_rejections"] = val

    def thread_pools(self):
        expr = f"sum(elasticsearch_thread_pool_active_count{{env='{self.env}',cluster='cw-es', type!='management'}}) by (type)"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["thread_pools"] = val

    def avg_heap_in_15min(self):
        expr = f"avg_over_time(elasticsearch_jvm_memory_used_bytes{{area='heap',env='{self.env}',cluster='cw-es'}}[15m]) / elasticsearch_jvm_memory_max_bytes{{area='heap',env='{self.env}',cluster='cw-es'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["avg_heap_in_15min"] = val

    def rx_rate_5m(self):
        expr = f"sum(rate(elasticsearch_transport_rx_packets_total{{env='{self.env}',cluster='cw-es'}}[5m]))"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["rx_tx_rate_5m"] = val

    def tx_rate_5m(self):
        expr = f"sum(rate(elasticsearch_transport_tx_packets_total{{env='{self.env}',cluster='cw-es'}}[5m]))"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["rx_tx_rate_5m"] = val

    def run(self):
        """统一执行实例方法"""
        target = ['service_status', 'run_time', 'cpu_usage', 'mem_usage', 'running_nodes',
                  'active_data_nodes',
                  'pending_tasks', 'active_shards', 'active_primary_shards', 'initializing_shards', 'relocating_shards',
                  'unassigned_shards', 'delayed_unassigned_shards', 'documents_indexed', 'index_size',
                  'documents_indexed_rate',
                  'query_rate', 'queue_count', 'gc_seconds', 'thread_pool_rejections', 'thread_pools',
                  'avg_heap_in_15min',
                  'rx_rate_5m', 'tx_rate_5m']
        for t in target:
            if getattr(self, t):
                getattr(self, t)()
