# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/10/14 4:01 下午
# Description:
import json
import logging
import requests
from datetime import datetime
from db_models.models import MonitorUrl
from db_models.models import InspectionHistory, InspectionReport

logger = logging.getLogger("server")


class Prometheus(object):
    """
    prometheus
    执行prosql查询数据、查询alerts
    """

    def __init__(self):
        # prometheus 的 ip:port
        self.address = MonitorUrl.objects.get(name='prometheus').monitor_url

    def query(self, expr):
        """
        请求prometheus开放接口，执行prosql，查询数据
        :para expr: 需要执行的sql
        :return: 查询到的实时数据
        """
        url = f"http://{self.address}/api/v1/query?query={expr}"
        try:
            rsp = json.loads(requests.get(url=url, timeout=0.5
                                          ).content.decode('utf8', 'ignore'))
            if rsp.get('status') == 'success':
                return True, rsp.get('data')
            else:
                return False, {}
        except Exception as e:
            logger.error(f"Query query from prometheus error: {str(e)}")
            return False, {}

    @staticmethod
    def clean_alert(alerts):
        """
        清洗告警，去掉同类不同级别告警
        :param alerts:
        :return:
        """
        unique_alert_dic = dict()
        clean_alerts = list()
        for item in alerts:
            _key = item.get("labels", {}).get("alertname", "") + \
                item.get("labels", {}).get("instance", "")
            _level = item.get("labels", {}).get("severity", "")
            if _key not in unique_alert_dic:
                unique_alert_dic[_key] = {
                    "warning": "",
                    "critical": ""
                }
            unique_alert_dic[_key][_level] = item
        for key, value in unique_alert_dic.items():
            if value.get("critical"):
                clean_alerts.append(value.get("critical"))
            else:
                clean_alerts.append(value.get("warning"))
        return clean_alerts

    @staticmethod
    def unified_job(is_success, ret):
        """
        实例方法 返回值统一处理
        :ret: 返回值
        :is_success: 请求是否成功
        """
        if is_success:
            if ret.get('result'):
                return ret['result'][0].get('value')[1]
            else:
                return 0
        else:
            return 0

    def query_alerts(self):
        url = f'http://{self.address}/api/v1/alerts'
        try:
            rsp = json.loads(requests.get(url=url, timeout=0.5
                                          ).content.decode('utf8', 'ignore'))
            if rsp.get('status') == 'success':
                # 处理重复级别告警问题 jon.liu
                alerts = rsp.get('data').get('alerts')
                return self.clean_alert(alerts)
            else:
                return {}
        except Exception as e:
            logger.error(f"Query Alerts from prometheus error: {str(e)}")
            return {}


def back_fill(history_id, report_id, host_data=None, serv_data=None,
              serv_plan=None, risk_data=None, scan_info=None, scan_result=None,
              file_name=None):
    """
    异步反填报告数据
    :history_id : 巡检历史记录id
    :report_id : 巡检报告id
    :host_data : 主机巡检数据
    :serv_data : 组件巡检数据
    :serv_plan : 服务
    :risk_data : 报警数据
    :scan_info : 扫描统计
    :scan_result : 分析结果
    :file_name : 导出文件名
    """
    # 反填巡检历史记录InspectionHistory表，结束时间end_time、巡检用时duration字段、巡检状态inspection_status
    now = datetime.now()
    his_obj = InspectionHistory.objects.filter(id=history_id)
    duration = (now - his_obj[0].start_time).seconds
    duration = duration if duration > 0 else 1
    his_obj.update(end_time=now, duration=duration, inspection_status=2)

    # 反填巡检报告InspectionReport表
    rep_obj = InspectionReport.objects.filter(id=report_id)
    if host_data:
        # 反填巡检报告InspectionReport表，主机列表host_data字段
        rep_obj.update(host_data=host_data)
    if serv_data:
        # 反填巡检报告InspectionReport表，服务列表serv_data字段
        rep_obj.update(serv_data=serv_data)
    if serv_plan:
        # 反填巡检报告InspectionReport表，服务列表serv_plan字段
        rep_obj.update(serv_plan=serv_plan)
    if risk_data:
        # 反填巡检报告InspectionReport表，服务列表risk_data字段
        rep_obj.update(risk_data=risk_data)

    # 反填巡检报告InspectionReport表scan_info、scan_result
    rep_obj.update(
        scan_info=scan_info, scan_result=scan_result, file_name=file_name)
