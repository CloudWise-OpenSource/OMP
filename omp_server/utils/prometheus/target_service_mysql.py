# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/10/21 5:11 下午
# Description:
import json
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
        self.metric_num = 11
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

    def run_status(self):
        """运行状态"""
        expr = f"up{{env='{self.env}', instance='{self.instance}', " \
               f"job='mysqlExporter'}}"
        self.ret['run_status'] = self.unified_job(*self.query(expr))

    def run_time(self):
        """运行时间"""
        expr = f"mysql_global_status_uptime{{env='{self.env}'," \
               f"instance='{self.instance}'}}"
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

    def salt_json(self):
        try:
            self._obj.salt_module_update()
            ret = self._obj.fun(self.instance, "mysql_check.main")
            if ret and ret[0]:
                ret = json.loads(ret[1])
            else:
                ret = {}
        except Exception:
            ret = {}

        self.ret['cpu_usage'] = ret.get('cpu_usage', '-')
        self.ret['mem_usage'] = ret.get('mem_usage', '-')
        self.ret['run_time'] = ret.get('run_time', '-')

    def run(self):
        """统一执行实例方法"""
        target = ['run_status', 'run_time', 'slow_query', 'conn_num',
                  'max_connections', 'threads_running', 'qps', 'backup_status',
                  'salt_json']
        for t in target:
            if getattr(self, t):
                getattr(self, t)()


if __name__ == '__main__':
    h = ServiceMysqlCrawl(env='demo', instance='10.0.9.60')
    h.run()
    print(h.ret)
