# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/10/25 10:30 上午
# Description:


def joint_json_data(handle, _r, _h):
    ret = {
        "summary": {
            "task_info": {
                "task_name": _h.inspection_name,
                "operator": _h.inspection_operator,
                "task_status": _h.inspection_status
            },
            "time_info": {
                "start_time": _h.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                "end_time":
                    _h.end_time.strftime('%Y-%m-%d %H:%M:%S') if
                    _h.end_time else '',
                "cost": _h.duration
            },
            "scan_info": _r.scan_info,
            "scan_result": _r.scan_result
        },
        "risks": _r.risk_data
        if _r.risk_data else {"host_list": [], "service_list": []},
        "detail_dict": {},
        "file_name": _r.file_name
    }

    # 主机巡检
    if handle == 'host':
        ret['detail_dict']['host'] = _r.host_data

    # 组件巡检
    if handle == 'service':
        ret['detail_dict']['component'] = _r.serv_data

    # 深度巡检
    if handle == 'deep':
        # 服务平面图
        ret["service_topology"] = _r.serv_plan if _r.serv_plan else []
        ret['detail_dict']['host'] = _r.host_data
        ret['detail_dict']["service"] = _r.serv_data
        ret['detail_dict']["database"] = []
        ret['detail_dict']["component"] = []

    return ret
