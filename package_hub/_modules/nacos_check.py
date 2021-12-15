#!/usr/bin/env python3
# encoding: utf-8
# Author: Darren Liu
# Description: get nacos Inspection data

import json
import psutil

from inspection_common import GetLocal_Ip, GetProcess_Survive, GetProcess_Port, GetProcess_Runtime, \
    GetProcess_Mem, GetProcessCPU_Pre, GetCluster_IP, GetProcess_ServiceMem


def GetProcess_Pid():
    try:
        for pnum in psutil.pids():
            try:
                p = psutil.Process(pnum)
                if p.name() == 'java' and 'nacos' in p.cwd():
                    pid = pnum
                    return pid
            except Exception:
                pass
    except Exception:
        return None


def GetProcess_LogLevel(pid):
    if pid and type(pid).__name__ == 'int':
        try:
            p = psutil.Process(pid)
            nacos_path = p.cwd()
            f = open('%s/conf/nacos-logback.xml' % (nacos_path), 'r')
            context = f.readlines()
            nacos_log_level = context[-5].strip('\n').split('"')
            log_level = nacos_log_level[1]
        except Exception:
            log_level = None
        return log_level
    else:
        return None


def main(pid=GetProcess_Pid(), json_path="/data/app/data.json", **kwargs):
    process_message = dict()
    process_message["IP"] = GetLocal_Ip()
    process_message["service_status"] = GetProcess_Survive(pid)
    process_message["port_status"] = GetProcess_Port(pid)
    process_message['run_time'] = GetProcess_Runtime(pid)
    process_message['max_memory'] = GetProcess_ServiceMem(pid, is_java=True)
    process_message["mem_usage"] = GetProcess_Mem(pid)
    process_message["cpu_usage"] = GetProcessCPU_Pre(pid)
    process_message["log_level"] = GetProcess_LogLevel(pid)
    process_message["cluster_ip"] = GetCluster_IP(
        json_path=json_path, service_name="nacos")
    return json.dumps(process_message)


if __name__ == '__main__':
    print(main())
