import logging
import math

import requests

from db_models.models import MonitorUrl

logger = logging.getLogger('server')


class Prometheus:
    """
    定义prometheus的一些参数以及动作
    """

    def __init__(self):
        self.ip, self.port = self.get_prometheus_config()
        self.basic_api_url = f'http://{self.ip}:{self.port}/api/v1/query?query='

    @staticmethod
    def get_prometheus_config():
        # prometheus_url_config = MonitorUrl.objects.filter(name='prometheus')
        # ip = prometheus_url_config.ip
        # port = prometheus_url_config.port
        # if ip and port:
        #     return ip, port
        return '10.0.3.66', '19011'  # 默认值

    @staticmethod
    def get_host_threshold():
        host_threshold = {
            'cpu': (80, 90),
            'mem': (80, 90),
            'root_disk': (80, 90),
            'data_disk': (80, 90),
        }
        # TODO 从库里获取真实值
        return host_threshold

    def get_host_metric_status(self, metric, metric_value):
        host_threshold = self.get_host_threshold()
        if metric_value > max(host_threshold.get(metric)):
            status = 'critical'
        elif metric_value > min(host_threshold.get(metric)):
            status = 'normal'
        else:
            status = 'warning'
        return status

    def get_host_cpu_usage(self, host_list):
        """
        获取指定主机cpu使用率
        """
        headers = {'Content-Type': 'application/json'}
        query_url = f'{self.basic_api_url}(1 - avg(rate(node_cpu_seconds_total' \
                    f'{{mode="idle"}}[2m])) by (instance))*100'
        # print(query_url)
        try:
            get_cpu_response = requests.request(method="GET", url=query_url, headers=headers)
            if get_cpu_response.status_code == 200:
                cpu_usage_dict = get_cpu_response.json()
                if cpu_usage_dict.get('status') != 'success':
                    logger.error(get_cpu_response.text)
                    logger.error(f'获取主机CPU使用率失败！')
                    return None
                for index, host in enumerate(host_list.copy()):
                    for item in cpu_usage_dict.get('data').get('result'):
                        if item.get('metric').get('instance') == host.get('ip'):
                            host_list[index]['cpu_usage'] = math.ceil(float(item.get('value')[1]))
                            host_list[index]['cpu_status'] = self.get_host_metric_status('cpu', math.ceil(
                                float(item.get('value')[1])))
                            break
                        host_list[index]['cpu_usage'] = None
                        host_list[index]['cpu_status'] = None  # TODO  待阈值判断

                return host_list
            else:
                logger.error(get_cpu_response.text)
                logger.error(f'获取主机CPU使用率失败！')
                return None
        except requests.ConnectionError as e:
            logger.error(e)
            logger.error(f'获取主机CPU使用率失败！')
            return None

    def get_host_mem_usage(self, host_list):
        """
        获取指定主机内存使用率
        """
        headers = {'Content-Type': 'application/json'}
        query_url = f'{self.basic_api_url}(1 - (node_memory_MemAvailable_bytes / ' \
                    f'(node_memory_MemTotal_bytes)))* 100'
        # print(query_url)

        try:
            get_mem_response = requests.request(method="GET", url=query_url, headers=headers)
            if get_mem_response.status_code == 200:
                mem_usage_dict = get_mem_response.json()
                if mem_usage_dict.get('status') != 'success':
                    logger.error(get_mem_response.text)
                    logger.error(f'获取主机内存使用率失败！')
                    return None
                for index, host in enumerate(host_list.copy()):
                    for item in mem_usage_dict.get('data').get('result'):
                        if item.get('metric').get('instance') == host.get('ip'):
                            host_list[index]['mem_usage'] = math.ceil(float(item.get('value')[1]))
                            host_list[index]['mem_status'] = self.get_host_metric_status('mem', math.ceil(
                                float(item.get('value')[1])))
                            break
                        host_list[index]['mem_usage'] = None
                        host_list[index]['mem_status'] = None  # TODO  待阈值判断
                return host_list
            else:
                logger.error(get_mem_response.text)
                logger.error(f'获取主机内存使用率失败！')
                return None
        except requests.ConnectionError as e:
            logger.error(e)
            logger.error(f'获取主机内存使用率失败！')
            return None

    def get_host_root_disk_usage(self, host_list):
        """
        获取指定主机磁盘根分区使用率
        """
        headers = {'Content-Type': 'application/json'}
        query_url = f'{self.basic_api_url}(node_filesystem_size_bytes{{mountpoint="/"}} - ' \
                    f'node_filesystem_free_bytes{{mountpoint="/",fstype!="rootfs"}}) / ' \
                    f'(node_filesystem_avail_bytes{{mountpoint="/"}}-node_filesystem_free_bytes{{mountpoint="/"}} - ' \
                    f'(-node_filesystem_size_bytes{{mountpoint="/"}}))*100'
        # print(query_url)

        try:
            get_root_disk_response = requests.request(method="GET", url=query_url, headers=headers)
            if get_root_disk_response.status_code == 200:
                root_disk_usage_dict = get_root_disk_response.json()
                if root_disk_usage_dict.get('status') != 'success':
                    logger.error(get_root_disk_response.text)
                    logger.error(f'获取主机磁盘根分区使用率失败！')
                    return None
                for index, host in enumerate(host_list.copy()):
                    for item in root_disk_usage_dict.get('data').get('result'):
                        if item.get('metric').get('instance') == host.get('ip'):
                            host_list[index]['root_disk_usage'] = math.ceil(float(item.get('value')[1]))
                            host_list[index]['root_disk_status'] = self.get_host_metric_status('root_disk', math.ceil(
                                float(item.get('value')[1])))
                            break
                        host_list[index]['root_disk_usage'] = None
                        host_list[index]['root_disk_status'] = None  # TODO
                return host_list
            else:
                logger.error(get_root_disk_response.text)
                logger.error(f'获取主机磁盘根分区使用率失败！')
                return None
        except requests.ConnectionError as e:
            logger.error(e)
            logger.error(f'获取主机磁盘根分区使用率失败！')
            return None

    def get_host_data_disk_usage(self, host_list):
        """
        获取指定主机磁盘数据分区使用率
        """
        headers = {'Content-Type': 'application/json'}
        # print(query_url)
        for index, host in enumerate(host_list.copy()):
            host_ip = host.get('ip')
            host_data_disk = host.get('data_folder')
            query_url = f'{self.basic_api_url}' \
                        f'(node_filesystem_size_bytes{{mountpoint="{host_data_disk}",instance="{host_ip}"}} - ' \
                        f'node_filesystem_free_bytes{{mountpoint="{host_data_disk}",instance="{host_ip}"}}) / ' \
                        f'(node_filesystem_avail_bytes{{mountpoint="{host_data_disk}",instance="{host_ip}"}} - ' \
                        f'node_filesystem_free_bytes{{mountpoint="{host_data_disk}",instance="{host_ip}"}} - ' \
                        f'(-node_filesystem_size_bytes{{mountpoint="{host_data_disk}",instance="{host_ip}"}}))*100'
            try:
                get_data_disk_response = requests.request(method="GET", url=query_url, headers=headers)
                if get_data_disk_response.status_code == 200:
                    data_disk_usage_dict = get_data_disk_response.json()
                    if data_disk_usage_dict.get('status') != 'success':
                        logger.error(get_data_disk_response.text)
                        logger.error(f'获取主机磁盘数据分区使用率失败！')
                        return None
                    for item in data_disk_usage_dict.get('data').get('result'):
                        if item.get('metric').get('instance') == host.get('ip'):
                            host_list[index]['data_disk_usage'] = math.ceil(float(item.get('value')[1]))
                            host_list[index]['data_disk_status'] = self.get_host_metric_status('data_disk', math.ceil(
                                float(item.get('value')[1])))
                            break
                        host_list[index]['data_disk_usage'] = None
                        host_list[index]['data_disk_status'] = None  # TODO
                else:
                    logger.error(get_data_disk_response.text)
                    logger.error(f'获取主机磁盘数据分区使用率失败！')
                    return None
            except requests.ConnectionError as e:
                logger.error(e)
                logger.error(f'获取主机磁盘数据分区使用率失败！')
                return None
        return host_list

    def get_host_info(self, host_list):
        """

        """
        host_list = self.get_host_cpu_usage(host_list)
        host_list = self.get_host_mem_usage(host_list)
        host_list = self.get_host_root_disk_usage(host_list)
        host_list = self.get_host_data_disk_usage(host_list)
        return host_list


# 以下为测试内容，仅供测试用
if __name__ == '__main__':
    host_list_test = [
        {
            'ip': '10.0.3.72',
            'data_folder': '/boot',
            'cpu_usage': 0,
            'mem_usage': 0,
            'root_disk_usage': 0,
            'data_disk_usage': 0,
        },
        {
            'ip': '10.0.9.60',
            'data_disk': '/boot',
            'cpu_usage': 0,
            'mem_usage': 0,
            'root_disk_usage': 0,
            'data_disk_usage': 0
        },
        {
            'ip': '10.0.9.61',
            'data_disk': '/boot',
            'cpu_usage': 0,
            'mem_usage': 0,
            'root_disk_usage': 0,
            'data_disk_usage': 0
        }
    ]
    p = Prometheus()
    host_list_test = p.get_host_info(host_list_test)
    print(host_list_test)
