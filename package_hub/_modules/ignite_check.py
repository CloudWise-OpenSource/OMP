#!/usr/bin/env python3
# encoding: utf-8
# Author: Darren Liu
# Description: get ignite Inspection data

import json
import psutil

from inspection_common import GetLocal_Ip, GetProcess_Survive, GetProcess_Port, GetProcess_Runtime, \
    GetProcess_Mem, GetProcessCPU_Pre, GetProcess_ServiceMem, GetCluster_IP


def GetProcess_Pid():
    try:
        for pnum in psutil.pids():
            try:
                p = psutil.Process(pnum)
                if p.name() == 'java' and 'ignite' in p.cwd():
                    pid = pnum
                    return pid
            except Exception:
                pass
    except Exception:
        return None


def GetProcess_LogLevel(pid):
    log_level = None
    if pid and type(pid).__name__ == 'int':
        try:
            p = psutil.Process(pid)
            ignite_path = p.cwd()
            f = open('%s/config/ignite-log4j.xml' % (ignite_path), 'r')
            for lines_list in f:
                if '<level value="INFO"/>' in lines_list:
                    ignite_log_level = lines_list.strip('\n').split('"')
                    log_level = ignite_log_level[1]
            return log_level
        except Exception:
            return None
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
        json_path=json_path, service_name="ignite")
    return json.dumps(process_message)


if __name__ == '__main__':
    print(main())
