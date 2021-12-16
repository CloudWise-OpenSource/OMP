#!/usr/bin/env python3
# encoding: utf-8
# Author: Darren Liu
# Description: get clickhouse Inspection data
import json
import os
import time
import os.path as up
import psutil

from inspection_common import GetLocal_Ip, GetProcess_Survive, GetProcess_Port, GetProcess_Runtime, \
    GetProcess_Mem, GetProcessCPU_Pre


def GetClickhouse_Pid():
    try:
        for pnum in psutil.pids():
            try:
                p = psutil.Process(pnum)
                if p.name() == 'clickhouse-server':
                    pid = pnum
                    return pid
            except Exception:
                pass
    except Exception:
        return None


def GetProcess_ServiceMem(pid):
    if pid and type(pid).__name__ == 'int':
        try:
            service_mem_list = list()
            p = psutil.Process(pid)
            ch_path = up.abspath(up.join(p.exe(), "../.."))
            f = open('%s/etc/clickhouse-server/users.xml' % (ch_path), 'r')
            for lines_list in f:
                if '<max_memory_usage>' in lines_list:
                    service_mem_list = lines_list.strip().replace(
                        '>', '').replace('</', '').split('max_memory_usage')
            service_mem = int(service_mem_list[1]) / 1024 / 1024 / 1024
            ck_mem = "{:.2f}".format(service_mem) + 'G'
            return ck_mem
        except Exception:
            return None
    else:
        return None


def GetProcess_LogLevel(pid):
    service_log_level = list()
    if pid and type(pid).__name__ == 'int':
        p = psutil.Process(pid)
        ch_path = up.abspath(up.join(p.exe(), "../.."))
        f = open('%s/etc/clickhouse-server/config.xml' % (ch_path), 'r')
        for lines_list in f:
            if '<level>' in lines_list:
                service_log_level = lines_list.strip().replace(
                    '>', '').replace('</', '').split('level')
        log_level = service_log_level[1]
        return log_level
    else:
        return None


def GetTable_Readonly(pid, host, port, user, password):
    if pid and type(pid).__name__ == 'int':
        p = psutil.Process(pid)
        ch_path = up.abspath(up.join(p.exe(), "../.."))
        if password:
            ck_bin = '%s/bin/clickhouse-client -m -h %s --port %s -u %s --password %s -q ' % (
                ch_path, host, port, user, password)
        else:
            ck_bin = '%s/bin/clickhouse-client -m -h %s --port %s -q' % (
                ch_path, host, port)
        cmd = ck_bin + '"select database,table from  system.replicas  where is_readonly = 1;"'
        ck_readonly = os.popen(cmd).read().strip('\n').replace('\t', ' ')
        if ck_readonly:
            # table_readonly = ck_readonly.split('\n')
            return ck_readonly
        else:
            return "normal"
    else:
        return None


def GetNodeData_Size(pid, host, port, user, password):
    if pid and type(pid).__name__ == 'int':
        p = psutil.Process(pid)
        ch_path = up.abspath(up.join(p.exe(), "../.."))
        if password:
            ck_bin = '%s/bin/clickhouse-client -m -h %s --port %s -u %s --password %s -q ' % (
                ch_path, host, port, user, password)
        else:
            ck_bin = '%s/bin/clickhouse-client -m -h %s --port %s -q' % (
                ch_path, host, port)
        try:
            cmd = ck_bin + \
                '"select formatReadableSize(sum(data_compressed_bytes)) from system.parts;"'
            nodedata_size = os.popen(cmd).read().strip('\n')
            return nodedata_size
        except Exception:
            return None


def GetDistribute_Size(pid):
    if pid and type(pid).__name__ == 'int':
        p = psutil.Process(pid)
        data_path = up.abspath(up.join(p.cwd(), ".."))
        cmd = 'du -csh %s/data/tsb_distribute %s/data/_cw_distributed_db %s/data/jkb_distribute 2>/dev/null' % (
            data_path, data_path, data_path)
        distribute_size_list = os.popen(cmd).read().strip(
            '\n').replace('\t', ' ').split('\n')
        distribute_size = distribute_size_list[-1].split()
        size = distribute_size[0]
        return size
    else:
        return None


