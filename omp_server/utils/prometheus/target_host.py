# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/10/14 6:26 下午
# Description: 主机指标
import json
import logging

from utils.prometheus.prometheus import Prometheus
from utils.prometheus.utils import get_host_data_folder
from utils.plugin.salt_client import SaltClient

logger = logging.getLogger("server")


class HostCrawl(Prometheus):
    """
    查询 prometheus 主机指标
    """

    def __init__(self, env, instance):
        self.ret = {}
        self.env = env  # 环境
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
                return 0
        else:
            self.tag_error_num += 1     # 统计异常指标数
            return msg

    def run_status(self):
        """运行状态"""
        expr = f"round(up{{env='{self.env}', instance='{self.instance}', " \
               f"job='nodeExporter'}})"
        self.ret['run_status'] = self.unified_job(*self.query(expr))

    def run_time(self):
        """运行时间"""
        expr = f"avg(time() - node_boot_time_seconds{{env='{self.env}'," \
               f"instance=~'{self.instance}'}})"
        _ = self.unified_job(*self.query(expr))
        _ = float(_) if _ else 0
        minutes, seconds = divmod(_, 60)
        hours, minutes = divmod(minutes, 60)
        self.ret['run_time'] = f"{hours}小时{minutes}分钟{seconds}秒"

    # def cpu_num(self):
    #     """cpu 核数"""
    #     expr = f"count(node_cpu_seconds_total{{env='{self.env}'," \
    #            f"instance=~'{self.instance}', mode='system'}})"
    #     self.ret['cpu_num'] = self.unified_job(*self.query(expr))

    # def total_memory(self):
    #     """总内存"""
    #     expr = f"sum(node_memory_MemTotal_bytes{{env='{self.env}'," \
    #            f"instance=~'{self.instance}'}})"
    #     self.ret['total_memory'] = self.unified_job(*self.query(expr))

    def rate_cpu(self):
        """总cpu使用率"""
        expr = f"100 - (avg(rate(node_cpu_seconds_total" \
               f"{{env='{self.env}'," \
               f"instance=~'{self.instance}'," \
               f"mode='idle'}}[5m])) * 100)"
        self.ret['rate_cpu'] = \
            f"{round(float(self.unified_job(*self.query(expr))), 2)}%"

    def rate_io_wait(self):
        """IO wait使用率"""
        expr = f"avg(rate(node_cpu_seconds_total{{env='{self.env}'," \
               f"instance=~'{self.instance}',mode='iowait'}}[5m])) * 100"
        self.ret['rate_io_wait'] = \
            f"{round(float(self.unified_job(*self.query(expr))), 2)}%"

    def rate_memory(self):
        """内存使用率"""
        expr = f"(1 - (node_memory_MemAvailable_bytes" \
               f"{{env='{self.env}'," \
               f"instance=~'{self.instance}'}} / " \
               f"(node_memory_MemTotal_bytes{{env='{self.env}'," \
               f"instance=~'{self.instance}'}})))* 100"
        self.ret['rate_memory'] = \
            f"{round(float(self.unified_job(*self.query(expr))), 2)}%"

    def rate_max_disk(self):
        """根分区使用率"""
        expr = f"(node_filesystem_size_bytes{{env='{self.env}'," \
               f"instance=~'{self.instance}'," \
               f"fstype=~'ext.*|xfs',mountpoint='/'}} - " \
               f"node_filesystem_avail_bytes{{env='{self.env}'," \
               f"instance=~'{self.instance}'," \
               f"fstype=~'ext.*|xfs',mountpoint='/'}}) / " \
               f"node_filesystem_size_bytes{{env='{self.env}'," \
               f"instance=~'{self.instance}'," \
               f"fstype=~'ext.*|xfs',mountpoint='/'}} * 100"
        self.ret['rate_max_disk'] = \
            f"{round(float(self.unified_job(*self.query(expr))), 2)}%"

    def rate_data_disk(self):
        """数据分区使用率"""
        # 数据分区应该由主机表中的data_folder目录决定
        # 并协同disk信息判断出数据分区挂载点是哪个
        _data_path = get_host_data_folder(self.instance)
        if not _data_path:
            return "_"
        expr = f"(1-(node_filesystem_free_bytes{{env='{self.env}'," \
               f"instance=~'{self.instance}',mountpoint='{_data_path}', " \
               f"fstype=~'ext.*|xfs'}}" \
               f" / node_filesystem_size_bytes{{env='{self.env}'," \
               f"instance=~'{self.instance}',mountpoint='{_data_path}', " \
               f"fstype=~'ext.*|xfs'}}))" \
               f" * 100"
        _ = self.unified_job(*self.query(expr))
        self.ret['rate_data_disk'] = f"{round(float(_), 2)}%" if _ else '_'

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

    def rate_inode(self):
        """inode使用率"""
        expr = f"(1-node_filesystem_files_free{{fstype=~'xfs|ext4'," \
               f"mountpoint='/', env='{self.env}'," \
               f"instance=~'{self.instance}'}} / " \
               f"node_filesystem_files{{fstype=~'xfs|ext4',mountpoint='/', " \
               f"env='{self.env}',instance=~'{self.instance}'}})*100"
        self.ret['rate_inode'] = \
            f"{round(float(self.unified_job(*self.query(expr))), 2)}%"

    def total_file_descriptor(self):
        """总文件描述符"""
        expr = f"avg(node_filefd_maximum{{instance=~'{self.instance}'}})"
        self.ret['total_file_descriptor'] = self.unified_job(*self.query(expr))

    def avg_load(self):
        """系统平均负载"""
        # 1分钟负载
        expr = f"node_load1{{env='{self.env}',instance=~'{self.instance}'}}"
        load1 = self.unified_job(*self.query(expr))
        # 5分钟负载
        expr = f"node_load5{{env='{self.env}',instance=~'{self.instance}'}}"
        load5 = self.unified_job(*self.query(expr))
        # 15分钟负载
        expr = f"node_load15{{env='{self.env}',instance=~'{self.instance}'}}"
        load15 = self.unified_job(*self.query(expr))
        self.ret['load'] = f"{load1},{load5},{load15}"

    def network_bytes_total(self):
        """网络带宽使用"""
        # eth0 下载
        expr = f"sum(rate(node_network_receive_bytes_total{{env='{self.env}'," \
               f"instance=~'{self.instance}',device=~'eth0'}}[2m])*8/1024)"
        self.ret['network_bytes_total'] = {
            'receive': f"{round(float(self.unified_job(*self.query(expr))), 2)}"
                       f"kb/s"}
        # eth0 上传
        expr = f"sum(rate(node_network_transmit_bytes_total" \
               f"{{env='{self.env}',instance=~'{self.instance}'," \
               f"device=~'eth0'}}[2m])*8/1024)"
        self.ret['network_bytes_total']['transmit'] = {
            'receive': f"{round(float(self.unified_job(*self.query(expr))), 2)}"
                       f"kb/s"}

    def disk_io(self):
        """磁盘io"""
        # 读
        expr = f"sum(rate(node_disk_read_bytes_total{{env='{self.env}'," \
               f"instance=~'{self.instance}'}}[2m])) / 1024"
        self.ret['disk_io'] = \
            {'read': f"{round(float(self.unified_job(*self.query(expr))), 2)}"
                     f"kb/s"}
        # 写
        expr = f"sum(rate(node_disk_written_bytes_total" \
               f"{{env='{self.env}'," \
               f"instance=~'{self.instance}'}}[2m])) / 1024"
        self.ret['disk_io']['write'] = \
            f"{round(float(self.unified_job(*self.query(expr))), 2)}kb/s"

    def salt_json(self):
        try:
            self._obj.salt_module_update()
            ret = self._obj.fun(self.instance, "host_check.main")
            if ret and ret[0]:
                self.ret['_s'] = json.loads(ret[1])
            else:
                self.ret['_s'] = {}
        except Exception as e:
            logger.error(f"Salt host_check.main failed with error: {str(e)}")
            self.ret['_s'] = {}

    def run(self):
        """统一执行实例方法"""
        # target为实例方法，目的是统一执行实例方法并统一返回值
        target = ['rate_cpu', 'rate_memory', 'rate_max_disk',
                  'rate_data_disk', 'salt_json',
                  'run_time', 'avg_load', 'rate_inode',
                  'total_file_descriptor', 'rate_io_wait',
                  'network_bytes_total', 'disk_io', 'run_status']
        for t in target:
            if getattr(self, t):
                getattr(self, t)()


if __name__ == '__main__':
    h = HostCrawl(env='default', instance='10.0.14.224')
    h.run()
    print(h.ret)
