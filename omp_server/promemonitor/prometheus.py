import json
import logging
import math

import requests

from db_models.models import MonitorUrl
from utils.parse_config import MONITOR_PORT

logger = logging.getLogger('server')


class Prometheus:
    """
    定义prometheus的一些参数以及动作
    """
    STATUS = ("normal", "warning", "critical")

    def __init__(self):
        self.basic_url = self.get_prometheus_config()
        self.prometheus_api_query_url = f'http://{self.basic_url}/api/v1/query?query='  # NOQA

    @staticmethod
    def get_prometheus_config():
        prometheus_url_config = MonitorUrl.objects.filter(
            name='prometheus').first()
        if not prometheus_url_config:
            return f'127.0.0.1:{MONITOR_PORT.get("prometheus", 19011)}'  # 默认值

        monitor_url = prometheus_url_config.monitor_url
        if monitor_url:
            return monitor_url
        return f'127.0.0.1:{MONITOR_PORT.get("prometheus", 19011)}'  # 默认值

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
        if not metric_value:
            return None
        host_threshold = self.get_host_threshold()
        if metric_value > max(host_threshold.get(metric)):
            status = 'critical'
        elif metric_value < min(host_threshold.get(metric)):
            status = 'normal'
        else:
            status = 'warning'
        return status

    def get_host_cpu_usage(self, host_list):
        """
        获取指定主机cpu使用率
        """
        headers = {'Content-Type': 'application/json'}
        query_url = f'{self.prometheus_api_query_url}(1 - avg(rate(node_cpu_seconds_total' \
                    f'{{mode="idle"}}[2m])) by (instance))*100'
        # print(query_url)
        try:
            get_cpu_response = requests.get(url=query_url, headers=headers)
            if get_cpu_response.status_code == 200:
                cpu_usage_dict = get_cpu_response.json()
                if cpu_usage_dict.get('status') != 'success':
                    logger.error(get_cpu_response.text)
                    logger.error('获取主机CPU使用率失败！')
                    return host_list
                for index, host in enumerate(host_list.copy()):
                    for item in cpu_usage_dict.get('data').get('result'):
                        if item.get('metric').get('instance') == host.get('ip'):
                            host_list[index]['cpu_usage'] = math.ceil(
                                float(item.get('value')[1]))
                            host_list[index]['cpu_status'] = self.get_host_metric_status('cpu', math.ceil(
                                float(item.get('value')[1])))
                            break
                        host_list[index]['cpu_usage'] = None
                        host_list[index]['cpu_status'] = None  # TODO  待阈值判断

                return host_list
            else:
                logger.error(get_cpu_response.text)
                logger.error('获取主机CPU使用率失败！')
                return host_list
        except requests.ConnectionError as e:
            logger.error(e)
            logger.error('获取主机CPU使用率失败！')
            return host_list
        except Exception as e:
            logger.error(e)
            logger.error('获取主机CPU使用率失败！')
            return host_list

    def get_host_mem_usage(self, host_list):
        """
        获取指定主机内存使用率
        """
        headers = {'Content-Type': 'application/json'}
        query_url = f'{self.prometheus_api_query_url}(1 - (node_memory_MemAvailable_bytes / ' \
                    f'(node_memory_MemTotal_bytes)))* 100'
        # print(query_url)

        try:
            get_mem_response = requests.get(url=query_url, headers=headers)
            if get_mem_response.status_code == 200:
                mem_usage_dict = get_mem_response.json()
                if mem_usage_dict.get('status') != 'success':
                    logger.error(get_mem_response.text)
                    logger.error('获取主机内存使用率失败！')
                    return host_list
                for index, host in enumerate(host_list.copy()):
                    for item in mem_usage_dict.get('data').get('result'):
                        if item.get('metric').get('instance') == host.get('ip'):
                            host_list[index]['mem_usage'] = math.ceil(
                                float(item.get('value')[1]))
                            host_list[index]['mem_status'] = self.get_host_metric_status('mem', math.ceil(
                                float(item.get('value')[1])))
                            break
                        host_list[index]['mem_usage'] = None
                        host_list[index]['mem_status'] = None  # TODO  待阈值判断
                return host_list
            else:
                logger.error(get_mem_response.text)
                logger.error('获取主机内存使用率失败！')
                return host_list
        except requests.ConnectionError as e:
            logger.error(e)
            logger.error('获取主机内存使用率失败！')
            return host_list
        except Exception as e:
            logger.error(e)
            logger.error('获取主机内存使用率失败！')
            return host_list

    def get_host_root_disk_usage(self, host_list):
        """
        获取指定主机磁盘根分区使用率
        """
        headers = {'Content-Type': 'application/json'}
        query_url = f'{self.prometheus_api_query_url}(node_filesystem_size_bytes{{mountpoint="/"}} - ' \
                    f'node_filesystem_free_bytes{{mountpoint="/",fstype!="rootfs"}}) / ' \
                    f'(node_filesystem_avail_bytes{{mountpoint="/"}}-node_filesystem_free_bytes{{mountpoint="/"}} - ' \
                    f'(-node_filesystem_size_bytes{{mountpoint="/"}}))*100'
        # print(query_url)

        try:
            get_root_disk_response = requests.get(
                url=query_url, headers=headers)
            if get_root_disk_response.status_code == 200:
                root_disk_usage_dict = get_root_disk_response.json()
                if root_disk_usage_dict.get('status') != 'success':
                    logger.error(get_root_disk_response.text)
                    logger.error('获取主机磁盘根分区使用率失败！')
                    return host_list
                for index, host in enumerate(host_list.copy()):
                    for item in root_disk_usage_dict.get('data').get('result'):
                        if item.get('metric').get('instance') == host.get('ip'):
                            host_list[index]['root_disk_usage'] = math.ceil(
                                float(item.get('value')[1]))
                            host_list[index]['root_disk_status'] = self.get_host_metric_status('root_disk', math.ceil(
                                float(item.get('value')[1])))
                            break
                        host_list[index]['root_disk_usage'] = None
                        host_list[index]['root_disk_status'] = None  # TODO
                return host_list
            else:
                logger.error(get_root_disk_response.text)
                logger.error('获取主机磁盘根分区使用率失败！')
                return host_list
        except requests.ConnectionError as e:
            logger.error(e)
            logger.error('获取主机磁盘根分区使用率失败！')
            return host_list
        except Exception as e:
            logger.error(e)
            logger.error('获取主机磁盘根分区使用率失败！')
            return host_list

    def get_host_data_disk_usage(self, host_list):
        """
        获取指定主机磁盘数据分区使用率
        """
        headers = {'Content-Type': 'application/json'}
        # print(query_url)
        for index, host in enumerate(host_list.copy()):
            host_ip = host.get('ip')
            host_data_disk = host.get('data_folder')
            query_url = f'{self.prometheus_api_query_url}' \
                        f'(node_filesystem_size_bytes{{mountpoint="{host_data_disk}",instance="{host_ip}"}} - ' \
                        f'node_filesystem_free_bytes{{mountpoint="{host_data_disk}",instance="{host_ip}"}}) / ' \
                        f'(node_filesystem_avail_bytes{{mountpoint="{host_data_disk}",instance="{host_ip}"}} - ' \
                        f'node_filesystem_free_bytes{{mountpoint="{host_data_disk}",instance="{host_ip}"}} - ' \
                        f'(-node_filesystem_size_bytes{{mountpoint="{host_data_disk}",instance="{host_ip}"}}))*100'
            try:
                get_data_disk_response = requests.get(
                    url=query_url, headers=headers)
                if get_data_disk_response.status_code == 200:
                    data_disk_usage_dict = get_data_disk_response.json()
                    if data_disk_usage_dict.get('status') != 'success':
                        logger.error(get_data_disk_response.text)
                        logger.error('获取主机磁盘数据分区使用率失败！')
                        continue
                    if not data_disk_usage_dict.get('data').get('result'):
                        host_list[index]['data_disk_usage'] = None
                        host_list[index]['data_disk_status'] = None
                    for item in data_disk_usage_dict.get('data').get('result'):
                        if item.get('metric').get('instance') == host.get('ip'):
                            host_list[index]['data_disk_usage'] = math.ceil(
                                float(item.get('value')[1]))
                            host_list[index]['data_disk_status'] = self.get_host_metric_status('data_disk', math.ceil(
                                float(item.get('value')[1])))
                            break
                        host_list[index]['data_disk_usage'] = None
                        host_list[index]['data_disk_status'] = None
                else:
                    logger.error(get_data_disk_response.text)
                    logger.error('获取主机磁盘数据分区使用率失败！')
                    continue
            except requests.ConnectionError as e:
                logger.error(e)
                logger.error('获取主机磁盘数据分区使用率失败！')
                continue
            except Exception as e:
                logger.error(e)
                logger.error('获取主机磁盘数据分区使用率失败！')
                continue
        return host_list

    def get_host_info(self, host_list):
        """
        获取主机负载基本信息
        """
        for index, host in enumerate(host_list.copy()):
            host_list[index]['cpu_usage'] = None
            host_list[index]['cpu_status'] = None
            host_list[index]['mem_usage'] = None
            host_list[index]['mem_status'] = None
            host_list[index]['root_disk_usage'] = None
            host_list[index]['root_disk_status'] = None
            host_list[index]['data_disk_usage'] = None
            host_list[index]['data_disk_status'] = None
        host_list = self.get_host_cpu_usage(host_list)
        host_list = self.get_host_mem_usage(host_list)
        host_list = self.get_host_root_disk_usage(host_list)
        host_list = self.get_host_data_disk_usage(host_list)
        return host_list

    def get_all_service_status(self):
        """
        获取服务状态  0-运行; 1-停止
        :return:
        """
        headers = {'Content-Type': 'application/json'}
        query_url = f'{self.prometheus_api_query_url}probe_success'
        try:
            res_body = requests.get(url=query_url, headers=headers)
            res_dic = json.loads(res_body.text)
            if res_dic.get("status") != "success":
                return False, {}
            service_data = res_dic.get("data", {}).get("result", [])
            service_status_dic = dict()
            for item in service_data:
                metric = item.get("metric", {})
                if metric.get("service_type") != "service":
                    continue
                _key = metric.get("instance", "") + "_" + \
                    metric.get("instance_name", "")
                _value = True if int(
                    item.get("value", [0, 0])[-1]) == 1 else False
                service_status_dic[_key] = _value
            return True, service_status_dic
        except Exception as e:
            logger.error(f"从prometheus获取数据失败: {str(e)}")
            return False, {}

    def get_all_host_targets(self):
        headers = {'Content-Type': 'application/json'}
        query_url = f'{self.basic_url}/api/v1/targets'
        host_targets = list()
        try:
            res_body = requests.get(url=query_url, headers=headers)
            res_dic = json.loads(res_body.text)
            if res_dic.get("status") != "success":
                return False, {}
            targets_data = res_dic.get("data", {})
            for item in targets_data:
                if item.get("labels", {}).get("job") != "nodeExporter":
                    continue
                host_targets.append(item.get("labels").get("instance"))
            return True, host_targets
        except Exception as e:
            logger.error(f"从prometheus获取主机targets失败: {str(e)}")
            return False, []

    def get_all_service_targets(self):
        headers = {'Content-Type': 'application/json'}
        query_url = f'{self.basic_url}/api/v1/targets'
        service_targets = list()
        try:
            res_body = requests.get(url=query_url, headers=headers)
            res_dic = json.loads(res_body.text)
            if res_dic.get("status") != "success":
                return False, {}
            targets_data = res_dic.get("data", {})
            for item in targets_data:
                if item.get("labels", {}).get("service_type") != "service":
                    continue
                service_targets.append(
                    f'{item.get("labels").get("instance")}_{item.get("labels").get("instance_name")}')
            return True, service_targets
        except Exception as e:
            logger.error(f"从prometheus获取服务targets失败: {str(e)}")
            return False, []
