from db_models.models import GrafanaMainPage, MonitorUrl, Host, ApplicationHub
import requests
import json
import logging
import pytz
import datetime
import traceback
from omp_server.settings import TIME_ZONE
from utils.parse_config import PROMETHEUS_AUTH

logger = logging.getLogger('server')


class CurlPrometheus(object):
    @staticmethod
    def curl_prometheus():
        """
          请求prometheus接口返回相应json
        """
        prometheus_auth = (PROMETHEUS_AUTH.get("username"),
                           PROMETHEUS_AUTH.get("plaintext_password"))
        monitor_ip = MonitorUrl.objects.filter(name="prometheus")
        monitor_url = monitor_ip[0].monitor_url if len(
            monitor_ip) else "127.0.0.1:19013"
        try:
            url = f"http://{monitor_url}/api/v1/alerts"
            response = requests.request(
                "GET", url, headers={}, data="", auth=prometheus_auth)
            return json.loads(response.text)
        except Exception as e:
            logger.error("prometheus请求alerts失败：" + str(e))
            return {"status": "-1"}


def utc_local(utc_time_str, utc_format='%Y-%m-%dT%H:%M:%SZ'):
    """
    时区转换，如果转换报错，那么使用当前时间作为返回值
    :type utc_time_str str
    :param utc_time_str: utc时间字符串
    :type utc_format str
    :param utc_format: utc时间格式
    :return:
    """
    try:
        utc_time_str = utc_time_str.split(
            ".")[0] + utc_time_str.split(".")[-1][-1]
        local_tz = pytz.timezone(TIME_ZONE)
        local_format = "%Y-%m-%d %H:%M:%S"
        utc_dt = datetime.datetime.strptime(utc_time_str, utc_format)
        local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
        time_str = local_dt.strftime(local_format)
        return time_str
    except Exception as e:
        logger.error(f"在转化时间格式时报错: {str(e)}\n详情为: {traceback.format_exc()}")
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def explain_prometheus(params):
    """
      生成前端异常清单所需要的json列表
    """
    host_list = dict(Host.objects.values_list('ip', 'instance_name'))
    r = CurlPrometheus.curl_prometheus()
    if r.get('status') == 'success':
        prometheus_info = []
        compare_list = []
        alerts = r.get('data').get('alerts')
        prometheus_alerts = sorted(
            alerts, key=lambda e: e.get('labels').__getitem__('severity'), reverse=False)
        for lab in prometheus_alerts:
            if lab.get('status') == 'resolved':
                continue
            tmp_dict = {}
            label = lab.get('labels')
            tmp_list = [label.get('alertname'), label.get(
                'instance'), label.get('job')]
            if tmp_list in compare_list:
                continue
            compare_list.append(tmp_list)
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
            tmp_dict['date'] = utc_local(lab_date)
            prometheus_info.append(tmp_dict)
        prometheus_json = explain_url(prometheus_info)
        if params:
            prometheus_json = explain_filter(prometheus_json, params)
        return prometheus_json
    else:
        logger.error("prometheus请求alerts失败：" + str(r))
        return "error"


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
    # fil_info = filter(lambda x: fil_filed[1].lower()
    # in x.get(fil_filed[0]).lower(), prometheus_json)
    return explain_filter(fil_info, params)


def explain_url(explain_info, is_service=None):
    """
    封装dict添加grafana的url
    """
    # monitor_ip = MonitorUrl.objects.filter(name="grafana")
    # grafana_ins = monitor_ip[0].monitor_url if len(
    #     monitor_ip) else "127.0.0.1:19013"
    # grafana_url = f"http://{grafana_ins}"
    # 去掉跳转grafana中携带的ip、port
    grafana_url = ""
    url_dict = {}
    for i in GrafanaMainPage.objects.all():
        url_dict[i.instance_name] = i.instance_url
    for instance_info in explain_info:
        # TODO 待确认 跳转服务面板使用 app_name 而不是 instance_name ?
        if is_service:
            service_name = instance_info.get('app_name')
        else:
            service_name = instance_info.get('instance_name')
        if instance_info.get('is_web'):
            instance_info['monitor_url'] = None
            instance_info['log_url'] = None
            continue
        service_ip = instance_info.get('ip')
        if instance_info.get('type') == 'service' \
                or is_service:
            monitor_url = url_dict.get(service_name)
            if monitor_url:
                instance_info['monitor_url'] = grafana_url + \
                    monitor_url + f"?var-instance={service_ip}&kiosk=tv"
            else:
                try:
                    if service_name and ApplicationHub.objects.filter(
                            app_name=service_name
                    ).first() and ApplicationHub.objects.filter(
                            app_name=service_name
                    ).first().app_monitor.get("type") == "JavaSpringBoot":
                        instance_info['monitor_url'] = grafana_url + url_dict.get(
                            'javaspringboot',
                            'nojavaspringboot') + \
                            f"?var-env=default&var-ip={service_ip}" \
                            f"&var-app={service_name}&var-job={service_name}Exporter&kiosk=tv"
                    else:
                        instance_info['monitor_url'] = grafana_url + url_dict.get(
                            'service', 'noservice') + f"?var-ip={service_ip}&var-app={service_name}&kiosk=tv"
                except Exception as e:
                    logger.error(e)
                    instance_info['monitor_url'] = grafana_url + url_dict.get(
                        'service', 'noservice') + f"?var-ip={service_ip}&var-app={service_name}&kiosk=tv"
            instance_info['log_url'] = grafana_url + \
                url_dict.get('log', 'nolog') + f"?var-app={service_name}"
        else:
            instance_info['monitor_url'] = grafana_url + \
                url_dict.get('node', 'nohosts') + \
                f"?var-node={service_ip}&kiosk=tv"
            instance_info['log_url'] = None
    return explain_info
