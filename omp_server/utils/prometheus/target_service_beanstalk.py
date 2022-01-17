# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: lingyang guo
# CreateDate: 2021/12/15 8:00 下午
# Description:
from utils.plugin.salt_client import SaltClient
from utils.prometheus.prometheus import Prometheus


class ServiceBeanstalkCrawl(Prometheus):
    """
    查询 prometheus beanstalk 指标
    """

    def __init__(self, env, instance):
        self.ret = {}
        self.basic = []
        self.env = env  # 环境
        self.instance = instance  # 主机ip
        self._obj = SaltClient()
        self.metric_num = 18
        self.service_name = "beanstalk"
        Prometheus.__init__(self)

    def service_status(self):
        """运行状态"""
        expr = f"probe_success{{env='{self.env}', instance='{self.instance}', " \
               f"app='{self.service_name}'}}"
        self.ret['service_status'] = self.unified_job(*self.query(expr))

    def run_time(self):
        """beanstalk 运行时间"""
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
        """beanstalk cpu使用率"""
        expr = f"service_process_cpu_percent{{instance='{self.instance}',app='{self.service_name}'}}"
        val = self.unified_job(*self.query(expr))
        val = round(float(val), 4) if val else '-'
        self.ret['cpu_usage'] = f"{val}%"

    def mem_usage(self):
        """beanstalk 内存使用率"""
        expr = f"service_process_memory_percent{{instance='{self.instance}',app='{self.service_name}'}}"
        val = self.unified_job(*self.query(expr))
        val = round(float(val), 4) if val else '-'
        self.ret['mem_usage'] = f"{val}%"

    def total_connections(self):
        expr = f"total_connections{{job='beanstalkExporter',env='{self.env}',instance='{self.instance}'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["total_connections"] = val

        self.basic.append({
            "name": "total_connections",
            "name_cn": "总连接数",
            "value": val
        })

    def total_jobs(self):
        expr = f"total_jobs{{env='{self.env}',instance='{self.instance}',job='beanstalkExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["total_jobs"] = val

        self.basic.append({
            "name": "total_jobs",
            "name_cn": "总任务数",
            "value": val
        })

    def buried_jobs(self):
        expr = f"current_jobs_buried{{env='{self.env}',instance='{self.instance}',job='beanstalkExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["buried_jobs"] = val

        self.basic.append({
            "name": "buried_jobs",
            "name_cn": "buried job数",
            "value": val
        })

    def delayed_jobs(self):
        expr = f"current_jobs_delayed{{env='{self.env}',instance='{self.instance}',job='beanstalkExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["delayed_jobs"] = val

        self.basic.append({
            "name": "delayed_jobs",
            "name_cn": "延迟的job数",
            "value": val
        })

    def timeout_job_num(self):
        expr = f"job_timeouts{{env='{self.env}',instance='{self.instance}',job='beanstalkExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["timeout_job_num"] = val

        self.basic.append({
            "name": "timeout_job_num",
            "name_cn": "超时的job数",
            "value": val
        })

    def stats_cmd_num(self):
        expr = f"cmd_stats{{env='{self.env}',instance='{self.instance}',job='beanstalkExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["stats_cmd_num"] = val

        self.basic.append({
            "name": "stats_cmd_num",
            "name_cn": "stats命令数",
            "value": val
        })

    def reverse_cmd_num(self):
        expr = f"cmd_reserve{{env='{self.env}',instance='{self.instance}',job='beanstalkExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["reverse_cmd_num"] = val

        self.basic.append({
            "name": "reverse_cmd_num",
            "name_cn": "reverse命令数",
            "value": val
        })

    def release_cmd_num(self):
        expr = f"cmd_release{{env='{self.env}',instance='{self.instance}',job='beanstalkExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["release_cmd_num"] = val

        self.basic.append({
            "name": "release_cmd_num",
            "name_cn": "release命令数",
            "value": val
        })

    def put_cmd_num(self):
        expr = f"cmd_put{{env='{self.env}',instance='{self.instance}',job='beanstalkExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["put_cmd_num"] = val

        self.basic.append({
            "name": "put_cmd_num",
            "name_cn": "put命令数",
            "value": val
        })

    def peek_cmd_num(self):
        expr = f"cmd_peek{{env='{self.env}',instance='{self.instance}',job='beanstalkExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["peek_cmd_num"] = val

        self.basic.append({
            "name": "peek_cmd_num",
            "name_cn": "peak命令数",
            "value": val
        })

    def kick_cmd_num(self):
        expr = f"cmd_kick{{env='{self.env}',instance='{self.instance}',job='beanstalkExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["kick_cmd_num"] = val

        self.basic.append({
            "name": "kick_cmd_num",
            "name_cn": "kick命令数",
            "value": val
        })

    def ignore_cmd_num(self):
        expr = f"cmd_ignore{{env='{self.env}',instance='{self.instance}',job='beanstalkExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["ignore_cmd_num"] = val

        self.basic.append({
            "name": "ignore_cmd_num",
            "name_cn": "ignore命令数",
            "value": val
        })

    def delete_cmd_num(self):
        expr = f"cmd_delete{{env='{self.env}',instance='{self.instance}',job='beanstalkExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["delete_cmd_num"] = val

        self.basic.append({
            "name": "delete_cmd_num",
            "name_cn": "delete命令数",
            "value": val
        })

    def bury_cmd_num(self):
        expr = f"cmd_bury{{env='{self.env}',instance='{self.instance}',job='beanstalkExporter'}}"
        val = self.unified_job(*self.query(expr))
        val = val if val else 0
        self.ret["bury_cmd_num"] = val

        self.basic.append({
            "name": "bury_cmd_num",
            "name_cn": "bury命令数",
            "value": val
        })

    def run(self):
        """统一执行实例方法"""
        target = ['service_status', 'run_time', 'cpu_usage', 'mem_usage',
                  'total_connections', 'total_jobs', 'buried_jobs', 'delayed_jobs', 'timeout_job_num', 'stats_cmd_num',
                  'reverse_cmd_num', 'release_cmd_num', 'put_cmd_num', 'peek_cmd_num', 'kick_cmd_num', 'ignore_cmd_num',
                  'delete_cmd_num', 'bury_cmd_num']
        for t in target:
            if getattr(self, t):
                getattr(self, t)()
