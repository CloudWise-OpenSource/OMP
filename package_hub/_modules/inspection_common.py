#!/usr/bin/env python3
# encoding: utf-8
# Author: Jayden Liu
# Description: common function for inspection
import os
import time
import json
import socket
import psutil


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
    if pid and isinstance(pid, int):
        return "True"
    else:
        return "False"


def GetProcess_Port(pid):
    if pid and isinstance(pid, int):
        try:
            port = []
            cmd = 'ss -lnput | grep ' + str(pid)
            port_list = os.popen(cmd).read().strip('\n').split('\n')
            for line_list in port_list:
                if not line_list:
                    continue
                line = line_list.split()
                port_aa = line[4].split(':')
                port.append(port_aa[-1])
            port = list(set(port))
            return port
        except Exception:
            return None
    else:
        return None


def GetProcess_Runtime(pid):
    runtime = None
    if pid and isinstance(pid, int):
        try:
            cmd = 'ps -eo pid,etime|grep ' + str(pid)
            etime = os.popen(cmd).read().strip('\n').split()
            # if '-' in etime[1]:
            #     runtime = etime[1].replace('-', ' day ')
            # else:
            #     runtime = etime[1]

            runtime = etime[1].replace(
                '-', '天').replace(':', '小时', 1).replace(':', '分钟', 1) + '秒'

            run_time = etime[1].split(':')
            run_time = [int(i) for i in run_time]
            if len(run_time) == 1:
                runtime = f"{run_time[0]}秒"
            elif len(run_time) == 2:
                runtime = f"{run_time[0]}分钟{run_time[1]}秒"
            elif len(run_time) == 3:
                runtime = f"{run_time[0]}小时{run_time[1]}分钟{run_time[2]}秒"
            elif len(run_time) == 4:
                runtime = \
                    f"{run_time[0]}天{run_time[1]}小时{run_time[2]}分钟{run_time[3]}秒"
            elif len(run_time) == 5:
                runtime = \
                    f"{run_time[0]}年{run_time[1]}天{run_time[2]}小时" \
                    f"{run_time[3]}分钟{run_time[4]}秒"
        except Exception:
            pass
    return runtime


_timer = getattr(time, 'monotonic', time.time)
num_cpus = psutil.cpu_count() or 1


def timer():
    return _timer() * num_cpus


def GetProcessCPU_Pre(pid):
    if pid and isinstance(pid, int):
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
    if pid and isinstance(pid, int):
        try:
            p = psutil.Process(pid)
            process_mem = p.memory_percent()
            mem_usage = "{:.2f}".format(process_mem) + "%"
        except Exception:
            return None
    else:
        mem_usage = None
    return mem_usage


def GetProcess_ServiceMem(pid, is_java=False):
    if is_java:
        if pid and isinstance(pid, int):
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
    else:
        return None


def GetCluster_IP(json_path="/data/app/data.json", service_name=""):
    cluster_ip = []
    if json_path.endswith("json"):
        if not os.path.exists(json_path):
            return []
            # raise FileNotFoundError("json file not exist")
        with open(json_path, "r") as f:
            content = json.load(f)
        open_source_service = content.get("basics", [])
        internl_service = content.get("services", [])
        open_source_service.extend(internl_service)
        all_service = open_source_service
        for service in all_service:
            if service_name == service.get("name"):
                service_ip = service.get("local_ip")
                cluster_ip.append(service_ip)
        return cluster_ip
    elif json_path.endswith("list"):
        try:
            cmd = 'grep %s %s' % (service_name, json_path)
            cluster_list = os.popen(cmd).read().strip('\n').split('\n')
            for cluster_line in cluster_list:
                cluster = cluster_line.split()
                cluster_ip.append(cluster[0])
        except Exception:
            return cluster_ip
    else:
        return cluster_ip
