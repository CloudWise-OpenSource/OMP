# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/11/8 8:00 下午
# Description:
import json
from utils.plugin.salt_client import SaltClient
from utils.prometheus.prometheus import Prometheus


class ServiceRocketmqCrawl(Prometheus):
    """
    查询 prometheus rocketmq 指标
    """

    def __init__(self, env, instance):
        self.ret = {}
        self.basic = []
        self.env = env  # 环境
        self.instance = instance  # 主机ip
        self._obj = SaltClient()
        self.metric_num = 4
        self.service_name = "rocketmq"
        Prometheus.__init__(self)

    def service_status(self):
        """运行状态"""
        expr = f"probe_success{{env='{self.env}', instance='{self.instance}', " \
               f"app='{self.service_name}'}}"
        self.ret['service_status'] = self.unified_job(*self.query(expr))

    def run_time(self):
        """rocketmq 运行时间"""
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
        """rocketmq cpu使用率"""
        expr = f"service_process_cpu_percent{{instance='{self.instance}',app='{self.service_name}'}}"
        val = self.unified_job(*self.query(expr))
        val = round(float(val), 4) if val else '-'
        self.ret['cpu_usage'] = f"{val}%"

    def mem_usage(self):
        """rocketmq 内存使用率"""
        expr = f"service_process_memory_percent{{instance='{self.instance}',app='{self.service_name}'}}"
        val = self.unified_job(*self.query(expr))
        val = round(float(val), 4) if val else '-'
        self.ret['mem_usage'] = f"{val}%"

    def broker_tps(self):
        """生产消息数量/s"""
        expr = f"rocketmq_broker_tps{{env=~'{self.env}'," \
               f"instance=~'{self.instance}'}}"
        self.basic.append({
            "name": "broker_tps", "name_cn": "生产消息数量/s",
            "value": self.unified_job(*self.query(expr))}
        )

    def broker_qps(self):
        """消费消息数量/s"""
        expr = f"rocketmq_broker_qps{{env=~'{self.env}'," \
               f"instance=~'{self.instance}'}}"
        self.basic.append({
            "name": "broker_qps", "name_cn": "消费消息数量/s",
            "value": self.unified_job(*self.query(expr))}
        )

    def message_accumulation(self):
        """消息堆积量"""
        expr = f"rocketmq_message_accumulation{{env=~'{self.env}'," \
               f"instance=~'{self.instance}'}}"
        self.basic.append({
            "name": "message_accumulation", "name_cn": "消息堆积量",
            "value": self.unified_job(*self.query(expr))}
        )

    def salt_json(self):
        try:
            self._obj.salt_module_update()
            ret = self._obj.fun(self.instance, "rocketmq_check.main")
            if ret and ret[0]:
                ret = json.loads(ret[1])
            else:
                ret = {}
        except Exception:
            ret = {}

        self.ret['cpu_usage'] = ret.get('cpu_usage', '-')
        self.ret['mem_usage'] = ret.get('mem_usage', '-')
        self.ret['run_time'] = ret.get('run_time', '-')
        self.ret['log_level'] = ret.get('log_level', '-')
        self.basic.append({"name": "max_memory", "name_cn": "最大内存",
                           "value": ret.get('max_memory', '-')})

    def run(self):
        """统一执行实例方法"""
        # target = ['service_status', 'run_time', 'cpu_usage', 'mem_usage',
        #           'broker_tps', 'broker_qps', 'message_accumulation',
        #           'salt_json']
        target = ['service_status', 'run_time', 'cpu_usage', 'mem_usage']
        for t in target:
            if getattr(self, t):
                getattr(self, t)()
