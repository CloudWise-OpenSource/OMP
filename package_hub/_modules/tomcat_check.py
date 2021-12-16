#!/usr/bin/env python3
# encoding: utf-8
# Author: Darren Liu
# Description: get mysql Inspection data
import json
import os

import psutil

from inspection_common import GetProcess_Runtime, GetLocal_Ip, GetProcess_Survive, GetProcess_Port, GetProcess_Mem, \
    GetProcessCPU_Pre


def GetProcess_Pid(process_name='tomcat'):
    cmd = "ps aux|grep {}|grep -v grep".format(process_name)
    try:
        process_info = os.popen(cmd).read().split()
        return int(process_info[1])
    except Exception:
        return None


def GetProcess_Threads(pid):
    if pid and type(pid).__name__ == 'int':
        try:
            p = psutil.Process(pid)
            process_threads = p.num_threads()
            return process_threads
        except Exception:
            return None
    else:
        return None


def main():
    pid = GetProcess_Pid()
    if pid is None:
        return json.dumps({})
    process_message = dict()
    process_message["IP"] = GetLocal_Ip()
    process_message["service_status"] = GetProcess_Survive(pid)
    process_message["port_status"] = GetProcess_Port(pid)
    process_message['run_time'] = GetProcess_Runtime(pid)
    process_message["mem_usage"] = GetProcess_Mem(pid)
    process_message["cpu_usage"] = GetProcessCPU_Pre(pid)
    process_message['max_memory'] = None
    process_message["log_level"] = None
    process_message["process_threads"] = GetProcess_Threads(pid)
    return json.dumps(process_message)


if __name__ == '__main__':
    print(main())
