#!/usr/bin/env python3
# encoding: utf-8
# Author: Jayden Liu
# Description: get apmConsumer Inspection data

import json
import os

from inspection_common import GetLocal_Ip, GetProcess_Survive, GetProcess_Port, GetProcess_Runtime, \
    GetProcess_Mem, GetProcessCPU_Pre, GetProcess_ServiceMem


def GetProcess_Pid():
    try:
        cmd = "ps -eo pid,command |grep 'ntpd' | grep -v grep"
        cmd_list = os.popen(cmd).read().strip('\n').split()
        pid = int(cmd_list[0])
        return pid
    except Exception:
        return None


def main(pid=GetProcess_Pid(), json_path="/data/app/data.json", **kwargs):
    process_message = dict()
    process_message["IP"] = GetLocal_Ip()
    process_message["service_status"] = GetProcess_Survive(pid)
    process_message["port_status"] = GetProcess_Port(pid)
    process_message['run_time'] = GetProcess_Runtime(pid)
    process_message['max_memory'] = GetProcess_ServiceMem(pid)
    process_message["mem_usage"] = GetProcess_Mem(pid)
    process_message["cpu_usage"] = GetProcessCPU_Pre(pid)
    process_message["log_level"] = None
    process_message["cluster_ip"] = None
    return json.dumps(process_message)


if __name__ == '__main__':
    print(main())
