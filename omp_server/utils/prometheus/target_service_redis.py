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
        self.env = env              # 环境
        self.instance = instance    # 主机ip
        Prometheus.__init__(self)

    @staticmethod
    def unified_job(is_success, ret):
        """
        实例方法 返回值统一处理
        :ret: 返回值
        :is_success: 请求是否成功
        """
        if is_success:
            if ret.get('result'):
                return ret['result'][0].get('value')[1]
            else:
                return 0
        else:
            return 0

    def service_status(self):
        """运行状态"""
        expr = f"up{{env='{self.env}', instance='{self.instance}', " \
               f"job='redisExporter'}}"
        self.ret['service_status'] = self.unified_job(*self.query(expr))

    def run_time(self):
        """运行时间"""
        expr = f"max(max_over_time(redis_uptime_in_seconds{{env='{self.env}'," \
               f"instance=~'{self.instance}'}}[5m]))"
        _ = self.unified_job(*self.query(expr))
        _ = float(_) if _ else 0
        minutes, seconds = divmod(_, 60)
        hours, minutes = divmod(minutes, 60)
        self.ret['run_time'] = f"{int(hours)}小时{int(minutes)}分钟{int(seconds)}秒"

    def cpu_usage(self):
        """REDIS cpu使用率"""
        expr = f"rate(namedprocess_namegroup_cpu_seconds_total{{" \
               f"groupname=~'redis', instance=~'{self.instance}'," \
               f"mode='system'}}[5m]) * 100"
        val = self.unified_job(*self.query(expr))
        val = round(float(val), 4) if val else 0
        self.ret['cpu_usage'] = f"{val}%"

    def mem_usage(self):
        """REDIS 内存使用率"""
        expr = f"100 * (redis_memory_used_bytes{{env=~'{self.env}'," \
               f"instance=~'{self.instance}'}}  / " \
               f"redis_memory_max_bytes{{env=~'{self.env}'," \
               f"instance=~'{self.instance}'}})"
        val = self.unified_job(*self.query(expr))
        val = round(float(val), 4) if val else 0
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
        self.basic.append({
            "name": "max_memory", "name_cn": "最大内存",
            "value": self.unified_job(*self.query(expr))}
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
