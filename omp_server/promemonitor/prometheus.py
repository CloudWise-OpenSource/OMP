import logging

import requests

logger = logging.getLogger('server')


class Prometheus:
    """
    定义prometheus的一些参数以及动作
    """

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.basic_api_url = f'http://{self.ip}:{self.port}/api/v1/query?query='

    def get_host_cpu_usage(self, host_ip):
        """
        获取指定主机cpu使用率
        """
        headers = {'Content-Type': 'application/json'}
        query_url = f'{self.basic_api_url}(1 - avg(rate(node_cpu_seconds_total' \
                    f'{{instance="{host_ip}",mode="idle"}}[2m])) by (instance))*100'
        print(query_url)

        try:
            get_cpu_response = requests.request(method="GET", url=query_url, headers=headers)
            if get_cpu_response.status_code == 200:
                cpu_usage_dict = get_cpu_response.json()
                cpu_usage = cpu_usage_dict.get('data').get('result')
                return cpu_usage
            else:
                logger.error(get_cpu_response.text)
                logger.error(f'获取主机{host_ip}CPU使用率失败！')
                return None
        except requests.ConnectionError as e:
            logger.error(e)
            logger.error(f'获取主机{host_ip}CPU使用率失败！')
            return None

    def get_host_mem_usage(self, host_ip):
        """
        获取指定主机内存使用率
        """
        headers = {'Content-Type': 'application/json'}
        query_url = f'{self.basic_api_url}(1 - (node_memory_MemAvailable_bytes{{instance="{host_ip}"}} / ' \
                    f'(node_memory_MemTotal_bytes{{instance="{host_ip}"}})))* 100'
        print(query_url)

        try:
            get_mem_response = requests.request(method="GET", url=query_url, headers=headers)
            if get_mem_response.status_code == 200:
                mem_usage_dict = get_mem_response.json()
                mem_usage = mem_usage_dict.get('data').get('result')
                return mem_usage
            else:
                logger.error(get_mem_response.text)
                logger.error(f'获取主机{host_ip}内存使用率失败！')
                return None
        except requests.ConnectionError as e:
            logger.error(e)
            logger.error(f'获取主机{host_ip}内存使用率失败！')
            return None

    def get_host_root_disk_usage(self, host_ip):
        """
        获取指定主机磁盘根分区使用率
        """
        headers = {'Content-Type': 'application/json'}
        query_url = f'{self.basic_api_url}\'(node_filesystem_size_bytes{{mountpoint="/"}}-' \
                    f'node_filesystem_free_bytes{{mountpoint="/",fstype!="rootfs"}})*100/' \
                    f'(node_filesystem_avail_bytes{{mountpoint="/"}}+(node_filesystem_size_bytes{{mountpoint="/"}}-' \
                    f'node_filesystem_free_bytes{{mountpoint="/"}}))\''
        print(query_url)

        try:
            get_root_disk_response = requests.request(method="GET", url=query_url, headers=headers)
            if get_root_disk_response.status_code == 200:
                root_disk_usage_dict = get_root_disk_response.json()
                # root_disk_usage = root_disk_usage_dict.get('data').get('result')
                root_disk_usage = root_disk_usage_dict
                return root_disk_usage
            else:
                logger.error(get_root_disk_response.text)
                logger.error(f'获取主机{host_ip}磁盘根分区使用率失败！')
                return None
        except requests.ConnectionError as e:
            logger.error(e)
            logger.error(f'获取主机{host_ip}磁盘根分区使用率失败！')
            return None

    def get_host_data_disk_usage(self, host_ip, disk):
        """
        获取指定主机磁盘数据分区使用率
        """
        headers = {'Content-Type': 'application/json'}
        query_url = f'{self.basic_api_url}\'(node_filesystem_size_bytes{{mountpoint="{disk}"}}-' \
                    f'node_filesystem_free_bytes{{mountpoint="{disk}"}})*100/(node_filesystem_avail_bytes' \
                    f'{{mountpoint="{disk}"}}+(node_filesystem_size_bytes{{mountpoint="{disk}"}}-' \
                    f'node_filesystem_free_bytes{{mountpoint="{disk}"}}))\''
        print(query_url)

        try:
            get_data_disk_response = requests.request(method="GET", url=query_url, headers=headers)
            if get_data_disk_response.status_code == 200:
                data_disk_usage_dict = get_data_disk_response.json()
                # data_disk_usage = data_disk_usage_dict.get('data').get('result')
                data_disk_usage = data_disk_usage_dict
                return data_disk_usage
            else:
                logger.error(get_data_disk_response.text)
                logger.error(f'获取主机{host_ip}磁盘数据分区使用率失败！')
                return None
        except requests.ConnectionError as e:
            logger.error(e)
            logger.error(f'获取主机{host_ip}磁盘数据分区使用率失败！')
            return None


if __name__ == '__main__':
    p = Prometheus('10.0.3.66', '19011')
    cpu = p.get_host_cpu_usage('10.0.3.71')
    mem = p.get_host_mem_usage('10.0.3.71')
    root = p.get_host_root_disk_usage('10.0.3.71')
    a_disk = p.get_host_data_disk_usage('10.0.3.71', '/data')

    print(cpu)
    print(mem)
    print(root)
    print(a_disk)
