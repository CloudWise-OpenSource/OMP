# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/10/21 5:11 下午
# Description:
from utils.prometheus.prometheus import Prometheus


class ServiceMysqlCrawl(Prometheus):
    """
    查询 prometheus mysql 指标
    """
    def __init__(self, env, instance):
        self.ret = {}
        self.env = env  # 环境
        self.tag_total_num = 0      # 总指标数
        self.tag_error_num = 0      # 异常指标数
        self.instance = instance    # 主机ip

    def unified_job(self, is_success, ret, msg):
        """
        实例方法 返回值统一处理
        :ret: 返回值
        :msg: 返回值描述
        :is_success: 请求是否成功
        """
        self.tag_total_num += 1         # 统计总指标数
        if is_success:
            return ret.get('result')[0].get('value')[1]
        else:
            self.tag_error_num += 1     # 统计异常指标数
            return msg

    def run_status(self):
        """运行状态"""
        expr = f"up{{env='{self.env}', instance='{self.instance}', " \
               f"job='mysqlExporter'}}"
        self.ret['run_status'] = self.unified_job(*self.query(expr))

    def run_time(self):
        """运行时间"""
        expr = f"mysql_global_status_uptime{{env='{self.env}'," \
               f"instance='{self.instance}'}}"
        self.ret['run_time'] = self.unified_job(*self.query(expr))

    def slow_queries(self):
        """慢查询"""
        expr = f"rate(mysql_global_status_slow_queries[5m])"
        self.ret['run_time'] = self.unified_job(*self.query(expr))

    def threads_connected(self):
        """当前连接数量"""
        expr = f"rate(mysql_global_status_threads_connected[5m])"
        self.ret['run_time'] = self.unified_job(*self.query(expr))

    def max_connections(self):
        """最大连接数"""
        expr = f"mysql_global_variables_max_connections"
        self.ret['run_time'] = self.unified_job(*self.query(expr))

    def threads_running(self):
        """活跃连接数量"""
        expr = f"mysql_global_status_threads_running"
        self.ret['run_time'] = self.unified_job(*self.query(expr))

    def aborted_connects(self):
        """累计所有的连接数"""
        expr = f"mysql_global_status_aborted_connects"
        self.ret['run_time'] = self.unified_job(*self.query(expr))

    def qps(self):
        """qps"""
        expr = f"rate(mysql_global_status_questions[5m])"
        self.ret['run_time'] = self.unified_job(*self.query(expr))

    def slave_sql_running(self):
        """备份状态"""
        expr = f"mysql_slave_status_slave_sql_running"
        self.ret['run_time'] = self.unified_job(*self.query(expr))

    def run(self, target):
        """统一执行实例方法"""
        for t in target:
            if getattr(self, t):
                getattr(self, t)()


if __name__ == '__main__':
    h = ServiceMysqlCrawl(env='demo', instance='10.0.2.113')
    h.run(['run_time', 'rate_cpu', 'rate_memory', 'rate_max_disk',
           'rate_exchange_disk', 'avg_load',
           'total_file_descriptor', 'rate_io_wait', 'network_bytes_total',
           'disk_io'])
    print(h.ret)
