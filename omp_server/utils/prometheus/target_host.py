# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/10/14 6:26 下午
# Description: 主机指标
from prometheus import Prometheus


class HostCrawl(Prometheus):
    """
    查询 prometheus 主机指标
    """
    # 类的实例方法名，为的是统一执行实例方法及对可查询指标进行验证
    target = ['run_time', 'cpu_num', 'total_memory', 'rate_cpu', 'rate_io_wait', 'rate_memory', 'rate_max_disk',
              'rate_exchange_disk', 'rate_cpu_io_wait', ]

    def __init__(self, env='default', instance='10.0.9.158'):
        self.ret = {}
        self.env = env  # 环境
        self.instance = instance    # 主机ip

    def run_time(self):
        """运行时间"""
        expr = 'avg(time() - node_boot_time_seconds{env="%s",instance=~"%s"})'
        expr = expr % (self.env, self.instance)
        self.ret['run_time'] = self.query(expr).get('result')[0].get('value')[1]

    def cpu_num(self):
        """cpu 核数"""
        expr = 'count(node_cpu_seconds_total{env="%s",instance=~"%s", mode="system"})'
        expr = expr % (self.env, self.instance)
        self.ret['cpu_num'] = self.query(expr).get('result')[0].get('value')[1]

    def total_memory(self):
        """总内存"""
        expr = 'sum(node_memory_MemTotal_bytes{env="%s",instance=~"%s"})'
        expr = expr % (self.env, self.instance)
        self.ret['total_memory'] = self.query(expr).get('result')[0].get('value')[1]

    def rate_cpu(self):
        """总cpu使用率"""
        expr = '100 - (avg(rate(node_cpu_seconds_total{env="%s",instance=~"%s",mode="idle"}[5m])) * 100)'
        expr = expr % (self.env, self.instance)
        self.ret['rate_cpu'] = self.query(expr).get('result')[0].get('value')[1]

    def rate_io_wait(self):
        """IO wait使用率"""
        expr = 'avg(rate(node_cpu_seconds_total{env="%s",instance=~"%s",mode="iowait"}[5m])) * 100'
        expr = expr % (self.env, self.instance)
        self.ret['rate_io_wait'] = self.query(expr).get('result')[0].get('value')[1]

    def rate_memory(self):
        """内存使用率"""
        expr = '(1 - (node_memory_MemAvailable_bytes{env="%s",instance=~"%s"} / ' \
               '(node_memory_MemTotal_bytes{env="%s",instance=~"%s"})))* 100'
        expr = expr % (self.env, self.instance, self.env, self.instance)
        self.ret['rate_memory'] = self.query(expr).get('result')[0].get('value')[1]

    def rate_max_disk(self):
        """最大分区 /data 使用率"""
        expr = '(node_filesystem_size_bytes{{env="{env}",instance=~"{instance}",fstype=~"ext.*|xfs",' \
               'mountpoint="\\/data"}}-node_filesystem_free_bytes{{env="{env}",instance=~"{instance}",' \
               'fstype=~"ext.*|xfs",mountpoint="\\/data"}})*100 /(node_filesystem_avail_bytes {{env="{env}",' \
               'instance=~"{instance}",fstype=~"ext.*|xfs",mountpoint="\\/data"}}+' \
               '(node_filesystem_size_bytes{{env="{env}",instance=~"{instance}",fstype=~"ext.*|xfs",' \
               'mountpoint="\\/data"}}-node_filesystem_free_bytes{{env="{env}",instance=~"{instance}",' \
               'fstype=~"ext.*|xfs",mountpoint="\\/data"}}))'
        expr = expr.format(env=self.env, instance=self.instance)
        ret = self.query(expr)
        self.ret['rate_max_disk'] = ret.get('result')[0].get('value')[1] if ret else ''

    def rate_exchange_disk(self):
        """交换分区使用率"""
        expr = '(1 - ((node_memory_SwapFree_bytes{env="%s",instance=~"%s"} + 1)/ (node_memory_SwapTotal_bytes' \
               '{env="%s",instance=~"%s"} + 1))) * 100'
        expr = expr % (self.env, self.instance, self.env, self.instance)
        ret = self.query(expr)
        self.ret['rate_max_disk'] = ret.get('result')[0].get('value')[1] if ret else ''

    def rate_cpu_io_wait(self):
        """cpu io wait"""
        expr = 'avg(rate(node_cpu_seconds_total{instance=~"%s",mode="iowait"}[$interval])) * 100'
        expr = expr % (self.env, self.instance, self.env, self.instance)
        self.ret['rate_cpu_io_wait'] = self.query(expr).get('result')[0].get('value')[1]

    def rate_residue_node(self):
        """剩余节点数"""
        expr = 'avg(node_filesystem_files_free{instance=~"%s",mountpoint="/data",fstype=~"ext.?|xfs"})'
        expr = expr % (self.env, self.instance, self.env, self.instance)
        self.ret['rate_residue_node'] = self.query(expr).get('result')[0].get('value')[1]

    def total_file_descriptor(self):
        """总文件描述符"""
        expr = 'avg(node_filefd_maximum{instance=~"%s"})' % (self.instance,)
        self.ret['total_file_descriptor'] = self.query(expr).get('result')[0].get('value')[1]

    def avg_load(self):
        """系统平均负载"""
        # 1分钟负载
        expr = 'node_load1{env="%s",instance=~"%s"}' % (self.env, self.instance)
        self.ret['load'] = {'load1': self.query(expr).get('result')[0].get('value')[1]}
        # 5分钟负载
        expr = 'node_load5{env="%s",instance=~"%s"}' % (self.env, self.instance)
        self.ret['load']['load5'] = self.query(expr).get('result')[0].get('value')[1]
        # 15分钟负载
        expr = 'node_load15{env="%s",instance=~"%s"}' % (self.env, self.instance)
        self.ret['load']['load15'] = self.query(expr).get('result')[0].get('value')[1]

    def network_bytes_total(self):
        """网络带宽使用"""
        # eth0 下载
        expr = 'sum(rate(node_network_receive_bytes_total{env="%s",instance=~"%s",device=~"eth0"}[2m])*8/1024)'
        expr = expr % (self.env, self.instance)
        self.ret['network_bytes_total'] = {'receive': self.query(expr).get('result')[0].get('value')[1]}
        # eth0 上传
        expr = 'sum(rate(node_network_transmit_bytes_total{env="%s",instance=~"%s",device=~"eth0"}[2m])*8/1024)'
        expr = expr % (self.env, self.instance)
        self.ret['network_bytes_total']['transmit'] = self.query(expr).get('result')[0].get('value')[1]

    def disk_io(self):
        """磁盘io"""
        # 读
        expr = 'sum(rate(node_disk_read_bytes_total{env="%s",instance=~"%s"}[2m]))'
        expr = expr % (self.env, self.instance)
        self.ret['disk_io'] = {'read': self.query(expr).get('result')[0].get('value')[1]}
        # 写
        expr = 'sum(rate(node_disk_written_bytes_total{env="%s",instance=~"%s"}[2m]))'
        expr = expr % (self.env, self.instance)
        self.ret['disk_io']['write'] = self.query(expr).get('result')[0].get('value')[1]

    def run(self, target):
        """统一执行实例方法"""
        for t in target:
            if getattr(self, t):
                getattr(self, t)()


if __name__ == '__main__':
    h = HostCrawl()
    h.run(['rate_cpu', 'rate_memory', 'rate_max_disk', 'rate_exchange_disk', 'run_time', 'avg_load',
           'total_file_descriptor', 'rate_io_wait', 'network_bytes_total', 'disk_io'])
    print(h.ret)
