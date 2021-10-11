from db_models.models import GrafanaMainPage, MonitorUrl, Host
import requests
import json
import logging

logger = logging.getLogger('server')


class CurlPrometheus(object):
    @staticmethod
    def curl_prometheus():
        """
          请求prometheus接口返回相应json
        """
        monitor_ip = MonitorUrl.objects.filter(name="prometheus")
        monitor_url = monitor_ip[0].monitor_url if len(
            monitor_ip) else "127.0.0.1:19013"
        try:
            url = f"http://{monitor_url}/api/v1/alerts"
            response = requests.request("GET", url, headers={}, data="")
            return json.loads(response.text)
        except Exception as e:
            logger.error("prometheus请求alerts失败：" + str(e))


def explain_prometheus(params):
    """
      生成前端异常清单所需要的json列表
    """
    host_list = dict(Host.objects.values_list('ip', 'instance_name'))
    r = CurlPrometheus.curl_prometheus()
    if r.get('status') == 'success':
        prometheus_info = []
        for lab in r.get('data').get('alerts'):
            if lab.get('status') == 'resolved':
                continue
            tmp_dict = {}
            label = lab.get('labels')
            tmp_dict['type'] = "host" if label.get(
                'job') == 'nodeExporter' else "service"
            tmp_dict['ip'] = label.get('instance').split(":")[0]
            tmp_dict['instance_name'] = label.get('app') if label.get(
                'app') else host_list.get(tmp_dict.get('ip'))
            tmp_dict['severity'] = label.get('severity')
            annotation = lab.get('annotations')
            tmp_dict['description'] = annotation.get('description')
            lab_date = lab.get('activeAt') if lab.get(
                'activeAt') else lab.get('startsAt')
            tmp_dict['date'] = lab_date.split(".")[0].replace("T", " ")
            prometheus_info.append(tmp_dict)
        prometheus_json = explain_url(prometheus_info)
        if params:
            prometheus_json = explain_filter(prometheus_json, params)
        return prometheus_json
    else:
        logger.error("prometheus请求alerts失败：" + str(r))


def explain_filter(prometheus_json, params):
    """
       递归筛选
    """
    if not params:
        return prometheus_json
    fil_filed = params.popitem()
    fil_info = []
    for j in prometheus_json:
        value = j.get(fil_filed[0])
        if value and fil_filed[1].lower() in value.lower():
            fil_info.append(j)
    # fil_info = filter(lambda x: fil_filed[1].lower() in x.get(fil_filed[0]).lower(), prometheus_json)
    return explain_filter(fil_info, params)


def explain_url(explain_info):
    """
    封装dict添加grafana的url
    """
    monitor_ip = MonitorUrl.objects.filter(name="grafana")
    grafana_ins = monitor_ip[0].monitor_url if len(
        monitor_ip) else "127.0.0.1:19013"
    grafana_url = f"http://{grafana_ins}"
    url_dict = {}
    for i in GrafanaMainPage.objects.all():
        url_dict[i.instance_name] = i.instance_url
    for instance_info in explain_info:
        service_name = instance_info.get('instance_name')
        service_ip = instance_info.get('ip')
        if instance_info.get('type') == 'service':
            monitor_url = url_dict.get(service_name)
            if monitor_url:
                instance_info['monitor_url'] = grafana_url + \
                    monitor_url + f"?var-instance={service_ip}"
            instance_info['monitor_url'] = grafana_url + url_dict.get(
                'service') + f"?var-ip={service_ip}&var-app={service_name}"
            instance_info['log_url'] = grafana_url + \
                url_dict.get('log') + f"?var-app={service_name}"
        else:
            instance_info['monitor_url'] = grafana_url + \
                url_dict.get('node') + f"?var-node={service_ip}"
            instance_info['log_url'] = None
    return explain_info
