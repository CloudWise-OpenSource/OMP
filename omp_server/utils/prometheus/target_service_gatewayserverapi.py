# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/11/8 8:00 下午
# Description:
from utils.prometheus.prometheus import Prometheus


class GatewayServerApi(Prometheus):
    """
    查询 prometheus GatewayServerApi 指标
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
        expr = f"probe_success{{env=~'{self.env}'," \
               f"instance=~'{self.instance}',app=~'gatewayServerApi'," \
               f"app!='node'}}"
        self.ret['service_status'] = self.unified_job(*self.query(expr))

    def run_time(self):
        """运行时间"""
        expr = f"process_uptime_seconds{{env=~'{self.env}'," \
               f"instance=~'{self.instance}',job=~'gatewayServerApiExporter'}}"
        _ = self.unified_job(*self.query(expr))
        _ = float(_) if _ else 0
        minutes, seconds = divmod(_, 60)
        hours, minutes = divmod(minutes, 60)
        self.ret['run_time'] = f"{int(hours)}小时{int(minutes)}分钟{int(seconds)}秒"

    def cpu_usage(self):
        """cpu使用率"""
        expr = f"system_cpu_usage{{env=~'{self.env}'," \
               f"instance=~'{self.instance}', " \
               f"job='gatewayServerApiExporter'}} * 100"
        val = self.unified_job(*self.query(expr))
        val = round(float(val), 2) if val else 0
        self.ret['cpu_usage'] = f"{val}%"

    def mem_usage(self):
        """内存使用率"""
        expr = f"sum(jvm_memory_used_bytes{{area='heap', env='{self.env}'," \
               f"instance=~'{self.instance}'," \
               f"job='gatewayServerApiExporter'}}) / " \
               f"sum(jvm_memory_max_bytes{{area='heap', env=~'{self.env}'," \
               f"instance=~'{self.instance}'," \
               f"job='gatewayServerApiExporter'}}) * 100"
        val = self.unified_job(*self.query(expr))
        val = round(float(val), 2) if val else 0
        self.ret['mem_usage'] = f"{val}%"

    def thread_num(self):
        """进程数量"""
        expr = f"jvm_threads_daemon_threads{{env=~'{self.env}'," \
               f"instance=~'{self.instance}',job=~'gatewayServerApiExporter'}}"
        self.basic.append({
            "name": "thread_num", "name_cn": "进程数量",
            "value": self.unified_job(*self.query(expr))}
        )

    def load_average_1m(self):
        """系统一分钟负载占用情况"""
        expr = f"system_load_average_1m{{env=~'{self.env}'," \
               f"instance=~'{self.instance}',job=~'gatewayServerApiExporter'}}"
        self.basic.append({
            "name": "load_average_1m", "name_cn": "系统一分钟负载占用情况",
            "value": self.unified_job(*self.query(expr))}
        )

    def tomcat_sessions(self):
        """Tomcat当前活跃session数量"""
        expr = f"tomcat_sessions_active_current_sessions{{env=~'{self.env}'," \
               f"instance=~'{self.instance}',job=~'gatewayServerApiExporter'}}"
        self.basic.append({
            "name": "tomcat_sessions", "name_cn": "Tomcat当前活跃session数量",
            "value": self.unified_job(*self.query(expr))}
        )

    def files_max_files(self):
        """可打开的最大文件描述符数量"""
        expr = f"process_files_max_files{{env=~'{self.env}'," \
               f"instance=~'{self.instance}',job=~'gatewayServerApiExporter'}}"
        self.basic.append({
            "name": "files_max_files", "name_cn": "可打开的最大文件描述符数量",
            "value": self.unified_job(*self.query(expr))}
        )

    def files_open_files(self):
        """当前打开的最大文件描述符数量"""
        expr = f"process_files_open_files{{env=~'{self.env}'," \
               f"instance=~'{self.instance}',job=~'gatewayServerApiExporter'}}"
        self.basic.append({
            "name": "files_open_files", "name_cn": "当前打开的最大文件描述符数量",
            "value": self.unified_job(*self.query(expr))}
        )

    def run(self):
        """统一执行实例方法"""
        target = ['service_status', 'run_time', 'cpu_usage', 'mem_usage',
                  'thread_num', 'load_average_1m', 'tomcat_sessions',
                  'files_max_files', 'files_open_files']
        for t in target:
            if getattr(self, t):
                getattr(self, t)()
