#!/usr/bin/env python3
# encoding: utf-8
# Author: Darren Liu
# Description: get tengine Inspection data
import json
import os
import os.path as up
import psutil

from package_hub._modules.inspection_common import GetLocal_Ip, GetProcess_Survive, GetProcess_Port, GetProcess_Runtime, \
    GetProcess_Mem, GetProcessCPU_Pre, GetCluster_IP


def GetProcess_Pid():
    try:
        for pnum in psutil.pids():
            try:
                p = psutil.Process(pnum)
                if p.name() == 'nginx' and 'master' in p.cmdline():
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
            nginx_path = up.abspath(up.join(p.exe(), "../.."))
            cmd = 'grep access_log  %s/conf/vhost/*.conf |wc -l' % (nginx_path)
            log_list = os.popen(cmd).read().strip('\n')
            if int(log_list) == 0:
                log_level = 'error'
            else:
                log_level = 'access'
            return log_level
        except Exception:
            return None
    else:
        return None


def main(pid=GetProcess_Pid(), json_path="/data/app/data.json", **kwargs):
    process_message = {}
    process_message["IP"] = GetLocal_Ip()
    process_message["service_status"] = GetProcess_Survive(pid)
    process_message["port_status"] = GetProcess_Port(pid)
    process_message['run_time'] = GetProcess_Runtime(pid)
    process_message['max_memory'] = None
    process_message["mem_usage"] = GetProcess_Mem(pid)
    process_message["cpu_usage"] = GetProcessCPU_Pre(pid)
    process_message["log_level"] = GetProcess_LogLevel(pid)
    process_message["cluster_ip"] = GetCluster_IP(
        json_path=json_path, service_name="tengine")
    return json.dumps(process_message)


if __name__ == '__main__':
    print(main())
