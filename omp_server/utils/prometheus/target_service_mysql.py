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
        self.env = env              # 环境
        self.tag_error_num = 0      # 异常指标数
        self.instance = instance    # 主机ip
        self._obj = SaltClient()
        Prometheus.__init__(self)

    def unified_job(self, is_success, ret, msg):
        """
        实例方法 返回值统一处理
        :ret: 返回值
        :msg: 返回值描述
        :is_success: 请求是否成功
        """
        if is_success:
            if ret.get('result'):
                return ret['result'][0].get('value')[1]
            else:
                return ''
        else:
            self.tag_error_num += 1  # 统计异常指标数
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
        _ = self.unified_job(*self.query(expr))
        _ = float(_) if _ else 0
        minutes, seconds = divmod(_, 60)
        hours, minutes = divmod(minutes, 60)
        self.ret['run_time'] = f"{hours}小时{minutes}分钟{seconds}秒"

    def slow_queries(self):
        """慢查询"""
        expr = f"rate(mysql_global_status_slow_queries[5m])"
        self.ret['slow_queries'] = self.unified_job(*self.query(expr))

    def threads_connected(self):
        """当前连接数量"""
        expr = f"rate(mysql_global_status_threads_connected[5m])"
        self.ret['threads_connected'] = self.unified_job(*self.query(expr))

    def max_connections(self):
        """最大连接数"""
        expr = f"mysql_global_variables_max_connections"
        self.ret['max_connections'] = self.unified_job(*self.query(expr))

    def threads_running(self):
        """活跃连接数量"""
        expr = f"mysql_global_status_threads_running"
        self.ret['threads_running'] = self.unified_job(*self.query(expr))

    def aborted_connects(self):
        """累计所有的连接数"""
        expr = f"mysql_global_status_aborted_connects"
        self.ret['aborted_connects'] = self.unified_job(*self.query(expr))

    def qps(self):
        """qps"""
        expr = f"rate(mysql_global_status_questions[5m])"
        self.ret['qps'] = self.unified_job(*self.query(expr))

    def slave_sql_running(self):
        """备份状态"""
        expr = f"mysql_global_status_slave_open_temp_tables"
        self.ret['slave_sql_running'] = self.unified_job(*self.query(expr))

    def salt_json(self):
        try:
            self._obj.salt_module_update()
            ret = self._obj.fun(self.instance, "mysql_check.main")
            if ret and ret[0]:
                self.ret['_s'] = json.loads(ret[1])
            else:
                self.ret['_s'] = {}
        except:
            self.ret['_s'] = {}

    def run(self):
        """统一执行实例方法"""
        target = ['run_status', 'run_time', 'slow_queries',
                  'threads_connected', 'max_connections',
                  'threads_running', 'aborted_connects', 'qps',
                  'slave_sql_running', 'salt_json']
        for t in target:
            if getattr(self, t):
                getattr(self, t)()


if __name__ == '__main__':
    h = ServiceMysqlCrawl(env='demo', instance='10.0.9.60')
    h.run()
    print(h.ret)
