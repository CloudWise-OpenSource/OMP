# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/10/14 6:26 下午
# Description: 主机指标
from utils.prometheus.prometheus import Prometheus


class HostCrawl(Prometheus):
    """
    查询 prometheus 主机指标
    """
    # 类的实例方法名，为的是统一执行实例方法及对可查询指标进行验证
    target = ['run_time', 'cpu_num', 'total_memory', 'rate_cpu', 'rate_io_wait',
              'rate_memory', 'rate_max_disk', 'rate_exchange_disk',
              'rate_cpu_io_wait', ]

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

    def run_time(self):
        """运行时间"""
        expr = f"avg(time() - node_boot_time_seconds{{env='{self.env}'," \
               f"instance=~'{self.instance}'}})"
        self.ret['run_time'] = self.unified_job(*self.query(expr))

    def cpu_num(self):
        """cpu 核数"""
        expr = f"count(node_cpu_seconds_total{{env='{self.env}'," \
               f"instance=~'{self.instance}', mode='system'}})"
        self.ret['cpu_num'] = self.unified_job(*self.query(expr))

    def total_memory(self):
        """总内存"""
        expr = f"sum(node_memory_MemTotal_bytes{{env='{self.env}'," \
               f"instance=~'{self.instance}'}})"
        self.ret['total_memory'] = self.unified_job(*self.query(expr))

    def rate_cpu(self):
        """总cpu使用率"""
        expr = f"100 - (avg(rate(node_cpu_seconds_total{{env='{self.env}'," \
               f"instance=~'{self.instance}'," \
               f"mode='idle'}}[5m])) * 100)"
        self.ret['rate_cpu'] = self.unified_job(*self.query(expr))

    def rate_io_wait(self):
        """IO wait使用率"""
        expr = f"avg(rate(node_cpu_seconds_total{{env='{self.env}'," \
               f"instance=~'{self.instance}',mode='iowait'}}[5m])) * 100"
        self.ret['rate_io_wait'] = self.unified_job(*self.query(expr))

    def rate_memory(self):
        """内存使用率"""
        expr = f"(1 - (node_memory_MemAvailable_bytes{{env='{self.env}'," \
               f"instance=~'{self.instance}'}} / " \
               f"(node_memory_MemTotal_bytes{{env='{self.env}'," \
               f"instance=~'{self.instance}'}})))* 100"
        self.ret['rate_memory'] = self.unified_job(*self.query(expr))

    def rate_max_disk(self):
        """最大分区 /data 使用率"""
        expr = f"(node_filesystem_size_bytes{{env='{self.env}'," \
               f"instance=~'{self.instance}',fstype=~'ext.*|xfs'," \
               f"mountpoint='/data'}}-" \
               f"node_filesystem_free_bytes{{env='{self.env}'," \
               f"instance=~'{self.instance}'," \
               f"fstype=~'ext.*|xfs',mountpoint='/data'}})*100 /" \
               f"(node_filesystem_avail_bytes{{env='{self.env}'," \
               f"instance=~'{self.instance}',fstype=~'ext.*|xfs'," \
               f"mountpoint='/data'}}+" \
               f"(node_filesystem_size_bytes{{env='{self.env}'," \
               f"instance=~'{self.instance}',fstype=~'ext.*|xfs'," \
               f"mountpoint='/data'}}-" \
               f"node_filesystem_free_bytes{{env='{self.env}'," \
               f"instance=~'{self.instance}'," \
               f"fstype=~'ext.*|xfs',mountpoint='/data'}}))"
        self.ret['rate_max_disk'] = self.unified_job(*self.query(expr))

    def rate_exchange_disk(self):
        """交换分区使用率"""
        expr = f"(1 - (node_memory_SwapFree_bytes{{env='{self.env}'," \
               f"instance=~'{self.instance}'}} / " \
               f"node_memory_SwapTotal_bytes{{env='{self.env}'," \
               f"instance=~'{self.instance}'}})) * 100"
        self.ret['rate_exchange_disk'] = self.unified_job(*self.query(expr))

    def rate_cpu_io_wait(self):
        """cpu io wait"""
        expr = f"avg(rate(node_cpu_seconds_total" \
               f"{{instance=~'{self.instance}',mode='iowait'}}[5m])) * 100"
        self.ret['rate_cpu_io_wait'] = self.unified_job(*self.query(expr))

    def rate_residue_node(self):
        """剩余节点数"""
        expr = f"avg(node_filesystem_files_free{{instance=~'{self.instance}'," \
               f"mountpoint='/data',fstype=~'ext.?|xfs'}})"
        self.ret['rate_residue_node'] = self.unified_job(*self.query(expr))

    def total_file_descriptor(self):
        """总文件描述符"""
        expr = f"avg(node_filefd_maximum{{instance=~'{self.instance}'}})"
        self.ret['total_file_descriptor'] = self.unified_job(*self.query(expr))

    def avg_load(self):
        """系统平均负载"""
        # 1分钟负载
        expr = f"node_load1{{env='{self.env}',instance=~'{self.instance}'}}"
        self.ret['load'] = {'load1': self.unified_job(*self.query(expr))}
        # 5分钟负载
        expr = f"node_load5{{env='{self.env}',instance=~'{self.instance}'}}"
        self.ret['load']['load5'] = self.unified_job(*self.query(expr))
        # 15分钟负载
        expr = f"node_load15{{env='{self.env}',instance=~'{self.instance}'}}"
        self.ret['load']['load15'] = self.unified_job(*self.query(expr))

    def network_bytes_total(self):
        """网络带宽使用"""
        # eth0 下载
        expr = f"sum(rate(node_network_receive_bytes_total{{env='{self.env}'," \
               f"instance=~'{self.instance}',device=~'eth0'}}[2m])*8/1024)"
        self.ret['network_bytes_total'] = \
            {'receive': self.unified_job(*self.query(expr))}
        # eth0 上传
        expr = f"sum(rate(node_network_transmit_bytes_total" \
               f"{{env='{self.env}',instance=~'{self.instance}'," \
               f"device=~'eth0'}}[2m])*8/1024)"
        self.ret['network_bytes_total']['transmit'] = \
            self.unified_job(*self.query(expr))

    def disk_io(self):
        """磁盘io"""
        # 读
        expr = f"sum(rate(node_disk_read_bytes_total{{env='{self.env}'," \
               f"instance=~'{self.instance}'}}[2m]))"
        self.ret['disk_io'] = {'read': self.unified_job(*self.query(expr))}
        # 写
        expr = f"sum(rate(node_disk_written_bytes_total{{env='{self.env}'," \
               f"instance=~'{self.instance}'}}[2m]))"
        self.ret['disk_io']['write'] = self.unified_job(*self.query(expr))

    def run(self, target):
        """统一执行实例方法"""
        for t in target:
            if getattr(self, t):
                getattr(self, t)()


if __name__ == '__main__':
    h = HostCrawl(env='demo', instance='10.0.2.113')
    h.run(['run_time', 'rate_cpu', 'rate_memory', 'rate_max_disk',
           'rate_exchange_disk', 'avg_load',
           'total_file_descriptor', 'rate_io_wait', 'network_bytes_total',
           'disk_io'])
    print(h.ret)
