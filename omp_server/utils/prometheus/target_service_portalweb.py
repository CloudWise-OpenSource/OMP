# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/11/8 8:00 下午
# Description:
from utils.prometheus.prometheus import Prometheus


class ServicePortalWebCrawl(Prometheus):
    """
    查询 prometheus PortalWeb 指标
    """
    def __init__(self, env, instance):
        self.ret = {}
        self.basic = []
        self.env = env              # 环境
        self.instance = instance    # 主机ip
        Prometheus.__init__(self)

    @staticmethod
    def unified_job(is_success, ret, msg):
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
            return ''

    def service_status(self):
        """运行状态"""
        self.ret['service_status'] = '-'

    def run_time(self):
        """运行时间"""
        self.ret['run_time'] = '-'

    def cpu_usage(self):
        """cpu使用率"""
        self.ret['cpu_usage'] = "-"

    def mem_usage(self):
        """内存使用率"""
        self.ret['mem_usage'] = '-'

    def run(self):
        """统一执行实例方法"""
        target = ['service_status', 'run_time', 'cpu_usage', 'mem_usage']
        for t in target:
            if getattr(self, t):
                getattr(self, t)()
