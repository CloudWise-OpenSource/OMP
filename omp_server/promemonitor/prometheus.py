import requests


class Prometheus:
    """
    定义prometheus的一些参数以及动作
    """
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.basic_api_url = f'http://{self.ip}:{self.port}/api/v1/query?'

    def get_host_cpu_usage(self, host_ip):
        """
        获取制定主机cpu使用率
        """
        query_content = f'{self.basic_api_url}query=(1 - avg(rate(node_cpu_seconds_total' \
                        f'{{instance="{host_ip}",mode="idle"}}[2m])) by (instance))*100'

