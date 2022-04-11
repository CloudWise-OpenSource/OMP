#!/usr/bin/env python3
# encoding: utf-8
# Author: Darren Liu
# Description: get mysql Inspection data
import json
import subprocess

import psutil
import pymysql

from inspection_common import GetProcess_Runtime, GetLocal_Ip, GetProcess_Survive, GetProcess_Port, GetProcess_Mem, \
    GetProcessCPU_Pre


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


def GetProcess_Pid():
    try:
        for pnum in psutil.pids():
            try:
                p = psutil.Process(pnum)
                if p.name() == 'mysqld':
                    pid = pnum
                    return pid
            except Exception:
                pass
    except Exception:
        return None


def GetProcess_Threads(pid):
    if pid and type(pid).__name__ == 'int':
        try:
            # port = []
            p = psutil.Process(pid)
            process_threads = p.num_threads()
            return process_threads
        except Exception:
            return None
    else:
        return None


def get_connection(host, user, passwd, port, database=None):
    try:
        host = GetLocal_Ip()
        if database:
            conn = pymysql.connect(host=host, user=user, passwd=passwd, port=port, database=database, charset='utf8',
                                   use_unicode=True, cursorclass=pymysql.cursors.DictCursor)
        else:
            conn = pymysql.connect(host=host, user=user, passwd=passwd, port=port, charset='utf8', use_unicode=True,
                                   cursorclass=pymysql.cursors.DictCursor)
        return conn
    except pymysql.Error:
        return None


def GetMysql_ConnNum(user, passwd, port, database):
    host = GetLocal_Ip()
    connected_sql = "show status where Variable_name='Threads_connected';"
    conn_conn = get_connection(host, user, passwd, port, database)
    if not conn_conn:
        return None
    conn_cursor = conn_conn.cursor()
    try:
        conn_cursor.execute(connected_sql)
        conn_conn.commit()
        exe_result = conn_cursor.fetchone()
    except conn_conn.Error:
        exe_result = None
    finally:
        conn_cursor.close()
        conn_conn.close()
    if exe_result:
        conn_num = exe_result['Value']
    else:
        conn_num = ''
    return conn_num


def GetMysql_Backup(user, passwd, port, database):
    host = GetLocal_Ip()
    check_sql = 'show slave status;'
    check_conn = get_connection(host, user, passwd, port, database)
    if not check_conn:
        return None
    check_cursor = check_conn.cursor()
    try:
        check_cursor.execute(check_sql)
        check_conn.commit()
        exe_result = check_cursor.fetchone()
    except check_conn.Error:
        exe_result = None
        return None
    finally:
        check_cursor.close()
        check_conn.close()
    if exe_result:
        slave_io_status = exe_result['Slave_IO_Running']
        slave_sql_status = exe_result['Slave_SQL_Running']
        if slave_io_status == 'Yes' and slave_sql_status == 'Yes':
            backup_status = 'up'
        else:
            backup_status = 'down'
    else:
        backup_status = 'no slave'
    return backup_status


def GetAbortedClients_Num(user, passwd, port, database):
    host = GetLocal_Ip()
    aborted_clients_num_sql = "show global status like 'Aborted_clients';"
    aborted_clients_num_conn = get_connection(
        host, user, passwd, port, database)
    if not aborted_clients_num_conn:
        return None
    aborted_clients_num_cursor = aborted_clients_num_conn.cursor()
    try:
        aborted_clients_num_cursor.execute(aborted_clients_num_sql)
        aborted_clients_num_conn.commit()
        aborted_clients_num_result = aborted_clients_num_cursor.fetchone()
    except aborted_clients_num_conn.Error:
        return None
    finally:
        aborted_clients_num_cursor.close()
        aborted_clients_num_conn.close()
    aborted_clients_num = aborted_clients_num_result['Value']
    return aborted_clients_num


def GetFailConnect_Num(user, passwd, port, database):
    host = GetLocal_Ip()
    failure_connect_num_sql = "show global status like 'Aborted_connects';"
    failure_connect_num_conn = get_connection(
        host, user, passwd, port, database)
    if not failure_connect_num_conn:
        return None
    failure_connect_num_cursor = failure_connect_num_conn.cursor()
    try:
        failure_connect_num_cursor.execute(failure_connect_num_sql)
        failure_connect_num_conn.commit()
        failure_connect_num_result = failure_connect_num_cursor.fetchone()
    except failure_connect_num_conn.Error:
        return None
    finally:
        failure_connect_num_cursor.close()
        failure_connect_num_conn.close()
    failure_connect_num = failure_connect_num_result['Value']
    return failure_connect_num


def GetSlowQuery_Num(user, passwd, port, database):
    host = GetLocal_Ip()
    select_slow_query_switch_sql = "show variables where variable_name='slow_query_log';"
    select_slow_query_log_file_sql = "show variables where variable_name='slow_query_log_file';"
    select_slow_query_log_file = ''
    slow_query_num = ''
    select_slow_query_num_conn = get_connection(
        host, user, passwd, port, database)
    if not select_slow_query_num_conn:
        return None
    select_slow_query_num_cursor = select_slow_query_num_conn.cursor()
    try:
        select_slow_query_num_cursor.execute(select_slow_query_switch_sql)
        select_slow_query_num_conn.commit()
        switch_exe_result = select_slow_query_num_cursor.fetchone()
    except select_slow_query_num_conn.Error:
        return None
    if not switch_exe_result:
        return None
    if switch_exe_result['Value'] != 'ON':
        return None
    try:
        select_slow_query_num_cursor.execute(select_slow_query_log_file_sql)
        select_slow_query_num_conn.commit()
        file_exe_result = select_slow_query_num_cursor.fetchone()
    except select_slow_query_num_conn.Error:
        return None
    finally:
        select_slow_query_num_cursor.close()
        select_slow_query_num_conn.close()
    if not file_exe_result:
        return None
    select_slow_query_log_file = file_exe_result['Value']
    get_slow_query_num_cmd = "grep Query_time {} | wc -l".format(
        select_slow_query_log_file)
    grep_wc_result = run_cmd(get_slow_query_num_cmd)
    if not grep_wc_result:
        return None
    slow_query_num = grep_wc_result
    return slow_query_num


def main(pid=GetProcess_Pid(), host='127.0.0.1', user='Rootmaster', passwd='Rootmaster@777', port=18103, database=None,
         **kwargs):
    process_message = dict()
    process_message["IP"] = GetLocal_Ip()
    process_message["service_status"] = GetProcess_Survive(pid)
    process_message["port_status"] = GetProcess_Port(pid)
    process_message['run_time'] = GetProcess_Runtime(pid)
    process_message["mem_usage"] = GetProcess_Mem(pid)
    process_message["cpu_usage"] = GetProcessCPU_Pre(pid)
    process_message['max_memory'] = None
    process_message["log_level"] = None
    process_message["process_threads"] = GetProcess_Threads(pid)
    process_message["conn_num"] = GetMysql_ConnNum(
        user, passwd, port, database)
    process_message["aborted_clients"] = GetAbortedClients_Num(
        user, passwd, port, database)
    process_message["failure_connect"] = GetFailConnect_Num(
        user, passwd, port, database)
    process_message["slow_query"] = GetSlowQuery_Num(
        user, passwd, port, database)
    process_message['backup_status'] = GetMysql_Backup(
        user, passwd, port, database)
    return json.dumps(process_message)


if __name__ == '__main__':
    print(main())
