import json
import time

import requests

from db_models.models import MonitorUrl, GrafanaMainPage
from utils.parse_config import GRAFANA_API_KEY


def make_request(url, headers, payload):
    """
    请求
    :param url:
    :param headers:
    :param payload:
    :return:
    """
    flag = 0
    while flag < 5:
        response = requests.request(
            "GET", url, headers=headers, data=payload)
        r = json.loads(response.text)
        for url in r:
            if not isinstance(url, dict):
                break
        else:
            return True, r
        flag += 1
        time.sleep(30)
    return False, None


def synch_grafana_info():
    """如果存在则不再添加,修改会追加一条数据"""

    monitor_ip = MonitorUrl.objects.filter(name="grafana")
    monitor_url = monitor_ip[0].monitor_url if len(
        monitor_ip) else "127.0.0.1:19014"

    url = """http://{0}/proxy/v1/grafana/api/search?query=&
          starred=false&skipRecent=false&
          skipStarred=false&folderIds=0&layout=folders""".format(monitor_url)
    payload = {}
    headers = {
        'Authorization': f'Bearer {GRAFANA_API_KEY}'
    }
    try:
        flag, r = make_request(url=url, headers=headers, payload=payload)
        if not flag:
            return
    except Exception as e:
        print(e)
        return
    url_type = {"service": "fu", "node": "zhu", "log": "applogs"}
    url_dict = {}
    for url in r:
        url_name = url.get("uri").rsplit("/", 1)[1].split("-", 1)[0]
        url_dict[url_name.lower()] = url.get("url")

    for key, value in url_type.items():
        url_dict.update({key: url_dict.pop(value)})

    if GrafanaMainPage.objects.all().count() != len(url_dict):
        dbname = [i.instance_name for i in GrafanaMainPage.objects.all()]
        difference = list(set(url_dict.keys()).difference(set(dbname)))
        grafana_obj = [GrafanaMainPage(
            instance_name=i, instance_url=url_dict.get(i)) for i in difference]
        GrafanaMainPage.objects.bulk_create(grafana_obj)
