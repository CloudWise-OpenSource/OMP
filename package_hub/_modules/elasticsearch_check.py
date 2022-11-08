#!/usr/bin/env python3
# encoding: utf-8
# Author: Darren Liu
# Description: get es Inspection data
import json
import ssl
import urllib.request

import psutil

from inspection_common import GetLocal_Ip, GetProcess_Survive, GetProcess_Port, GetProcess_Runtime, \
    GetProcess_Mem, GetProcessCPU_Pre, GetProcess_ServiceMem, GetCluster_IP


def GetProcess_Pid():
    try:
        for pnum in psutil.pids():
            try:
                p = psutil.Process(pnum)
                if p.name() == 'java' and 'elasticsearch' in p.cwd():
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
            es_path = p.cwd()
            f = open('%s/config/log4j2.properties' % (es_path), 'r')
            for lines_list in f:
                if 'logger.action.level =' in lines_list:
                    es_log_level = lines_list.strip('\n').split()
                    log_level = es_log_level[-1]
        except Exception:
            log_level = None
        return log_level
    else:
        return None


def GetCluster_Status(port):
    url = 'http://127.0.0.1' + ':' + str(port) + "/_cluster/health"
    ssl._create_default_https_context = ssl._create_unverified_context
    try:
        cluster_list = urllib.request.urlopen('%s' % (url), timeout=15)
        cluster_line = json.loads(cluster_list.read())
        cluster = cluster_line["status"]
        return cluster
    except Exception:
        return None


def GetIndex_Status(port):
    status = {}
    url = 'http://127.0.0.1' + ':' + str(port) + "/_cat/indices"
    ssl._create_default_https_context = ssl._create_unverified_context
    try:
        index_list = urllib.request.urlopen('%s' % (url), timeout=15)
        index_line = index_list.read().decode().strip().split('\n')
        for index in index_line:
            index_status = index.split()
            if index_status[0] != 'green' and index_status[1] == 'open':
                status[index_status[2]] = index_status[0]
        if status:
            return status
        else:
            return 'green'
    except Exception:
        return None


def main(pid=GetProcess_Pid(), port=18115, json_path="/data/app/data.json", **kwargs):
    process_message = dict()
    process_message["IP"] = GetLocal_Ip()
    process_message["service_status"] = GetProcess_Survive(pid)
    process_message["port_status"] = GetProcess_Port(pid)
    process_message['run_time'] = GetProcess_Runtime(pid)
    process_message['max_memory'] = GetProcess_ServiceMem(pid, is_java=True)
    process_message["mem_usage"] = GetProcess_Mem(pid)
    process_message["cpu_usage"] = GetProcessCPU_Pre(pid)
    process_message["log_level"] = GetProcess_LogLevel(pid)
    process_message['cluster_status'] = GetCluster_Status(port)
    process_message["index_status"] = GetIndex_Status(port)
    process_message["cluster_ip"] = GetCluster_IP(
        json_path=json_path, service_name="elasticsearch")
    return json.dumps(process_message)


if __name__ == "__main__":
    print(main())
