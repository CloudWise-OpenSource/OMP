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
        val = round(float(val), 4) if val else '-'
        self.ret['cpu_usage'] = f"{val}%"

    def mem_usage(self):
        """elasticsearch 内存使用率"""
        expr = f"service_process_memory_percent{{instance='{self.instance}',app='{self.service_name}'}}"
        val = self.unified_job(*self.query(expr))
        val = round(float(val), 4) if val else '-'
        self.ret['mem_usage'] = f"{val}%"

    def running_nodes(self):
        expr = f"sum(elasticsearch_cluster_health_number_of_nodes{{env='{self.env}',cluster='cw-es'}})/count(elasticsearch_cluster_health_number_of_nodes{{env='{self.env}',cluster='cw-es'}})"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["running_nodes"] = val
        self.basic.append({
            "name": "running_nodes",
            "name_cn": "运行节点数",
            "value": val
        })

    def active_data_nodes(self):
        expr = f"elasticsearch_cluster_health_number_of_data_nodes{{env='{self.env}',cluster='cw-es'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["active_data_nodes"] = val
        self.basic.append({
            "name": "active_data_nodes",
            "name_cn": "活跃数据节点数",
            "value": val
        })

    def pending_tasks(self):
        expr = f"elasticsearch_cluster_health_number_of_pending_tasks{{env='{self.env}',cluster='cw-es'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["pending_tasks"] = val
        self.basic.append({
            "name": "pending_tasks",
            "name_cn": "pending任务数",
            "value": val
        })

    def active_shards(self):
        expr = f"elasticsearch_cluster_health_active_shards{{env='{self.env}',cluster='cw-es'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["active_shards"] = val
        self.basic.append({
            "name": "active_shards",
            "name_cn": "活跃shard数",
            "value": val
        })

    def active_primary_shards(self):
        expr = f"elasticsearch_cluster_health_active_primary_shards{{env='{self.env}',cluster='cw-es'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["active_primary_shards"] = val
        self.basic.append({
            "name": "active_primary_shards",
            "name_cn": "活跃 primary shard数",
            "value": val
        })

    def initializing_shards(self):
        expr = f"elasticsearch_cluster_health_initializing_shards{{env='{self.env}',cluster='cw-es'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["initializing_shards"] = val
        self.basic.append({
            "name": "initializing_shards",
            "name_cn": "初始化中的 shard数",
            "value": val
        })

    def relocating_shards(self):
        expr = f"elasticsearch_cluster_health_relocating_shards{{env='{self.env}',cluster='cw-es'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["relocating_shards"] = val
        self.basic.append({
            "name": "relocating_shards",
            "name_cn": "迁移中的shard数",
            "value": val
        })

    def unassigned_shards(self):
        expr = f"elasticsearch_cluster_health_unassigned_shards{{env='{self.env}',cluster='cw-es'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["unassigned_shards"] = val
        self.basic.append({
            "name": "unassigned_shards",
            "name_cn": "未分配shard数",
            "value": val
        })

    def delayed_unassigned_shards(self):
        expr = f"elasticsearch_cluster_health_delayed_unassigned_shards{{env='{self.env}',cluster='cw-es'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["delayed_unassigned_shards"] = val
        self.basic.append({
            "name": "delayed_unassigned_shards",
            "name_cn": "延迟shard数",
            "value": val
        })

    def documents_indexed(self):
        expr = f"sum(elasticsearch_indices_docs{{env='{self.env}',cluster='cw-es'}})"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["documents_indexed"] = val
        self.basic.append({
            "name": "documents_indexed",
            "name_cn": "已索引文档数",
            "value": val
        })

    def index_size(self):
        expr = f"sum(elasticsearch_indices_store_size_bytes{{env='{self.env}',cluster='cw-es'}})"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["index_size"] = val
        self.basic.append({
            "name": "index_size",
            "name_cn": "索引大小",
            "value": val
        })

    def documents_indexed_rate(self):
        expr = f"rate(elasticsearch_indices_indexing_index_total{{env='{self.env}',cluster='cw-es'}}[1h])"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["documents_indexed_rate"] = val
        self.basic.append({
            "name": "documents_indexed_rate",
            "name_cn": "文档索引率",
            "value": val
        })

    def query_rate(self):
        expr = f"rate(elasticsearch_indices_search_fetch_total{{env='{self.env}',cluster='cw-es'}}[1h])"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["query_rate"] = val
        self.basic.append({
            "name": "query_rate",
            "name_cn": "查询率",
            "value": val
        })

    def queue_count(self):
        expr = f"sum(elasticsearch_thread_pool_queue_count{{env='{self.env}',cluster='cw-es', type!='management'}}) by (type)"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["queue_count"] = val
        self.basic.append({
            "name": "queue_count",
            "name_cn": "队列数",
            "value": val
        })

    def gc_seconds(self):
        expr = f"irate(elasticsearch_jvm_gc_collection_seconds_sum{{env='{self.env}',cluster='cw-es'}}[1m])"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["gc_seconds"] = val
        self.basic.append({
            "name": "gc_seconds",
            "name_cn": "gc总时间",
            "value": val
        })

    def thread_pool_rejections(self):
        expr = f"rate(elasticsearch_thread_pool_rejected_count{{env='{self.env}',cluster='cw-es', type!='management'}}[5m])"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["thread_pool_rejections"] = val
        self.basic.append({
            "name": "thread_pool_rejections",
            "name_cn": "线程池拒绝数",
            "value": val
        })

    def thread_pool_active_count(self):
        expr = f"sum(elasticsearch_thread_pool_active_count{{env='{self.env}',cluster='cw-es', type!='management'}}) by (type)"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["thread_pools"] = val
        self.basic.append({
            "name": "thread_pool_active_count",
            "name_cn": "线程池活跃数",
            "value": val
        })

    def avg_heap_in_15min(self):
        expr = f"avg_over_time(elasticsearch_jvm_memory_used_bytes{{area='heap',env='{self.env}',cluster='cw-es'}}[15m]) / elasticsearch_jvm_memory_max_bytes{{area='heap',env='{self.env}',cluster='cw-es'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["avg_heap_in_15min"] = val
        self.basic.append({
            "name": "avg_heap_in_15min",
            "name_cn": "15分钟堆内存平均使用大小",
            "value": val
        })

    def rx_rate_5m(self):
        expr = f"sum(rate(elasticsearch_transport_rx_packets_total{{env='{self.env}',cluster='cw-es'}}[5m]))"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["rx_tx_rate_5m"] = val
        self.basic.append({
            "name": "rx_rate_5m",
            "name_cn": "rx_rate_5m",
            "value": val
        })

    def tx_rate_5m(self):
        expr = f"sum(rate(elasticsearch_transport_tx_packets_total{{env='{self.env}',cluster='cw-es'}}[5m]))"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["rx_tx_rate_5m"] = val
        self.basic.append({
            "name": "tx_rate_5m",
            "name_cn": "tx_rate_5m",
            "value": val
        })

    def run(self):
        """统一执行实例方法"""
        target = ['service_status', 'run_time', 'cpu_usage', 'mem_usage', 'running_nodes',
                  'active_data_nodes',
                  'pending_tasks', 'active_shards', 'active_primary_shards', 'initializing_shards', 'relocating_shards',
                  'unassigned_shards', 'delayed_unassigned_shards', 'documents_indexed', 'index_size',
                  'documents_indexed_rate',
                  'query_rate', 'queue_count', 'gc_seconds', 'thread_pool_rejections', 'thread_pool_active_count',
                  'avg_heap_in_15min',
                  'rx_rate_5m', 'tx_rate_5m']
        for t in target:
            if getattr(self, t):
                getattr(self, t)()
