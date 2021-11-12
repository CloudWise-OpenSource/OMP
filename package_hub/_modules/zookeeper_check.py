#!/usr/bin/env python3
# encoding: utf-8
# Auther: Darren Liu
# Description: get zookeeper Inspection data

from inspection_common import *


def GetProcess_Pid():
    try:
        for pnum in psutil.pids():
            try:
                p = psutil.Process(pnum)
                if p.name() == 'java' and 'zookeeper' in p.cwd():
                    pid = pnum
                    return pid
            except:
                pass
    except:
        return None


def GetNode_Status(pid):
    if pid and type(pid).__name__ == 'int':
        try:
            p = psutil.Process(pid)
            cmd = "bash %s/bin/zkServer.sh status 2>/dev/null" % (p.cwd())
            node_status = os.popen(cmd).read().strip('\n').split(':')
            status = node_status[-1].strip()
            return status
        except:
            return None


def GetCluster_IP(pid):
    zk_cluster = []
    if pid and type(pid).__name__ == 'int':
        try:
            p = psutil.Process(pid)
            f = open('%s/conf/zoo.cfg' % (p.cwd()), 'r')
            for lines_list in f:
                if 'server' in lines_list:
                    zk_cluster_list = lines_list.strip('\n').split('=')
                    zk_cluster_ip = zk_cluster_list[-1].split(':')
                    zk_cluster.append(zk_cluster_ip[0])
            return zk_cluster
        except:
            return None
    else:
        return None


def GetProcess_LogLevel(pid):
    zk_cluster = []
    log_level = None
    if pid and type(pid).__name__ == 'int':
        try:
            p = psutil.Process(pid)
            f = open('%s/conf/log4j.properties' % (p.cwd()), 'r')
            for lines_list in f:
                if 'zookeeper.root.logger=' in lines_list:
                    zk_log_level = lines_list.strip('\n').split('=')
                    log_level = zk_log_level[-1]
            return log_level
        except:
            return None
    else:
        return None


def main(pid=GetProcess_Pid(), json_path="/data/app/data.json", **kwargs):
    process_message = {}
    process_message["IP"] = GetLocal_Ip()
    process_message["service_status"] = GetProcess_Survive(pid)
    process_message["port_status"] = GetProcess_Port(pid)
    process_message['run_time'] = GetProcess_Runtime(pid)
    process_message['max_memory'] = GetProcess_ServiceMem(pid, is_java=True)
    process_message["mem_usage"] = GetProcess_Mem(pid)
    process_message["cpu_usage"] = GetProcessCPU_Pre(pid)
    process_message["log_level"] = GetProcess_LogLevel(pid)
    process_message["node_status"] = GetNode_Status(pid)
    process_message["cluster_ip"] = GetCluster_IP(pid)
    return json.dumps(process_message)


if __name__ == '__main__':
    print(main())
