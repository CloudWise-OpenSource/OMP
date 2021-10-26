# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/10/14 4:01 下午
# Description:
import json
import requests
import traceback
from datetime import datetime
from db_models.models import MonitorUrl
from db_models.models import InspectionHistory, InspectionReport


class Prometheus(object):
    def __init__(self):
        # prometheus 的 ip:port
        self.address = MonitorUrl.objects.get(name='prometheus').monitor_url

    def query(self, expr):
        url = 'http://' + self.address + '/api/v1/query?query=' + expr
        try:
            rsp = json.loads(requests.get(url=url, timeout=0.5
                                          ).content.decode('utf8', 'ignore'))
            if rsp.get('status') == 'success':
                return True, rsp.get('data'), 'success'
            else:
                return False, {}, 'fail'
        except Exception as e:
            return False, {}, traceback.format_exc(e)


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
    his_obj.update(end_time=now, duration=(now - his_obj[0].start_time).seconds,
                   inspection_status=2)
    if host_data:
        # 反填巡检报告InspectionReport表，主机列表host_data字段
        InspectionReport.objects.filter(id=report_id).update(
            host_data=host_data)
    if serv_data:
        # 反填巡检报告InspectionReport表，服务列表serv_data字段
        InspectionReport.objects.filter(id=report_id).update(
            serv_data=serv_data)
    if serv_plan:
        # 反填巡检报告InspectionReport表，服务列表serv_plan字段
        InspectionReport.objects.filter(id=report_id).update(
            serv_plan=serv_plan)
    if risk_data:
        # 反填巡检报告InspectionReport表，服务列表risk_data字段
        InspectionReport.objects.filter(id=report_id).update(
            risk_data=risk_data)
    # 反填巡检报告InspectionReport表scan_info、scan_result
    InspectionReport.objects.filter(id=report_id).update(
        scan_info=scan_info, scan_result=scan_result, file_name=file_name)
