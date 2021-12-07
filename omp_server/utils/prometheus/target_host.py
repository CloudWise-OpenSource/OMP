# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/10/14 6:26 下午
# Description: 主机指标
import json
import logging
import random
from datetime import datetime
from db_models.models import Host
from utils.plugin.salt_client import SaltClient
from utils.prometheus.prometheus import Prometheus
from utils.prometheus.utils import get_host_data_folder

logger = logging.getLogger("server")


def target_host_thread(env, instance):
    """
    主机巡检，多线程执行
    :env: 环境 queryset 对象
    :instance: 主机ip地址
    """
    temp = dict()
    # 主机 prometheus 数据请求
    h_w_obj = HostCrawl(env=env.name, instance=instance)
    h_w_obj.run()
    _p = h_w_obj.ret
    temp['id'] = random.randint(1, 99999999)
    temp['mem_usage'] = _p.get('mem_usage')
    temp['cpu_usage'] = _p.get('cpu_usage')
    temp['disk_usage_root'] = _p.get('disk_usage_root')
    temp['disk_usage_data'] = _p.get('disk_usage_data')
    temp['sys_load'] = _p.get('sys_load')
    temp['run_time'] = _p.get('run_time')
    temp['host_ip'] = instance
    temp['memory_top'] = _p.get('memory_top', [])
    temp['cpu_top'] = _p.get('cpu_top', [])
    temp['kernel_parameters'] = _p.get('kernel_parameters', [])
    # 操作系统
    _h = Host.objects.filter(ip=instance).first()
    temp['release_version'] = _h.operate_system if _h else ''
    # 配置信息
    host_massage = \
        f"{_h.cpu if _h else '-'}C|{_h.memory if _h else '-'}G|" \
        f"{sum(_h.disk.values()) if _h and _h.disk else '-'}G"
    temp['host_massage'] = host_massage
    temp['basic'] = [
        {"name": "IP", "name_cn": "主机IP", "value": instance},
        {"name": "hostname", "name_cn": "主机名",
         "value": _h.host_name if _h else '-'},
        {"name": "kernel_version", "name_cn": "内核版本",
         "value": _p.get('kernel_version')},
        {"name": "selinux", "name_cn": "SElinux 状态",
         "value": _p.get('selinux')},
        {"name": "max_openfile", "name_cn": "最大打开文件数",
         "value": _p.get('max_openfile')},
        {"name": "iowait", "name_cn": "IOWait", "value": _p.get('iowait')},
        {"name": "inode_usage", "name_cn": "inode 使用率",
         "value": {"/": _p.get('inode_usage')}},
        {"name": "now_time", "name_cn": "当前时间",
         "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
        {"name": "run_process", "name_cn": "进程数",
         "value": _p.get('run_process')},
        {"name": "umask", "name_cn": "umask", "value": _p.get('umask')},
        {"name": "bandwidth", "name_cn": "带宽", "value": _p.get('bandwidth')},
        {"name": "throughput", "name_cn": "IO", "value": _p.get('throughput')},
        {"name": "zombies_process", "name_cn": "僵尸进程",
         "value": _p.get('zombies_process')}
    ]
    return temp


class HostCrawl(Prometheus):
    """
    查询 prometheus 主机指标
    """

    def __init__(self, env, instance):
        self.ret = {}
        self.env = env              # 环境
        self.instance = instance    # 主机ip
        self._obj = SaltClient()
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
        days, hours = divmod(hours, 24)
        if int(0) > 0:
            self.ret['run_time'] = \
                f"{int(days)}天{int(hours)}小时{int(minutes)}分钟{int(seconds)}秒"
        else:
            self.ret['run_time'] = \
                f"{int(hours)}小时{int(minutes)}分钟{int(seconds)}秒"

    def cpu_usage(self):
        """总cpu使用率"""
        expr = f"100 - (avg(rate(node_cpu_seconds_total" \
               f"{{env='{self.env}'," \
               f"instance=~'{self.instance}'," \
               f"mode='idle'}}[5m])) * 100)"
        self.ret['cpu_usage'] = \
            f"{round(float(self.unified_job(*self.query(expr))), 2)}%"

    def iowait(self):
        """IO wait使用率"""
        expr = f"avg(rate(node_cpu_seconds_total{{env='{self.env}'," \
               f"instance=~'{self.instance}',mode='iowait'}}[5m])) * 100"
        self.ret['iowait'] = \
            f"{round(float(self.unified_job(*self.query(expr))), 2)}%"

    def mem_usage(self):
        """内存使用率"""
        expr = f"(1 - (node_memory_MemAvailable_bytes" \
               f"{{env='{self.env}'," \
               f"instance=~'{self.instance}'}} / " \
               f"(node_memory_MemTotal_bytes{{env='{self.env}'," \
               f"instance=~'{self.instance}'}})))* 100"
        self.ret['mem_usage'] = \
            f"{round(float(self.unified_job(*self.query(expr))), 2)}%"

    def disk_usage_root(self):
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
        self.ret['disk_usage_root'] = \
            f"{round(float(self.unified_job(*self.query(expr))), 2)}%"

    def disk_usage_data(self):
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
        self.ret['disk_usage_data'] = f"{round(float(_), 2)}%" if _ else '_'

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

    def inode_usage(self):
        """inode使用率"""
        expr = f"(1-node_filesystem_files_free{{fstype=~'xfs|ext4'," \
               f"mountpoint='/', env='{self.env}'," \
               f"instance=~'{self.instance}'}} / " \
               f"node_filesystem_files{{fstype=~'xfs|ext4',mountpoint='/', " \
               f"env='{self.env}',instance=~'{self.instance}'}})*100"
        self.ret['inode_usage'] = \
            f"{round(float(self.unified_job(*self.query(expr))), 2)}%"

    def max_openfile(self):
        """总文件描述符"""
        expr = f"avg(node_filefd_maximum{{instance=~'{self.instance}'}})"
        self.ret['max_openfile'] = self.unified_job(*self.query(expr))

    def sys_load(self):
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
        self.ret['sys_load'] = f"{load1},{load5},{load15}"

    def bandwidth(self):
        """网络带宽使用"""
        # eth0 下载
        expr = f"sum(rate(node_network_receive_bytes_total{{env='{self.env}'," \
               f"instance=~'{self.instance}',device=~'eth0'}}[2m])*8/1024)"
        self.ret['bandwidth'] = {
            'receive': f"{round(float(self.unified_job(*self.query(expr))), 2)}"
                       f"kb/s"}
        # eth0 上传
        expr = f"sum(rate(node_network_transmit_bytes_total" \
               f"{{env='{self.env}',instance=~'{self.instance}'," \
               f"device=~'eth0'}}[2m])*8/1024)"
        self.ret['bandwidth']['transmit'] = \
            f"{round(float(self.unified_job(*self.query(expr))), 2)}kb/s"

    def throughput(self):
        """磁盘io"""
        # 读
        expr = f"sum(rate(node_disk_read_bytes_total{{env='{self.env}'," \
               f"instance=~'{self.instance}'}}[2m])) / 1024"
        self.ret['throughput'] = \
            {'read': f"{round(float(self.unified_job(*self.query(expr))), 2)}"
                     f"kb/s"}
        # 写
        expr = f"sum(rate(node_disk_written_bytes_total" \
               f"{{env='{self.env}'," \
               f"instance=~'{self.instance}'}}[2m])) / 1024"
        self.ret['throughput']['write'] = \
            f"{round(float(self.unified_job(*self.query(expr))), 2)}kb/s"

    def salt_json(self):
        try:
            self._obj.salt_module_update()
            ret = self._obj.fun(self.instance, "host_check.main")
            if ret and ret[0]:
                ret = json.loads(ret[1])
            else:
                ret = {}
        except Exception as e:
            logger.error(f"Salt host_check.main failed with error: {str(e)}")
            ret = {}

        self.ret['memory_top'] = ret.get('memory_top', [])
        self.ret['cpu_top'] = ret.get('cpu_top', [])
        self.ret['kernel_parameters'] = ret.get('kernel_parameters', [])
        self.ret['kernel_version'] = ret.get('kernel_version')
        self.ret['selinux'] = ret.get('selinux')
        self.ret['run_process'] = ret.get('run_process')
        self.ret['umask'] = ret.get('umask')
        self.ret['zombies_process'] = ret.get('zombies_process')

    def run(self):
        """统一执行实例方法"""
        # target为实例方法，目的是统一执行实例方法并统一返回值
        target = ['mem_usage', 'cpu_usage', 'disk_usage_root',
                  'disk_usage_data', 'sys_load', 'run_time', 'max_openfile',
                  'inode_usage', 'iowait', 'bandwidth', 'throughput',
                  'salt_json', 'run_status']
        for t in target:
            if getattr(self, t):
                getattr(self, t)()


if __name__ == '__main__':
    h = HostCrawl(env='default', instance='10.0.14.224')
    h.run()
    print(h.ret)
