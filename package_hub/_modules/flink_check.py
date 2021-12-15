#!/usr/bin/env python3
# encoding: utf-8
# Author: Darren Liu
# Description: get flink Inspection data

import json
import os
import socket
import time

import psutil


def GetProcess_Pid():
    try:
        for pnum in psutil.pids():
            try:
                p = psutil.Process(pnum)
                if p.name() == 'java' and "flink" in p.cwd():
                    pid = pnum
                    return pid
            except Exception:
                pass
    except Exception:
        return None


def GetLocal_Ip():
    try:
        csock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        csock.connect(('8.8.8.8', 80))
        (addr, port) = csock.getsockname()
        csock.close()
        return addr
    except socket.error:
        return "127.0.0.1"


def GetProcess_Survive(pid):
    if pid and type(pid).__name__ == 'int':
        return "True"
    else:
        return "False"


def GetProcess_Port(pid):
    try:
        if pid and type(pid).__name__ == 'int':
            port = []
            # p = psutil.Process(pid)
            cmd = 'ss -tnlp | grep ' + str(pid)
            port_list = os.popen(cmd).read().strip('\n').split('\n')
            for line_list in port_list:
                if not line_list:
                    continue
                line = line_list.split()
                port_aa = line[3].split(':')
                port.append(port_aa[-1])
            port = list(set(port))
            return port
        else:
            return None
    except Exception:
        return None


def GetProcess_Runtime(pid):
    if pid and type(pid).__name__ == 'int':
        try:
            cmd = 'ps -eo pid,etime|grep ' + str(pid)
            etime = os.popen(cmd).read().strip('\n').split()
            if '-' in etime[1]:
                runtime = etime[1].replace('-', ' day ')
            else:
                runtime = etime[1]
        except Exception:
            runtime = None
    else:
        runtime = None
    return runtime


_timer = getattr(time, 'monotonic', time.time)
num_cpus = psutil.cpu_count() or 1


def timer():
    return _timer() * num_cpus


def GetProcessCPU_Pre(pid):
    if pid and type(pid).__name__ == 'int':
        try:
            pid_cpuinfo = {}
            p = psutil.Process(pid)
            pt = p.cpu_times()
            st1, pt1_0, pt1_1 = timer(), pt.user, pt.system  # new
            st0, pt0_0, pt0_1 = pid_cpuinfo.get(pid, (0, 0, 0))  # old
            delta_proc = (pt1_0 - pt0_0) + (pt1_1 - pt0_1)
            delta_time = st1 - st0
            cpus_percent = ((delta_proc / delta_time) * 100)
            pid_cpuinfo[pid] = [st1, pt1_0, pt1_1]
            cpu_usage = "{:.2f}".format(cpus_percent) + "%"
        except Exception:
            cpu_usage = None
    else:
        cpu_usage = None
    return cpu_usage


def GetProcess_Mem(pid):
    if pid and type(pid).__name__ == 'int':
        try:
            p = psutil.Process(pid)
            process_mem = p.memory_percent()
            mem_usage = "{:.2f}".format(process_mem) + "%"
        except Exception:
            return None
    else:
        mem_usage = None
    return mem_usage


def GetProcess_ServiceMem(pid):
    if pid and type(pid).__name__ == 'int':
        try:
            cmd = 'ps -eo pid,command|grep %s' % (pid)
            process_list = os.popen(cmd).read().strip('\n').split('-Xms')
            process_mem = process_list[-1].split()
            service_mem = process_mem[0]
            return service_mem
        except Exception:
            return None
    else:
        return None


# def GetProcess_LogLevel(pid):
#     if pid and type(pid).__name__ == 'int':
#         try:
#             p = psutil.Process(pid)
#             domm_path = p.cwd()
#             f = open('%s/conf/log4j2.xml' % (domm_path),'r')
#             for lines_list in f:
#                 if '<Root level=' in lines_list:
#                     log_level = lines_list.strip().replace('<Root level="${env:CW_DOMM_LOG_LEVEL:-','').replace('}">','')
#         except Exception:
#             log_level = None
#         return log_level
#     else:
#         return None


def main(pid=GetProcess_Pid(), **kwargs):
    process_message = dict()
    process_message["IP"] = GetLocal_Ip()
    process_message["service_status"] = GetProcess_Survive(pid)
    process_message["port_status"] = GetProcess_Port(pid)
    process_message['run_time'] = GetProcess_Runtime(pid)
    process_message['max_memory'] = None
    process_message["mem_usage"] = GetProcess_Mem(pid)
    process_message["cpu_usage"] = GetProcessCPU_Pre(pid)
    process_message["log_level"] = None
    process_message["cluster_ip"] = None
    return json.dumps(process_message)


if __name__ == '__main__':
    print(main())
