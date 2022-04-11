import logging
import requests
import json
from utils.parse_config import MONITOR_PORT
from promemonitor.prometheus_utils import CW_TOKEN


logger = logging.getLogger("server")


def get_service_status_direct(service_obj_list):
    """
    直接从monitor_agent获取服务状态
    param: [{"ip": "127.0.0.1", "service_name": "mysql"}, {"ip": "127.0.0.1", "service_name": "redis"}]
    """
    service_obj_result = list()
    monitor_agent_port = MONITOR_PORT.get('monitorAgent', 19031)
    headers = {"Content-Type": "application/json"}.update(CW_TOKEN)
    ip_item_list = list()
    ip_list = list()
    for ele in service_obj_list:
        ip_list.append(ele.get("ip"))
    ip_list = list(set(ip_list))
    for ip in ip_list:
        ip_service_list = list()
        for item in service_obj_list:
            if ip == item.get("ip"):
                ip_service_list.append(item)
        ip_item_list.append(ip_service_list)

    try:
        for ii in ip_item_list:
            status_url = f"http://{ii[0].get('ip')}:{monitor_agent_port}/service_status"  # NOQA
            response = requests.request(
                "POST", status_url, headers=headers, data=json.dumps(ii))
            if response.status_code != 200:
                continue
            service_obj_result.extend(response.json().get("beans"))
        return service_obj_result
    except Exception as e:
        logger.error(f"获取制定服务列表状态失败，详情为：{e}")
        return service_obj_list
