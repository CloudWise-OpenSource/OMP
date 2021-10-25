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
            "scan_info": {
                "host": len(_h.hosts),
                "service": 0,
                "component": 0
            },
            "scan_result": {
                "all_target_num": _r.tag_total_num,
                "abnormal_target": _r.tag_error_num,
                "healthy": "100%"
            }
        },
        "risks": {
            "host_list": [],
            "service_list": []
        },
        "detail_dict": {},
        "file_name": f"{_h.inspection_name}.tar.gz"
    }

    # 主机巡检
    if handle == 'host':
        _r_data = []
        for i in _r.host_data:
            tmp = {
                "release_version": i.get('static_data').get('operate_system'),
                "host_massage": "",
                "mem_usage": f"{i.get('dynamic_data').get('rate_memory')}%",
                "cpu_usage": f"{i.get('dynamic_data').get('rate_cpu')}%",
                "disk_usage_root":
                    f"{i.get('dynamic_data').get('rate_exchange_disk')}%",
                "sys_load": i.get('dynamic_data').get('load'),
                "run_time": f"{i.get('dynamic_data').get('run_time')}%",
                "host_ip": i.get('static_data').get('ip'),
                "memory_top": [],
                "cpu_top": [],
                "kernel_parameters": [],
                "basic": [
                    {"name": "IP",
                     "name_cn": "主机IP",
                     "value": i.get('static_data').get('ip')},
                    {"name": "hostname",
                     "name_cn": "主机名",
                     "value": i.get('static_data').get('host_name')},
                    {"name": "kernel_version",
                     "name_cn": "内核版本",
                     "value": ""},
                    {"name": "selinux",
                     "name_cn": "SElinux 状态",
                     "value": ""},
                    {"name": "max_openfile",
                     "name_cn": "最大打开文件数",
                     "value":
                         i.get('dynamic_data').get('total_file_descriptor')},
                    {"name": "iowait",
                     "name_cn": "IOWait",
                     "value": i.get('dynamic_data').get('rate_io_wait')},
                    {"name": "inode_usage",
                     "name_cn": "inode 使用率",
                     "value": {
                         "/": f"{i.get('dynamic_data').get('rate_max_disk')}%"
                        }},
                    {"name": "now_time",
                     "name_cn": "当前时间",
                     "value": i.get('dynamic_data').get('now_time')},
                    {"name": "run_process",
                     "name_cn": "进程数",
                     "value": 0},
                    {"name": "umask",
                     "name_cn": "umask",
                     "value": {"user": "commonuser", "umask": "0022"}},
                    {"name": "bandwidth",
                     "name_cn": "带宽",
                     "value": i.get('dynamic_data').get('network_bytes_total')},
                    {"name": "throughput",
                     "name_cn": "IO",
                     "value": i.get('dynamic_data').get('disk_io')},
                    {"name": "zombies_process",
                     "name_cn": "僵尸进程",
                     "value": []}
                ]
            }
            _r_data.append(tmp)

        ret['detail_dict']['host'] = _r_data

    # 组件巡检
    if handle == 'service':
        _r_data = []
        for i in _r.serv_data:
            tmp = {
                "host_ip": i.get('ip'),
                "cluster_name": '',
                "cpu_usage": "0.00%",
                "log_level": '',
                "mem_usage": "1.32%",
                "run_time": "02:12:37",
                "service_name": "mysql",
                "service_port": '',
                "service_status": 'true',
                "service_type": "2",
                "basic": [
                    {"name": "max_memory",
                     "name_cn": "最大内存",
                     "value": ''},
                    {"name": "port_status",
                     "name_cn": "监听端口",
                     "value": ["18103"]},
                    {"name": "IP",
                     "name_cn": "IP地址",
                     "value": "10.0.3.20"},
                    {"name": "process_threads",
                     "name_cn": "线程数量",
                     "value": 67},
                    {"name": "conn_num",
                     "name_cn": "连接数量",
                     "value": "15"},
                    {"name": "aborted_clients",
                     "name_cn": "中断连接数",
                     "value": "30"},
                    {"name": "failure_connect",
                     "name_cn": "失败连接数",
                     "value": "3446"},
                    {"name": "slow_query",
                     "name_cn": "慢查询",
                     "value": ''},
                    {"name": "backup_status",
                     "name_cn": "数据同步状态",
                     "value": "no slave"}
                ]
            }
            _r_data.append(tmp)

        ret['detail_dict']['component'] = _r_data

    # 深度巡检
    if handle == 'deep':
        # 服务平面图
        ret["service_topology"] = _r.serv_plan
        ret['detail_dict']['host'] = [
            {
                "release_version": '',
                "host_massage": "",
                "mem_usage": '',
                "cpu_usage": '',
                "disk_usage_root": '',
                "sys_load": '',
                "run_time": '',
                "host_ip": '',
                "memory_top": [],
                "cpu_top": [],
                "kernel_parameters": [],
                "basic": [
                    {"name": "IP",
                     "name_cn": "主机IP",
                     "value": ''},
                    {"name": "hostname",
                     "name_cn": "主机名",
                     "value": ''},
                    {"name": "kernel_version",
                     "name_cn": "内核版本",
                     "value": ""},
                    {"name": "selinux",
                     "name_cn": "SElinux 状态",
                     "value": ""},
                    {"name": "max_openfile",
                     "name_cn": "最大打开文件数",
                     "value": ''},
                    {"name": "iowait",
                     "name_cn": "IOWait",
                     "value": ''},
                    {"name": "inode_usage",
                     "name_cn": "inode 使用率",
                     "value": {
                         "/": ''
                     }},
                    {"name": "now_time",
                     "name_cn": "当前时间",
                     "value": ''},
                    {"name": "run_process",
                     "name_cn": "进程数",
                     "value": 0},
                    {"name": "umask",
                     "name_cn": "umask",
                     "value": {"user": "commonuser", "umask": "0022"}},
                    {"name": "bandwidth",
                     "name_cn": "带宽",
                     "value": ''},
                    {"name": "throughput",
                     "name_cn": "IO",
                     "value": ''},
                    {"name": "zombies_process",
                     "name_cn": "僵尸进程",
                     "value": []}
                ]
            }
        ]
        ret['detail_dict']["service"] = [
            {
                "host_ip": "10.0.3.20",
                "service_status": 'true',
                "run_time": "2 day 13:35:13",
                "log_level": 'null',
                "mem_usage": "2.48%",
                "cpu_usage": "0.04%",
                "service_name": "mysql",
                "service_port": 18103,
                "cluster_name": '',
                "service_type": "2",
                "basic": [
                     {"name": "max_memory",
                      "name_cn": "最大内存",
                      "value": ''},
                     {"name": "port_status",
                      "name_cn": "监听端口",
                      "value": ["18103"]},
                     {"name": "IP",
                      "name_cn": "IP地址",
                      "value": "10.0.3.20"},
                     {"name": "process_threads",
                      "name_cn": "线程数量",
                      "value": 67},
                     {"name": "conn_num",
                      "name_cn": "连接数量",
                      "value": "15"},
                     {"name": "aborted_clients",
                      "name_cn": "中断连接数",
                      "value": "30"},
                     {"name": "failure_connect",
                      "name_cn": "失败连接数",
                      "value": "3446"},
                     {"name": "slow_query",
                      "name_cn": "慢查询",
                      "value": ''},
                     {"name": "backup_status",
                      "name_cn": "数据同步状态",
                      "value": "no slave"}
                 ]}
        ]

    return ret
