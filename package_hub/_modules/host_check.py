#!/usr/bin/env python3
# encoding: utf-8
# Author: Darren Liu
# Description: get host Inspection data

import datetime
import json
import os
import platform
import re
import socket
import subprocess
import time

import psutil


def run_cmd(cmd):
    """
    运行系统命令，返回标准输出，标准错误输出及执行状态码
    :param cmd:
    :return:
    """
    p = subprocess.run(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    cmd_stdout = bytes.decode(p.stdout)
    if cmd_stdout.endswith('\n'):
        cmd_stdout = cmd_stdout.strip()
    # cmd_stderr = bytes.decode(p.stderr)

    if p.returncode == '0':
        return None
    else:
        # return cmd_stdout, cmd_stderr, p.returncode
        return cmd_stdout


def GetLocal_Ip():
    try:
        csock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        csock.connect(('8.8.8.8', 80))
        (addr, port) = csock.getsockname()
        csock.close()
        return addr
    except socket.error:
        return "127.0.0.1"


def GetHostname_Info():
    try:
        host_name = socket.gethostname()
        return host_name
    except Exception:
        return None


def GetRelease_Version():
    try:
        if os.path.exists('/etc/redhat-release'):
            with open('/etc/redhat-release') as file:
                for line in file:
                    return line.strip('\n')
        else:
            return None
    except Exception:
        return None


def GetKernel_Version():
    """
    获取系统内核版本
    :return:
    """
    try:
        release_version_list = platform.platform()
        release_version_line = release_version_list.split('-with-')
        release_version = release_version_line[0]
        return release_version
    except Exception:
        return None


def GetSelinux_Status():
    """
    获取selinux状态
    :return:
    """
    try:
        cmd = 'getenforce'
        selinux_status = run_cmd(cmd)
        return selinux_status
    except Exception:
        return None


def GetUmask_Status():
    try:
        user_cmd = 'whoami'
        user = run_cmd(user_cmd)
        cmd = 'umask'
        umask_status = run_cmd(cmd)
        return {"user": user, "umask": umask_status}
    except Exception:
        return None


def GetUlimit_Num():
    try:
        cmd = 'ulimit -n'
        ulimit_num = run_cmd(cmd)
        return ulimit_num
    except Exception:
        return None


def GetTimeNow_Info():
    """
    获取系统当前时间
    :return:
    """
    try:
        time_now = datetime.datetime.strftime(
            datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
        return time_now
    except Exception:
        return None


def GetRunTime_Info():
    """
    获取系统运行时间
    :return:
    """
    try:
        cmd = "uptime"
        uptime_list = run_cmd(cmd).strip().split('up')
        run_time = uptime_list[1].strip().split(',')
        if 'user' in run_time[1]:
            time = run_time[0]
        else:
            time = run_time[0] + run_time[1]
        return time
    except Exception:
        return None


def GetCpu_Total():
    try:
        cpu_count = str(psutil.cpu_count()) + "C"
        return cpu_count
    except Exception:
        return None


def GetMemory_Total():
    try:
        with open('/proc/meminfo') as fd:
            for line in fd:
                if line.startswith('MemTotal'):
                    mem = int(line.split()[1].strip())
                    break
        mem = int('%.f' % (mem / 1024.0))
        if mem > 1024:
            mem = '%.f' % (mem / 1024.0) + 'GB'
        else:
            mem = str(mem) + 'MB'
        return mem
    except Exception:
        return None


def GetDisk_Total():
    try:
        total_mb = 0
        df_cmd = "df -h | grep -v 'tmpfs' | tail -n +2"
        result = run_cmd(df_cmd).strip().split('\n')
        for total_list in result:
            total = total_list.split()
            if 'T' in total[1]:
                total_tb = total[1].replace('T', '')
                total_mb += int('%.f' %
                                (int(float(total_tb)) * 1024.0 * 1024.0))
            if 'G' in total[1]:
                total_gb = total[1].replace('G', '')
                total_mb += int('%.f' % (int(float(total_gb)) * 1024.0))
            if 'M' in total[1]:
                total_mb += int(float(total[1].replace('M', '')))
        if total_mb > 1024 and total_mb < 1048576:
            disk_total = '%.f' % (total_mb / 1024.0) + 'GB'
        elif total_mb > 1048576:
            disk_total = '%.f' % (total_mb / 1024.0 / 1024.0) + 'TB'
        else:
            disk_total = str(total_mb) + 'MB'
        return disk_total
    except Exception:
        return None


def GetMemory_Usage():
    """
    获取内存使用信息
    :return:
    """
    try:
        svmem = psutil.virtual_memory()
        mem_usage = str(svmem.percent) + '%'
        return mem_usage
    except Exception:
        return None


def GetCpu_Usage():
    """
    获取cpu使用率
    :return:
    """
    try:
        cpu_usage = str(psutil.cpu_percent()) + '%'
        return cpu_usage
    except Exception:
        return None


def GetDisk_Info(data_path):
    """
    获取磁盘使用量信息
    :return:
    """
    try:
        disk_usage_json = {}
        df_cmd = "df -h | grep -v 'tmpfs' | tail -n +2"
        result = run_cmd(df_cmd).strip().split('\n')
        for total_list in result:
            total = total_list.split()
            if total[-1] == '/':
                disk_usage_json[total[-1]] = total[-2]
            if total[-1] == data_path:
                disk_usage_json[total[-1]] = total[-2]
        return disk_usage_json
    except Exception:
        return None


def GetInode_Info(data_path):
    """
    获取inode使用量信息
    :return:
    """
    try:
        inode_usage_json = {}
        inode_cmd = "df -i | grep -v 'tmpfs' | tail -n +2"
        result = run_cmd(inode_cmd).strip().split('\n')
        for total_list in result:
            total = total_list.split()
            if total[-1] == '/':
                inode_usage_json[total[-1]] = total[-2]
            if total[-1] == data_path:
                inode_usage_json[total[-1]] = total[-2]
        return inode_usage_json
    except Exception:
        return None


def GetSysLoad_Average():
    """
    获取系统平均负载信息
    :return:
    """
    try:
        load_average_info = psutil.getloadavg()
        load_average_dict = dict()
        load_average_dict.update({'m1_average_load': load_average_info[0]})
        load_average_dict.update({'m5_average_load': load_average_info[1]})
        load_average_dict.update({'m15_average_load': load_average_info[2]})
        load_average_json = load_average_dict
        return load_average_json
    except Exception:
        return None


def GetServicesPort_Connectivity(port_list):
    try:
        port_json = []
        for port in port_list:
            sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sk.settimeout(2)
            status = sk.connect_ex((port['ip'], int(port['port'])))
            if status != 0:
                port["status"] = "False"
                port_json.append(port)
        if len(port_json) > 0:
            return port_json
        else:
            return 'Ture'
    except socket.error:
        return None
    sk.close()


def GetServer_Bandwidth():
    try:
        bandwidth_1 = psutil.net_io_counters()
        time.sleep(1)
        bandwidth_2 = psutil.net_io_counters()
        bandwidth_sent = '%.f' % (
            (bandwidth_2.bytes_sent - bandwidth_1.bytes_sent) / 1024)
        bandwidth_recv = '%.f' % (
            (bandwidth_2.bytes_recv - bandwidth_1.bytes_recv) / 1024)
        sent = bandwidth_sent + "KB/s"
        receive = bandwidth_recv + "KB/s"
        return {"sent": sent, "receive": receive}
    except Exception:
        return None


def GetDisK_ReadWrite():
    try:
        disk_1 = psutil.disk_io_counters()
        time.sleep(1)
        disk_2 = psutil.disk_io_counters()
        disk_read = '%.f' % ((disk_2.read_bytes - disk_1.read_bytes) / 1024)
        disk_write = '%.f' % ((disk_2.write_bytes - disk_1.write_bytes) / 1024)
        read = disk_read + "KB/s"
        write = disk_write + "KB/s"
        return {"read": read, "write": write}
    except Exception:
        return None


def GetDisk_IoWait():
    try:
        disk_iowait = 0
        cmd = "vmstat 1 10"
        iowait_list = run_cmd(cmd).strip().split('\n')
        for iowait in iowait_list:
            if 'cpu' in iowait_list or 'wa' in iowait:
                continue
            else:
                disk_iowait += int(iowait.split()[-2])
        disk = disk_iowait / 10
        return disk
    except Exception:
        return None


def GetMemory_Top10():
    """
    获取占用内存前10的应用
    :return:
    """

    class Cwp:
        def __init__(self, pid, memory_percent, cmdline):
            self.pid = pid
            self.cmdline = cmdline
            self.memory_percent = memory_percent

    all_pids = psutil.pids()
    cw_ps = []
    for ele in all_pids:
        try:
            p = psutil.Process(ele)
            cw_p = Cwp(p.pid, p.memory_percent(), ' '.join(p.cmdline()))
            cw_ps.append(cw_p)
        except psutil.Error:
            continue
    cw_ps.sort(key=lambda c: c.memory_percent, reverse=True)
    content_list = list()
    for ele in cw_ps[:10]:
        tma_dict = {
            'TOP': str(cw_ps.index(ele) + 1),
            'PID': ele.pid,
            'P_RATE': str(round(ele.memory_percent, 2)) + '%',
            'P_CMD': ele.cmdline
        }
        content_list.append(tma_dict)
    top10_mem_app_json = content_list
    return top10_mem_app_json


def GetCpu_Top10():
    """
    获取cpu使用率前10的应用
    :return:
    """

    class Cwp:
        def __init__(self, pid, cpu_percent, cmdline):
            self.pid = pid
            self.cmdline = cmdline
            self.cpu_percent = cpu_percent

    all_pids = psutil.pids()
    cw_ps = []
    for ele in all_pids:
        try:
            p = psutil.Process(ele)
            if len(p.cmdline()) >= 1:
                cpu_p = p.cpu_percent(interval=1)
                cw_p = Cwp(p.pid, cpu_p, ' '.join(p.cmdline()))
                cw_ps.append(cw_p)
        except psutil.Error:
            continue
    cw_ps.sort(key=lambda c: c.cpu_percent, reverse=True)
    content_list = list()
    for ele in cw_ps[:10]:
        tca_dict = {
            'TOP': str(cw_ps.index(ele) + 1),
            'PID': ele.pid,
            'P_RATE': str(round(ele.cpu_percent, 2)) + '%',
            'P_CMD': ele.cmdline
        }
        content_list.append(tca_dict)
    top10_cpu_app_json = content_list
    return top10_cpu_app_json


def GetKernel_Info():
    try:
        cmd = "egrep -v '^#|^$' /etc/sysctl.conf"
        sysctl = run_cmd(cmd).strip().split('\n')
        if len(sysctl) > 0:
            return sysctl
        else:
            return None
    except Exception:
        return None


def GetBoot_Start():
    try:
        boot_start = []
        release_version_list = platform.platform()
        if '-6.' in release_version_list:
            cmd = "chkconfig --list"
        if '-7.' in release_version_list:
            cmd = 'systemctl list-unit-files | grep enabled'
        boot_start_list = run_cmd(cmd).strip().split('\n')
        for line_list in boot_start_list:
            line = line_list.split()
            boot_start.append(line[0])
        return boot_start
    except Exception:
        return None


def GetZombies_Status():
    try:
        cmd = "ps -A -ostat,ppid,cmd |grep -e '^[Zz]'"
        zombies_status_list = run_cmd(cmd).strip().split('\n')
        if len(zombies_status_list) > 0:
            return zombies_status_list
        else:
            return None
    except Exception:
        return None


def GatRun_Process():
    """
    获取正在运行的进程数
    :return:
    """
    try:
        all_process_num = len(psutil.pids())
        return all_process_num
    except Exception:
        return None


def GetFirewall_Info():
    try:
        get_firewall_cmd = "iptables -nL"
        result = run_cmd(get_firewall_cmd)
        new_str = "".join([s for s in result.splitlines(True) if s.strip()])
        if len(new_str.split('\n')) == 6:
            return None
        fw_block_list = result.split('\n\n')
        firewall_dict = dict()
        for block in fw_block_list:
            block_rules_list = list()
            tmp_rules = block.split('\n')
            fw_title = tmp_rules[0]
            for line in tmp_rules:
                rule_dict = dict()
                if line.startswith('Chain') or line.startswith('target'):
                    continue
                items = re.split(r'\s+', line)
                rule_dict.update({'target': items[0]})
                rule_dict.update({'port': items[1]})
                rule_dict.update({'opt': items[2]})
                rule_dict.update({'source': items[3]})
                rule_dict.update({'destination': items[4]})
                rule_dict.update({'others': ' '.join(items[5:])})
                block_rules_list.append(rule_dict)
            if len(block_rules_list) > 0:
                firewall_dict.update({fw_title: block_rules_list})
        firewall_json = firewall_dict
        return firewall_json
    except Exception:
        return None


def main(data_path='/data', port_list=[{"name": "ssh", "ip": "127.0.0.1", "port": "36000"}], **kwargs):
    process_message = dict()
    # process_message["IP"] = GetLocal_Ip()
    # process_message["hostname"] = GetHostname_Info()
    process_message["release_version"] = GetRelease_Version()
    process_message["kernel_version"] = GetKernel_Version()
    process_message["selinux"] = GetSelinux_Status()
    process_message["umask"] = GetUmask_Status()
    # process_message["max_openfile"] = GetUlimit_Num()
    # process_message["now_time"] = GetTimeNow_Info()
    # process_message["run_time"] = GetRunTime_Info()
    # process_message["host_massage"] = {"cpu": GetCpu_Total(), "memory": GetMemory_Total(), "disk": GetDisk_Total()}
    # process_message["memory_usage"] = GetMemory_Usage()
    # process_message["cpu_usage"] = GetCpu_Usage()
    # process_message["disk_usage"] = GetDisk_Info(data_path)
    # process_message["inode_usage"] = GetInode_Info(data_path)
    # process_message["sys_load"] = GetSysLoad_Average()
    # process_message["port_connectivity"] = GetServicesPort_Connectivity(port_list)
    # process_message["bandwidth"] = GetServer_Bandwidth()
    # process_message["throughput"] = GetDisK_ReadWrite()
    # process_message["iowait"] = GetDisk_IoWait()
    process_message["memory_top"] = GetMemory_Top10()
    process_message["cpu_top"] = GetCpu_Top10()
    process_message["kernel_parameters"] = GetKernel_Info()
    # process_message["boot_start"] = GetBoot_Start()
    process_message["zombies_process"] = GetZombies_Status()
    process_message["run_process"] = GatRun_Process()
    # process_message["iptables"] = GetFirewall_Info()
    return json.dumps(process_message)