def GetRealTime_Data(pid, host, port, user, password):
    realtime_json = {}
    if pid and type(pid).__name__ == 'int':
        tsb_table_list = ['host_basic_all', 'browser_page_all',
                          'app_request_all', 'mobile_basic_all']
        now_time = int(time.time())
        ago_tiem = int(now_time) - 300
        p = psutil.Process(pid)
        ch_path = up.abspath(up.join(p.exe(), "../.."))
        if password:
            ck_bin = '%s/bin/clickhouse-client -m -h %s --port %s -u %s --password %s -q ' % (
                ch_path, host, port, user, password)
        else:
            ck_bin = '%s/bin/clickhouse-client -m -h %s --port %s -q' % (
                ch_path, host, port)
        for table in tsb_table_list:
            cmd = ck_bin + '"select count() from tsb_distribute.%s where current_time between toDateTime(%d) and toDateTime(%d);"' % (
                table, ago_tiem, now_time) + " 2>/dev/null"
            realtime = os.popen(cmd).read().strip('\n')
            try:
                if int(realtime) > 0:
                    realtime_json[table] = 'True'
                else:
                    realtime_json[table] = 'False'
            except Exception:
                realtime_json[table] = 'False'
        return realtime_json
    else:
        return None


def GetJKBRealTime_Data(pid, host, port, user, password):
    realtime_json = {}
    if pid and type(pid).__name__ == 'int':
        table_list = ['api_snapshot_data_all', 'task_snapshot_all']
        now_time = int(time.time())
        ago_tiem = int(now_time) - 300
        p = psutil.Process(pid)
        ch_path = up.abspath(up.join(p.exe(), "../.."))
        if password:
            ck_bin = '%s/bin/clickhouse-client -m -h %s --port %s -u %s --password %s -q ' % (
                ch_path, host, port, user, password)
        else:
            ck_bin = '%s/bin/clickhouse-client -m -h %s --port %s -q' % (
                ch_path, host, port)
        for table in table_list:
            cmd = ck_bin + '"select count() from jkb_distribute.%s where current_time between toDateTime(%d) and toDateTime(%d);"' % (
                table, ago_tiem, now_time) + " 2>/dev/null"
            realtime = os.popen(cmd).read().strip('\n')
            try:
                if int(realtime) > 0:
                    realtime_json[table] = 'True'
                else:
                    realtime_json[table] = 'False'
            except Exception:
                realtime_json[table] = 'False'
        return realtime_json
    else:
        return None


def GetCluster_IP(pid, host, port, user, password):
    if pid and type(pid).__name__ == 'int':
        p = psutil.Process(pid)
        ch_path = up.abspath(up.join(p.exe(), "../.."))
        if password:
            ck_bin = '%s/bin/clickhouse-client -m -h %s --port %s -u %s --password %s -q ' % (
                ch_path, host, port, user, password)
        else:
            ck_bin = '%s/bin/clickhouse-client -m -h %s --port %s -q' % (
                ch_path, host, port)
        try:
            cmd = ck_bin + '''"select host_address from system.clusters where host_address not like '127.0.0.1' group by host_address;"'''
            cluster_ip = os.popen(cmd).read().strip('\n').split('\n')
            return cluster_ip
        except Exception:
            return None


def main(pid=GetClickhouse_Pid(), host='127.0.0.1', port='18101', user='default', password='', **kwargs):
    process_message = dict()
    process_message["IP"] = GetLocal_Ip()
    process_message["service_status"] = GetProcess_Survive(pid)
    process_message["port_status"] = GetProcess_Port(pid)
    process_message['run_time'] = GetProcess_Runtime(pid)
    process_message['max_memory'] = GetProcess_ServiceMem(pid)
    process_message["mem_usage"] = GetProcess_Mem(pid)
    process_message["log_level"] = GetProcess_LogLevel(pid)
    process_message["cpu_usage"] = GetProcessCPU_Pre(pid)
    process_message["cluser_ip"] = GetCluster_IP(
        pid, host, port, user, password)
    process_message["table_readonly"] = GetTable_Readonly(
        pid, host, port, user, password)
    process_message["nodedata_size"] = GetNodeData_Size(
        pid, host, port, user, password)
    process_message["distribute_size"] = GetDistribute_Size(pid)
    process_message["tsb_realtime"] = GetRealTime_Data(
        pid, host, port, user, password)
    process_message["jkb_realtime"] = GetJKBRealTime_Data(
        pid, host, port, user, password)
    return json.dumps(process_message)


if __name__ == '__main__':
    print(main())
