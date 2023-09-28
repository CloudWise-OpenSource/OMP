from db_models.models import GrafanaMainPage, MonitorUrl, Host, ApplicationHub, Service
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


def get_item_type(item, database_list, service_list, component_list):
    """
    获取item类型
    """
    app_name_str = ""
    if item.get("labels").get("job") == "nodeExporter":
        return "host"
    app_name_str = item.get("labels").get("app") if item.get("labels").get("app") else \
        item.get("labels").get("job", "").split("Exporter")[0]
    if not app_name_str:
        return "service"
    if list(filter(
            lambda x: x.service.app_name == app_name_str,
            list(database_list))):
        return "database"
    elif list(filter(
            lambda x: x.service.app_name == app_name_str, list(
                service_list)
    )):
        return "service"
    elif list(filter(
            lambda x: x.service.app_name == app_name_str, list(
                component_list)
    )):
        return "component"
    else:
        return "service"


def explain_prometheus(params):
    """
      生成前端异常清单所需要的json列表
    """
    ignore_status_list = [Service.SERVICE_STATUS_NORMAL,
                          Service.SERVICE_STATUS_STARTING,
                          Service.SERVICE_STATUS_STOPPING,
                          Service.SERVICE_STATUS_RESTARTING,
                          Service.SERVICE_STATUS_STOP]
    host_list = Host.objects.values('ip', 'instance_name')
    host_ip_list = [host.get("ip") for host in host_list]
    database_list = Service.objects.filter(
        service__app_type=ApplicationHub.APP_TYPE_COMPONENT).filter(
        service__app_labels__label_name__contains="数据库").filter(
        service_status__in=ignore_status_list).filter(
        service__is_base_env=False)
    service_list = Service.objects.filter(
        service__app_type=ApplicationHub.APP_TYPE_SERVICE).filter(
        service_status__in=ignore_status_list).filter(
        service__is_base_env=False).filter(
        service_controllers__start__isnull=False)
    component_list = Service.objects.filter(
        service__app_type=ApplicationHub.APP_TYPE_COMPONENT).filter(
        service_status__in=ignore_status_list).filter(
        service__is_base_env=False)
    r = CurlPrometheus.curl_prometheus()
    if r.get('status') == 'success':
        prometheus_info = []
        compare_list = []
        alerts = r.get('data', {}).get('alerts')
        prometheus_alerts = sorted(
            alerts, key=lambda e: e.get('labels').__getitem__('severity'), reverse=False)
        for lab in prometheus_alerts:
            if lab.get('status') == 'resolved':
                continue
            label = lab.get('labels')
            if label.get("instance", "") not in host_ip_list:
                continue
            tmp_dict = {}
            tmp_list = [label.get('alertname'), label.get(
                'instance_name'), label.get('job')]
            if tmp_list in compare_list:
                continue
            compare_list.append(tmp_list)
            _type = get_item_type(item=lab, database_list=database_list, service_list=service_list,
                                  component_list=component_list)
            tmp_dict['type'] = _type
            _ip = label.get('instance').split(":")[0] if label.get('instance') else ''
            tmp_dict['ip'] = _ip
            s_app = label.get('app') if label.get(
                'app') else label.get("job", "").split("Exporter")[0]
            tmp_dict['instance_name'] = f"{s_app}-{_ip.split('.')[2]}-{_ip.split('.')[3]}" if _type != "host" else s_app
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
        # TODO 组件集合包含数据库
        if fil_filed[1].lower() == "component" and value.lower() == "database":
            fil_info.append(j)
    return explain_filter(fil_info, params)


def explain_url(explain_info, is_service=None, is_host=None):
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
            service_name = instance_info.get('instance_name', '').split("-")[0]
        if instance_info.get('is_web'):
            instance_info['monitor_url'] = None
            instance_info['log_url'] = None
            continue
        service_ip = instance_info.get('ip')
        if instance_info.get('type') != 'host' and not is_host \
                or is_service:
            service_instance_name = instance_info.get('service_instance_name')

            monitor_url = url_dict.get(service_name.lower() if isinstance(service_name, str) else service_name)
            instance_info['cluster_url'] = ""
            if monitor_url:
                instance_info['monitor_url'] = grafana_url + \
                                               monitor_url + f"?var-instance={service_ip}&kiosk=tv"
                if Service.objects.filter(
                        service_instance_name=service_instance_name).first() and Service.objects.filter(
                    service_instance_name=service_instance_name).first().cluster:
                    cluster_name = Service.objects.filter(
                        service_instance_name=service_instance_name).first().cluster.cluster_name
                    cluster_monitor_url = url_dict.get(f"{service_name}cluster", "")
                    instance_info[
                        'cluster_url'] = cluster_monitor_url + f"?var-cluster={cluster_name}&kiosk=tv" if cluster_monitor_url else ""
            else:
                try:
                    if service_name and ApplicationHub.objects.filter(
                            app_name=service_name
                    ).first() and ApplicationHub.objects.filter(
                        app_name=service_name
                    ).first().app_monitor and ApplicationHub.objects.filter(
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
                                       url_dict.get(
                                           'log',
                                           'nolog') + f"?var-env=default&var-app={service_name}" + f"&var-instance={service_instance_name}"
        else:
            instance_info['monitor_url'] = grafana_url + \
                                           url_dict.get('node', 'nohosts') + \
                                           f"?var-node={service_ip}&kiosk=tv"
            instance_info['log_url'] = None
    return explain_info
