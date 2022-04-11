# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/11/8 8:00 下午
# Description:
from utils.prometheus.prometheus import Prometheus


class ServiceRedisCrawl(Prometheus):
    """
    查询 prometheus redis 指标
    """

    def __init__(self, env, instance):
        self.ret = {}
        self.basic = []
        self.env = env  # 环境
        self.instance = instance  # 主机ip
        self.metric_num = 8
        self.service_name = "redis"
        Prometheus.__init__(self)

    def service_status(self):
        """运行状态"""
        expr = f"probe_success{{env='{self.env}', instance='{self.instance}', " \
               f"app='{self.service_name}'}}"
        self.ret['service_status'] = self.unified_job(*self.query(expr))

    def run_time(self):
        """redis 运行时间"""
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
        """redis cpu使用率"""
        expr = f"service_process_cpu_percent{{instance='{self.instance}',app='{self.service_name}'}}"
        val = self.unified_job(*self.query(expr))
        val = round(float(val), 4) if val else '-'
        self.ret['cpu_usage'] = f"{val}%"

    def mem_usage(self):
        """redis 内存使用率"""
        expr = f"service_process_memory_percent{{instance='{self.instance}',app='{self.service_name}'}}"
        val = self.unified_job(*self.query(expr))
        val = round(float(val), 4) if val else '-'
        self.ret['mem_usage'] = f"{val}%"

    def conn_num(self):
        """连接数量"""
        expr = f"redis_connected_clients{{env='{self.env}'," \
               f"instance=~'{self.instance}'}}"
        self.basic.append({
            "name": "conn_num", "name_cn": "连接数量",
            "value": self.unified_job(*self.query(expr))}
        )

    def hit_rate(self):
        """命中率"""
        expr = f"(redis_keyspace_hits_total{{env='{self.env}', " \
               f"instance=~'{self.instance}', job='redisExporter'}}  / " \
               f"(redis_keyspace_hits_total{{env='{self.env}', " \
               f"instance=~'{self.instance}', job='redisExporter'}} + " \
               f"redis_keyspace_misses_total{{env='{self.env}', " \
               f"instance=~'{self.instance}', job='redisExporter'}})) * 100"
        val = self.unified_job(*self.query(expr))
        val = round(float(val), 4) if val else 0
        self.basic.append({
            "name": "hit_rate", "name_cn": "缓存命中率",
            "value": f"{val}%"}
        )

    def max_memory(self):
        """最大内存"""
        expr = f"redis_memory_max_bytes{{env=~'{self.env}'," \
               f"instance=~'{self.instance}'}})"
        val = self.unified_job(*self.query(expr))
        val = round(int(val) / 1048576, 2) if val else '-'
        self.basic.append({
            "name": "max_memory", "name_cn": "最大内存",
            "value": f"{val}m"}
        )

    def network_io(self):
        """网络io"""
        expr = f"redis_net_input_bytes_total{{env=~'{self.env}'," \
               f"instance=~'{self.instance}'}} / 1000000"
        val_in = self.unified_job(*self.query(expr))
        val_in = round(float(val_in), 2) if val_in else 0

        expr = f"redis_net_output_bytes_total{{env=~'{self.env}'," \
               f"instance=~'{self.instance}'}} / 1000000"
        val_out = self.unified_job(*self.query(expr))
        val_out = round(float(val_out), 2) if val_out else 0

        self.basic.append({
            "name": "network_io", "name_cn": "网络io",
            "value": f"{val_in}B/{val_out}B"}
        )

    def run(self):
        """统一执行实例方法"""
        target = ['service_status', 'run_time', 'cpu_usage', 'mem_usage',
                  'conn_num', 'hit_rate', 'max_memory', 'network_io']
        for t in target:
            if getattr(self, t):
                getattr(self, t)()
