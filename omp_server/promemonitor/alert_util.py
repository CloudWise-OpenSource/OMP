import datetime
import logging
import traceback

import pytz
from omp_server.settings import TIME_ZONE
from db_models.models import Host
from promemonitor.grafana_url import explain_url

logger = logging.getLogger('server')


def get_service_type(ip, service_name):
    """
    获取服务的中文名称以及服务分类
    :param ip: ip
    :param service_name: 服务名称
    :type service_name str
    :return: product_cn_name, service_type
    """
    product_cn_name = service_name
    service_type = ip
    return product_cn_name, service_type


def get_monitor_url(ele):
    return explain_url(ele)[0].get('monitor')


def get_log_url(ele):
    return explain_url(ele)[0].get('monitor_log')


def utc_to_local(utc_time_str, utc_format='%Y-%m-%dT%H:%M:%SZ'):
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


class AlertAnalysis:

    def __init__(self, item):
        """
        解析prometheus返回的信息
        :param item:
            {
              "status": "resolved",
              "labels":
                {
                    "alertname":"app state",
                    "app":"nbdServer",
                    "instance":"10.0.9.61:18215",
                    "ip":"10.0.9.61",
                    "job":"10.0.9.61",
                    "severity":"critical"
                },
              "annotations":
                {
                  "consignee":"2871253303@qq.com",
                  "description":"主机 10.0.12.35 中的 zookeeper_exporter 已经down掉超过一分钟.",
                  "summary":"app state(instance 10.0.9.61:18215)"
                },
              "state":"firing",
              "activeAt":"2021-04-10T08:36:23.838961588Z",
              "value":"0e+00",
              "fingerprint": "" # 非
            }
        """
        self.item = item
        self.labels = self.item.get("labels", {})
        self.annotations = self.item.get("annotations", {})
        self.fingerprint = self.item.get("fingerprint", "")

    @staticmethod
    def _get(items, key):
        return items.get(key, "DEFAULT_DATA")

    @property
    def is_resolved(self):
        return self.item.get("status") == 'resolved'

    @property
    def is_alert(self):
        return self._get(self.labels, "severity") in ["critical", "warning"]

    def node_exporter(self):
        return dict(
            alert_type="host",
            alert_host_ip=self._get(self.labels, "instance"),
            alert_service_name="",
            alert_service_type="",
            alert_service_en_type=""
        )

    def exporter(self):
        alert_host_ip = self._get(self.labels, "instance")
        alert_service = self._get(self.labels, "job")
        alert_service_name = alert_service.replace("Exporter", "").strip()
        alert_service_type, alert_service_en_type = get_service_type(
            alert_host_ip, alert_service_name)
        return dict(
            alert_type="service",
            alert_host_ip=self._get(self.labels, "instance"),
            alert_service_name=alert_service_name,
            alert_service_type=alert_service_type,
            alert_service_en_type=alert_service_en_type
        )

    def other(self):
        alert_host_ip = self._get(self.labels, "ip")
        alert_service_name = self._get(self.labels, "app").strip()
        alert_service_type, alert_service_en_type = get_service_type(
            alert_host_ip, alert_service_name)
        return dict(
            alert_type="service",
            alert_host_ip=alert_host_ip,
            alert_service_name=alert_service_name,
            alert_service_type=alert_service_type,
            alert_service_en_type=alert_service_en_type
        )

    def get_alert_time(self):
        start_time = self.item.get("startsAt", "")
        if not start_time:
            start_time = self.item.get("activeAt", "")
        return utc_to_local(utc_time_str=start_time)

    def analysis_labels(self):
        old_alert_type = self._get(self.labels, "job")
        if old_alert_type == "nodeExporter":
            kwargs = self.node_exporter()
        elif "Exporter" in old_alert_type:
            kwargs = self.exporter()
        else:
            kwargs = self.other()
        kwargs["status"] = self.item.get("status", "firing")
        kwargs["alert_level"] = self._get(self.labels, "severity")
        kwargs["alertname"] = self._get(self.labels, "alertname")
        kwargs["fingerprint"] = self.fingerprint
        kwargs.update(alert_time=self.get_alert_time())
        if kwargs["alert_type"] == "service":
            kwargs["monitor"] = get_monitor_url(
                [{
                    "ip": kwargs.get("alert_host_ip"),
                    "type": "service",
                    "instance_name": kwargs.get("alert_service_name")
                }]
            )
            kwargs["monitor_log"] = get_log_url(
                [{
                    "ip": kwargs.get("alert_host_ip"),
                    "type": "service",
                    "instance_name": kwargs.get("alert_service_name")
                }]
            )
        else:
            kwargs["monitor"] = get_monitor_url(
                [{
                    "ip": kwargs.get("alert_host_ip"),
                    "type": "host",
                    "instance_name": "node"
                }]
            )
            kwargs["monitor_log"] = get_log_url(
                [{
                    "ip": kwargs.get("alert_host_ip"),
                    "type": "host",
                    "instance_name": "node"
                }]
            )
        return kwargs

    def analysis_annotations(self):
        return dict(
            alert_receiver=self._get(self.annotations, "consignee"),
            #  服务down：主机 10.0.12.35 中的 zookeeper 已经down掉超过一分钟.
            #  服务exporter down：
            #  主机 10.0.12.35 中的 zookeeper_exporter 已经down掉超过一分钟.
            alert_describe=self._get(self.annotations, "description")
        )

    def __call__(self, env_id=0, *args, **kwargs):
        """
        :param env_id:
        :param args:
        :param kwargs:
        :return: {
            "alert_type": 告警类型 host or service,
            "alert_host_ip": 告警来自哪个主机,
            "alert_host_system": 告警来自主机的系统,
            "alert_service_name": 告警服务名称,
            "alert_service_type": 告警服务所属产品名称,
            "alert_service_en_type": 告警服务类型，self_dev component database,
            "alert_level": 告警级别,
            "alert_describe": 告警描述,
            "alert_receiver": 告警接收人,
            "alert_resolve": 告警解决方案,
            "alert_time": 告警发生时间,
            "monitor": 跳转grafana地址,
            "monitor_log": 日志跳转url（仅服务存在）,
            "fingerprint": 告警对应的唯一标识,
            "status": 告警状态： resolved，恢复；firing：告警 # 推送使用，其他无用,
            "alertname": 告警指标： # 推送使用，其他无用,
        }
        """
        # if not self.is_alert:
        #     return {}
        alert_info = self.analysis_labels()
        print(alert_info)
        if alert_info["alert_type"] == "host":
            host = Host.objects.filter(
                ip=alert_info["alert_host_ip"]).first()
            if not host:
                return {}
            alert_info["env_id"] = host.env_id
            alert_info["alert_host_instance_name"] = host.instance_name
        else:
            return {}  # TODO 待应用开发完成
        alert_info.update(**self.analysis_annotations())
        # if env_id and int(env_id) != alert_info["env_id"]:
        #     return {}  # TODO 等待env开发完成
        print(alert_info)
        return alert_info

    def analysis_alert(self):
        pass
