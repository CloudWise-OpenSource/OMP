# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/10/21 5:11 下午
# Description:
from utils.prometheus.prometheus import Prometheus
from utils.plugin.salt_client import SaltClient


class ServiceMysqlCrawl(Prometheus):
    """
    查询 prometheus mysql 指标
    """

    def __init__(self, env, instance):
        self.ret = {}
        self.basic = []
        self.env = env  # 环境
        self.instance = instance  # 主机ip
        self._obj = SaltClient()
        self.metric_num = 10
        self.service_name = "mysql"
        Prometheus.__init__(self)

    def service_status(self):
        """运行状态"""
        expr = f"probe_success{{env='{self.env}', instance='{self.instance}', " \
               f"app='{self.service_name}'}}"
        self.ret['service_status'] = self.unified_job(*self.query(expr))

    def run_time(self):
        """mysql 运行时间"""
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
        """mysql cpu使用率"""
        expr = f"service_process_cpu_percent{{instance='{self.instance}',app='{self.service_name}'}}"
        val = self.unified_job(*self.query(expr))
        val = round(float(val), 4) if val else '-'
        self.ret['cpu_usage'] = f"{val}%"

    def mem_usage(self):
        """mysql 内存使用率"""
        expr = f"service_process_memory_percent{{instance='{self.instance}',app='{self.service_name}'}}"
        val = self.unified_job(*self.query(expr))
        val = round(float(val), 4) if val else '-'
        self.ret['mem_usage'] = f"{val}%"

    def slow_query(self):
        """慢查询"""
        expr = "rate(mysql_global_status_slow_queries[5m])"
        self.basic.append({"name": "slow_query", "name_cn": "慢查询",
                           "value": self.unified_job(*self.query(expr))})

    def conn_num(self):
        """当前连接数量"""
        expr = "rate(mysql_global_status_threads_connected[5m])"
        self.basic.append({"name": "conn_num", "name_cn": "连接数量",
                           "value": self.unified_job(*self.query(expr))})

    def max_connections(self):
        """最大连接数"""
        expr = "mysql_global_variables_max_connections"
        self.basic.append({"name": "max_connections", "name_cn": "最大连接数",
                           "value": self.unified_job(*self.query(expr))})

    def threads_running(self):
        """活跃连接数量"""
        expr = "mysql_global_status_threads_running"
        self.basic.append({"name": "threads_running", "name_cn": "活跃连接数",
                           "value": self.unified_job(*self.query(expr))})

    def qps(self):
        """qps"""
        expr = "rate(mysql_global_status_questions[5m])"
        _ = self.unified_job(*self.query(expr))
        _ = round(float(_), 2) if _ else 0
        self.basic.append({"name": "qps", "name_cn": "qps", "value": _})

    def backup_status(self):
        """备份状态"""
        expr = "mysql_global_status_slave_open_temp_tables"
        self.basic.append({"name": "backup_status", "name_cn": "数据同步状态",
                           "value": self.unified_job(*self.query(expr))})

    def run(self):
        """统一执行实例方法"""
        target = ['service_status', 'run_time', 'cpu_usage', 'mem_usage', 'slow_query', 'conn_num',
                  'max_connections', 'threads_running', 'qps', 'backup_status']
        for t in target:
            if getattr(self, t):
                getattr(self, t)()


if __name__ == '__main__':
    h = ServiceMysqlCrawl(env='demo', instance='10.0.9.60')
    h.run()
    print(h.ret)
