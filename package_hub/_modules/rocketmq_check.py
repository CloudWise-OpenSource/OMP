#!/usr/bin/env python3
# encoding: utf-8
# Auther: Darren Liu
# Description: get rocketmq  Inspection data

import os
import re

import psutil
import time
import json
import socket


def GetProcess_Pid():
    try:
        pid_list = []
        for pnum in psutil.pids():
            try:
                p = psutil.Process(pnum)
                if p.name() == "java":
                    for cmd_str in p.cmdline():
                        if "rocketmq.broker" in cmd_str:
                            pid_list.append(pnum)
                        if "rocketmq.namesrv" in cmd_str:
                            pid_list.append(pnum)
            except:
                pass
        return pid_list
    except:
        return []


def GetLocal_Ip():
    try :
        csock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        csock.connect(( '8.8.8.8' , 80 ))
        (addr, port) = csock.getsockname()
        csock.close()
        return addr
    except socket.error:
        return "127.0.0.1"


def GetProcess_Survive(pid_list):
    if pid_list and isinstance(pid_list, list):
        return "True"
    else:
        return "False"


def GetProcess_Port(pid_list):
    if not pid_list or not isinstance(pid_list, list):
        return None
    port = []
    for pid in pid_list:
        try:
            cmd =  'ss -tnlp | grep '+str(pid)
            port_list = os.popen(cmd).read().strip('\n').split('\n')
            for line_list in port_list:
                if not line_list:
                    continue
                line = line_list.split()
                port_aa = line[3].split(':')
                port.append(port_aa[-1])
        except:
            return port
    return list(set(port))


def GetProcess_Runtime(pid_list):
    if not pid_list or not isinstance(pid_list, list):
        return None
    try:
        cmd =  'ps -eo pid,etime|grep '+str(pid_list[0])
        etime = os.popen(cmd).read().strip('\n').split()
        # if '-' in etime[1]:
        #     runtime = etime[1].replace('-', ' day ')
        # else:
        #     runtime = etime[1]

        runtime = etime[1].replace(
            '-', '天').replace(':', '小时', 1).replace(':', '分钟', 1) + '秒'
    except:
        runtime = None
    return runtime

_timer = getattr(time, 'monotonic', time.time)
num_cpus = psutil.cpu_count() or 1


def timer():
    return _timer() * num_cpus


def GetProcessCPU_Pre(pid_list):
    if not pid_list or not isinstance(pid_list, list):
        return None
    cpus_sum = 0
    pid_cpuinfo = {}
    for pid in pid_list:
        try:
            p = psutil.Process(pid)
            pt = p.cpu_times()
            st1,pt1_0,pt1_1 = timer(),pt.user,pt.system   # new
            st0,pt0_0,pt0_1 = pid_cpuinfo.get(pid,(0,0,0)) # old
            delta_proc = (pt1_0 - pt0_0) + (pt1_1 - pt0_1)
            delta_time = st1 - st0
            cpus_percent = ((delta_proc / delta_time) * 100)
            cpus_sum += cpus_percent
            pid_cpuinfo[pid] = [st1, pt1_0, pt1_1]
        except:
            pass
    cpu_usage = "{:.2f}".format(cpus_sum) + "%"
    return cpu_usage


def GetProcess_Mem(pid_list):
    if not pid_list or not isinstance(pid_list, list):
        return None
    process_mem_sum = 0
    for pid in pid_list:
        try:
            p = psutil.Process(pid)
            process_mem = p.memory_percent()
            process_mem_sum += process_mem
        except:
            pass
    mem_usage = "{:.2f}".format(process_mem_sum) + "%"
    return mem_usage


def GetProcess_ServiceMem(pid_list):
    if not pid_list or not isinstance(pid_list, list):
        return None
    service_mem_sum = 0
    for pid in pid_list:
        try:
            cmd = 'ps -eo pid,command|grep %s' % (pid)
            process_list = os.popen(cmd).read().strip('\n').split('-ms')
            process_mem = process_list[-1].split()
            service_mem = process_mem[0]
            service_mem_sum += service_mem
        except:
            pass
    return service_mem_sum if service_mem_sum else None


def GetProcess_LogLevel(pid_list):
    if not pid_list or not isinstance(pid_list, list):
        return None
    log_level_set = set()
    pid = pid_list[0]
    try:
        p = psutil.Process(pid)
        path_str = re.compile(r"(.*/rocketmq/conf)/.*")
        project_path = ""
        for cmd_str in p.cmdline():
            if path_str.findall(cmd_str):
                project_path = path_str.findall(cmd_str)[0]
        if not project_path:
            return ""
        for log_file in ['logback_broker.xml', 'logback_namesrv.xml', 'logback_tools.xml']:
            f = open(f'{project_path}/{log_file}', 'r')
            for lines_list in f:
                if '<level value' in lines_list:
                    log_level = lines_list.strip().replace('<level value="', '').replace('"/>', '')
                    log_level_set.add(log_level)
                    break
            f.close()
    except:
        pass
    return ",".join(log_level_set)


def main(pid_list=GetProcess_Pid(),**kwargs):
    process_message = {}
    process_message["IP"] = GetLocal_Ip()
    process_message["service_status"] = GetProcess_Survive(pid_list)
    process_message["port_status"] = GetProcess_Port(pid_list)
    process_message['run_time'] = GetProcess_Runtime(pid_list)
    process_message['max_memory'] = GetProcess_ServiceMem(pid_list)
    process_message["mem_usage"] = GetProcess_Mem(pid_list)
    process_message["cpu_usage"] = GetProcessCPU_Pre(pid_list)
    process_message["log_level"] = GetProcess_LogLevel(pid_list)
    return json.dumps(process_message)


if __name__ == '__main__':
    print(main())
