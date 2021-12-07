#!/usr/bin/env python3
# encoding: utf-8
# Auther: Darren Liu
# Description: get kafka Inspection data

import os.path as up

from inspection_common import *


def GetProcess_Pid():
    try:
        cmd = "ps -eo pid,command |grep 'kafka/bin/..' | grep -v grep"
        cmd_list = os.popen(cmd).read().strip('\n').split()
        pid = int(cmd_list[0])
        return pid
    except:
        return None


def GetProcess_LogLevel(pid):
    log_level = None
    if pid and type(pid).__name__ == 'int':
        try:
            p = psutil.Process(pid)
            kafka_path = up.abspath(up.join(p.exe(), "../../.."))
            f = open('%s/kafka/config/log4j.properties' % (kafka_path), 'r')
            for lines_list in f:
                if 'log4j.rootLogger=' in lines_list:
                    kafka_log_level = lines_list.strip('\n').split('=')
                    log_level = kafka_log_level[-1]
            return log_level
        except:
            return None
    else:
        return None


def GetKafka_PartitionSize(pid, port):
    if pid and type(pid).__name__ == 'int':
        try:
            topic_size_json = {}
            p = psutil.Process(pid)
            kafka_path = up.abspath(up.join(p.exe(), "../../.."))
            cmd = '%s/kafka/bin/kafka-topics.sh  --list --bootstrap-server %s:%s' % (kafka_path, GetLocal_Ip(), port)
            topic_list = os.popen(cmd).read().strip('\n').split('\n')
            f = open('%s/kafka/config/server.properties' % (kafka_path), 'r')
            for lines_list in f:
                if 'log.dirs=' in lines_list:
                    kafka_data_path = lines_list.strip('\n').split('=')
                    data_path = kafka_data_path[-1]
            for topic in topic_list:
                size_cmd = 'du -csh %s/%s' % (data_path, topic) + '-*'
                topic_size_list = os.popen(size_cmd).read().strip('\n').split('\n')
                topic_size = topic_size_list[-1].split()
                topic_size_json[topic] = topic_size[0]
        except:
            topic_size_json = None
        return topic_size_json


def GetKafka_PartitionCount(pid, port):
    if pid and type(pid).__name__ == 'int':
        partition_size_json = {}
        try:
            p = psutil.Process(pid)
            kafka_path = up.abspath(up.join(p.exe(), "../../.."))
            cmd = '%s/kafka/bin/kafka-topics.sh  --describe --bootstrap-server %s:%s' % (
            kafka_path, GetLocal_Ip(), port)
            topic_list = os.popen(cmd).read().strip('\n').split('\n')
            for topic_partition in topic_list:
                if 'PartitionCount' in topic_partition:
                    partition_list = topic_partition.split()
                    topic_line = partition_list[0].split(':')
                    partition_line = partition_list[1].split(':')
                    replication_line = partition_list[2].split(':')
                    topic = topic_line[-1]
                    replication = replication_line[-1]
                    partition = partition_line[-1]
                    partition_size_json[topic] = {"partition": partition, "replication": replication}
        except:
            partition_size_json = None
        return partition_size_json


def GetKafka_Offsets(pid, port):
    if pid and type(pid).__name__ == 'int':
        try:
            p = psutil.Process(pid)
            kafka_path = up.abspath(up.join(p.exe(), "../../.."))
            cmd = '%s/kafka/bin/kafka-consumer-groups.sh  --list --bootstrap-server %s:%s' % (
            kafka_path, GetLocal_Ip(), port)
            group_list = os.popen(cmd).read().strip('\n').split('\n')
            offset_group_json = {}
            for group in group_list:
                log_offset = 0
                lag_offset = 0
                offset_cmd = '%s/kafka/bin/kafka-consumer-groups.sh  --group %s --describe  --bootstrap-server %s:%s|sort 2>/dev/null' % (
                kafka_path, group, GetLocal_Ip(), port)
                offset_list = os.popen(offset_cmd).read().strip('\n').split('\n')
                if "Error" in offset_list[0]:
                    continue
                offset_json = {}
                for offsets in offset_list:
                    if 'PARTITION' not in offsets:
                        offset = offsets.split()
                        if offset[0] not in offset_json:
                            if offset[3] != '-':
                                log_offset = int(offset[3])
                            if offset[4] != '-':
                                lag_offset = int(offset[4])
                            offset_json[offset[0]] = {"log_offset": log_offset, "lag_offset": lag_offset}
                        else:
                            if offset[3] != '-':
                                log_offset += int(offset[3])
                            if offset[4] != '-':
                                lag_offset += int(offset[4])
                            offset_json[offset[0]] = {"log_offset": log_offset, "lag_offset": lag_offset}
                offset_group_json[group] = offset_json
            return offset_group_json
        except:
            return None


def main(pid=GetProcess_Pid(), port='18108', json_path="/data/app/data.json",**kwargs):
    process_message = {}
    process_message["IP"] = GetLocal_Ip()
    process_message["service_status"] = GetProcess_Survive(pid)
    process_message["port_status"] = GetProcess_Port(pid)
    process_message['run_time'] = GetProcess_Runtime(pid)
    process_message['max_memory'] = GetProcess_ServiceMem(pid, is_java=True)
    process_message["log_level"] = GetProcess_LogLevel(pid)
    process_message["mem_usage"] = GetProcess_Mem(pid)
    process_message["cpu_usage"] = GetProcessCPU_Pre(pid)
    process_message["topic_partition"] = GetKafka_PartitionCount(pid, port)
    process_message["kafka_offsets"] = GetKafka_Offsets(pid, port)
    process_message["topic_size"] = GetKafka_PartitionSize(pid, port)
    process_message["cluster_ip"] = GetCluster_IP(json_path=json_path, service_name="kafka")
    return json.dumps(process_message)


if __name__ == '__main__':
    print(main())
