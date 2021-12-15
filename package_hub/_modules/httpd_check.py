#!/usr/bin/env python3
# encoding: utf-8
# Author: Darren Liu
# Description: get httpd Inspection data
import json
import os.path as up
import psutil

from inspection_common import GetLocal_Ip, GetProcess_Survive, GetProcess_Port, GetProcess_Runtime, \
    GetProcess_Mem, GetProcessCPU_Pre, GetProcess_ServiceMem, GetCluster_IP


def GetProcess_Pid():
    try:
        for pnum in psutil.pids():
            try:
                p = psutil.Process(pnum)
                if p.name() == 'httpd' and 'httpd/bin/httpd' in p.exe():
                    pid = int(p.ppid())
                    if pid != 1:
                        return pid
                    else:
                        return pnum
            except Exception:
                pass
    except Exception:
        return None


def GetProcess_LogLevel(pid):
    if pid and type(pid).__name__ == 'int':
        try:
            log_level = ''
            p = psutil.Process(pid)
            httpd_path = up.abspath(up.join(p.exe(), "../.."))
            f = open('%s/conf/httpd.conf' % (httpd_path), 'r')
            for lines_list in f:
                if 'access_' in lines_list:
                    log_level = 'access'
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
    process_message['max_memory'] = GetProcess_ServiceMem(pid)
    process_message["mem_usage"] = GetProcess_Mem(pid)
    process_message["cpu_usage"] = GetProcessCPU_Pre(pid)
    process_message["log_level"] = GetProcess_LogLevel(pid)
    process_message["cluster_ip"] = GetCluster_IP(
        json_path=json_path, service_name="httpd")
    return json.dumps(process_message)


if __name__ == '__main__':
    print(main())
