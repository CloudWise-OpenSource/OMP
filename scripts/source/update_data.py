# -*- coding: utf-8 -*-
# Project: update_data
# Author: jon.liu@yunzhihui.com
# Create time: 2021-09-18 10:36
# IDE: PyCharm
# Version: 1.0
# Introduction:

import os
import sys
import hashlib

import django

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
PYTHON_PATH = os.path.join(PROJECT_DIR, "component/env/bin/python3")
MANAGE_PATH = os.path.join(PROJECT_DIR, "omp_server/manage.py")
sys.path.append(os.path.join(PROJECT_DIR, "omp_server"))

# 加载Django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "omp_server.settings")
django.setup()

from db_models.models import UserProfile
from db_models.models import MonitorUrl
from utils.parse_config import MONITOR_PORT, CLEAR_DB
from db_models.models import Env, AlertRule, \
    Rule, Service, \
    BackupHistory, BackupCustom, \
    DetailInstallHistory, Host, SelfHealingSetting
from utils.plugin.crontab_utils import change_task


def create_default_user():
    """
    创建基础用户
    :return:
    """
    TO_CREATE_USER_LIST = [
        {"username": "admin", "password": "Yunweiguanli@OMP_123", "email": "omp@cloudwise.com", "role": "SuperUser"},
        {"username": "omp", "password": "Yunweiguanli@OMP_123", "email": "omp@cloudwise.com", "role": "ReadOnlyUser"}
    ]
    username = password = email = role = ""
    for user_dict in TO_CREATE_USER_LIST:
        username = user_dict.get("username")
        password = user_dict.get("password")
        email = user_dict.get("email")
        role = user_dict.get("role")
        if UserProfile.objects.filter(username=username).count() != 0:
            continue
        UserProfile.objects.create_user(
            username=username,
            password=password,
            email=email,
            role=role
        )


def create_default_monitor_url():
    """
    配置监控地址初始入库
    :return:
    """
    if MonitorUrl.objects.all().count() != 0:
        return
    monitor_list = []
    local_ip = "127.0.0.1:"
    monitor_list.append(
        MonitorUrl(id="1", name="prometheus", monitor_url=local_ip + str(
            MONITOR_PORT.get("prometheus", "19011"))))
    monitor_list.append(
        MonitorUrl(id="2", name="alertmanager", monitor_url=local_ip + str(
            MONITOR_PORT.get("alertmanager", "19013"))))
    monitor_list.append(MonitorUrl(
        id="3", name="grafana",
        monitor_url=local_ip + str(MONITOR_PORT.get("grafana", "19014"))))
    MonitorUrl.objects.bulk_create(monitor_list)


def create_default_env():
    """
    创建默认环境
    :return:
    """
    env_name = "default"
    if Env.objects.filter(name=env_name).count() != 0:
        return
    Env(name=env_name).save()


def get_hash_value(expr, severity):
    data = expr + severity
    hash_data = hashlib.md5(data.encode(encoding='UTF-8')).hexdigest()
    return hash_data


def create_threshold():
    """
    为告警添加默认的告警阈值规则
    :return:
    - alert: exporter 异常
    annotations:
      consignee: omp@cloudwise.com
      description: 主机 {{ $labels.instance }} 中的 {{ $labels.app }}_exporter 已经down掉超过一分钟.
      summary: exporter status(instance {{ $labels.instance }})
    expr: exporter_status{env="default"} == 0
    for: 1m
    labels:
      severity: critical
    """
    builtins_rules = [
        {
            "alert": "实例宕机",
            "description": '实例 {{ $labels.instance }} '
                           'monitor_agent进程丢失或主机发生宕机已超过1分钟',
            "expr": 'sum(up{job="nodeExporter", env="default"}) by (instance)',
            "summary": "-",
            "compare_str": "<",
            "threshold_value": 1,
            "for_time": "60s",
            "severity": "critical",
            "labels": {
                "job": "nodeExporter",
                "severity": "critical"
            },
            "name": "实例宕机",
            "quota_type": 0,
            "status": 1,
            "service": "node",
            "forbidden": 2,

        },
        {
            "alert": "主机 CPU 使用率过高",
            "description": '主机 {{ $labels.instance }} CPU 使用率为 {{ $value | '
                           'humanize }}%, 大于阈值 90%',
            "expr": '(100 - sum(avg without (cpu)(irate('
                    'node_cpu_seconds_total{mode="idle", env="default"}['
                    '2m])))by (instance) * 100)',
            "summary": "-",
            "compare_str": ">=",
            "threshold_value": 90,
            "for_time": "60s",
            "severity": "critical",
            "labels": {
                "job": "nodeExporter",
                "severity": "critical"
            },
            "name": "CPU使用率",
            "quota_type": 0,
            "status": 1,
            "service": "node",
            "forbidden": 2

        },
        {
            "alert": "主机 CPU 使用率过高",
            "description": '主机 {{ $labels.instance }} CPU 使用率为 {{ $value | '
                           'humanize }}%, 大于阈值 80%',
            "expr": '(100 - sum(avg without (cpu)(irate('
                    'node_cpu_seconds_total{mode="idle", env="default"}['
                    '2m])))by (instance) * 100)',
            "compare_str": ">=",
            "summary": "-",
            "threshold_value": 80,
            "for_time": "60s",
            "severity": "warning",
            "labels": {
                "job": "nodeExporter",
                "severity": "warning"
            },
            "name": "CPU使用率",
            "quota_type": 0,
            "status": 1,
            "service": "node",
            "forbidden": 2
        },
        {
            "alert": "主机 内存 使用率过高",
            "description": '主机 {{ $labels.instance }} 内存使用率为 {{ $value | '
                           'humanize }}%, 大于阈值 90%',
            "expr": '(1 - (node_memory_MemAvailable_bytes{env="default"} / (node_memory_MemTotal_bytes{env="default"})))* 100',
            "summary": "-",
            "compare_str": ">=",
            "threshold_value": 90,
            "for_time": "60s",
            "severity": "critical",
            "labels": {
                "job": "nodeExporter",
                "severity": "critical"
            },
            "name": "内存使用率",
            "quota_type": 0,
            "status": 1,
            "service": "node",
            "forbidden": 2
        },
        {
            "alert": "主机 内存 使用率过高",
            "description": '主机 {{ $labels.instance }} 内存使用率为 {{ $value | '
                           'humanize }}%, 大于阈值 80%',
            "expr": '(1 - (node_memory_MemAvailable_bytes{env="default"} / (node_memory_MemTotal_bytes{env="default"})))* 100',
            "summary": "-",
            "compare_str": ">=",
            "threshold_value": 80,
            "for_time": "60s",
            "severity": "warning",
            "labels": {
                "job": "nodeExporter",
                "severity": "warning"
            },
            "name": "内存使用率",
            "quota_type": 0,
            "status": 1,
            "service": "node",
            "forbidden": 2
        },
        {
            "alert": "主机 根分区磁盘 使用率过高",
            "description": '主机 {{ $labels.instance }} 根分区使用率为 {{ $value | '
                           'humanize }}%, 大于阈值 90%',
            "expr": 'max((node_filesystem_size_bytes{env="default",'
                    'mountpoint="/"}-node_filesystem_free_bytes{'
                    'env="default",mountpoint="/"})*100/('
                    'node_filesystem_avail_bytes{env="default",'
                    'mountpoint="/"}+(node_filesystem_size_bytes{'
                    'env="default",'
                    'mountpoint="/"}-node_filesystem_free_bytes{'
                    'env="default",mountpoint="/"})))by(instance)',
            "summary": "-",
            "compare_str": ">=",
            "threshold_value": 90,
            "for_time": "60s",
            "severity": "critical",
            "labels": {
                "job": "nodeExporter",
                "severity": "critical"
            },
            "name": "根分区使用率",
            "quota_type": 0,
            "status": 1,
            "service": "node",
            "forbidden": 2
        },
        {
            "alert": "主机 根分区磁盘 使用率过高",
            "description": '主机 {{ $labels.instance }} 根分区使用率为 {{ $value | '
                           'humanize }}%, 大于阈值 90%',
            "expr": 'max((node_filesystem_size_bytes{env="default",'
                    'mountpoint="/"}-node_filesystem_free_bytes{'
                    'env="default",mountpoint="/"})*100/('
                    'node_filesystem_avail_bytes{env="default",'
                    'mountpoint="/"}+(node_filesystem_size_bytes{'
                    'env="default",'
                    'mountpoint="/"}-node_filesystem_free_bytes{'
                    'env="default",mountpoint="/"})))by(instance)',
            "summary": "-",
            "compare_str": ">=",
            "threshold_value": 80,
            "for_time": "60s",
            "severity": "warning",
            "labels": {
                "job": "nodeExporter",
                "severity": "warning"
            },
            "name": "根分区使用率",
            "quota_type": 0,
            "status": 1,
            "service": "node",
            "forbidden": 2
        },
        {
            "alert": "kafka消费组堆积数过多",
            "description": 'Kafka 消费组{{ $labels.consumergroup }}消息堆积数过多 {{ '
                           'humanize $value}} 大于阈值 4000',
            "expr": 'sum(kafka_consumergroup_lag{env="default"}) by ('
                    'consumergroup,instance,job,env)',
            "summary": "-",
            "compare_str": ">=",
            "threshold_value": 4000,
            "for_time": "60s",
            "severity": "warning",
            "labels": {
                "job": "kafkaExporter",
                "severity": "warning"
            },
            "name": "消费组堆积消息",
            "quota_type": 0,
            "status": 1,
            "service": "kafka",
            "forbidden": 1
        },
        {
            "alert": "kafka消费组堆积数过多",
            "description": 'Kafka 消费组{{ $labels.consumergroup }}消息堆积数过多 大于 {{ '
                           'humanize $value}} 大于阈值 5000',
            "expr": 'sum(kafka_consumergroup_lag{env="default"}) by ('
                    'consumergroup,instance,job,env)',
            "summary": "-",
            "compare_str": ">=",
            "threshold_value": 5000,
            "for_time": "60s",
            "severity": "critical",
            "labels": {
                "job": "kafkaExporter",
                "severity": "critical"
            },
            "name": "消费组堆积消息",
            "quota_type": 0,
            "status": 1,
            "service": "kafka",
            "forbidden": 1
        },
        {
            "alert": "exporter 异常",
            "description": '主机 {{ $labels.instance }} 中的 {{ $labels.app }}_exporter 已经down掉超过一分钟',
            "expr": 'exporter_status{env="default"}',
            "summary": "-",
            "compare_str": "==",
            "threshold_value": 0,
            "for_time": "60s",
            "severity": "critical",
            "labels": {
                "severity": "critical"
            },
            "name": "exporter异常",
            "quota_type": 0,
            "status": 1,
            "service": "node",
            "forbidden": 2
        },
        {
            "alert": "服务存活状态",
            "description": '主机 {{ $labels.instance }} 中的 服务 {{ $labels.app }} been down for more than a minute.',
            "expr": 'probe_success{env="default"}',
            "summary": "-",
            "compare_str": "==",
            "threshold_value": 0,
            "for_time": "60s",
            "severity": "critical",
            "labels": {
                "severity": "critical"
            },
            "name": "服务状态",
            "quota_type": 0,
            "status": 1,
            "service": "service",
            "forbidden": 2
        },
        {
            "alert": "jvm 文件句柄使用率过高",
            "description": '主机 {{ $labels.instance }}中的服务 {{ $labels.instance_name }} jvm 文件句柄使用率是{{ $value | '
                           'humanize }}%， 大于阈值 80%',
            "expr": '(process_files_open_files)*100/process_files_max_files',
            "summary": "-",
            "compare_str": ">",
            "threshold_value": 80,
            "for_time": "60s",
            "severity": "critical",
            "labels": {
                "severity": "critical"
            },
            "name": "jvm 文件句柄使用率",
            "quota_type": 0,
            "status": 1,
            "service": "service",
            "forbidden": 2
        },
        {
            "alert": "产品http请求 5XX 错误",
            "description": '主机 {{ $labels.instance }}中的服务 {{ $labels.instance_name }} ,请求方法是：{{ $labels.method }}，请求uri是 {{ $labels.uri }}发生http请求 status: {{ $labels.status }} 错误',
            "expr": 'http_server_requests_seconds_count{status=~\"5..\"}',
            "summary": "-",
            "compare_str": ">",
            "threshold_value": 0,
            "for_time": "60s",
            "severity": "critical",
            "labels": {
                "severity": "critical"
            },
            "name": "产品http请求 5XX 错误",
            "quota_type": 0,
            "status": 1,
            "service": "service",
            "forbidden": 2
        },
        {
            "alert": "heap使用率过高，可能导致oom",
            "description": '主机 {{ $labels.instance }}中的服务 {{ $labels.instance_name }} ,heap内存使用率为 {{ $value | '
                           'humanize }}%, 大于阈值 80%',
            "expr": 'sum(jvm_memory_used_bytes{area=~"heap"}) by (env, instance, job)/sum(jvm_memory_max_bytes{area=~"heap"}) by (env, instance, job) * 100',
            "summary": "-",
            "compare_str": ">",
            "threshold_value": 80,
            "for_time": "60s",
            "severity": "warning",
            "labels": {
                "severity": "warning"
            },
            "name": "heap使用率",
            "quota_type": 0,
            "status": 1,
            "service": "service",
            "forbidden": 2
        },
        {
            "alert": "gc后老年代所占内存比例过高，可能导致oom",
            "description": '主机 {{ $labels.instance }}中的服务 {{ $labels.instance_name }} ,gc后老年代所占内存比例为 {{ $value | '
                           'humanize }}%, 大于阈值 80%',
            "expr": 'sum(jvm_gc_live_data_size_bytes) by (env, instance, job)/sum(jvm_gc_max_data_size_bytes) by (env, instance, job) * 100',
            "summary": "-",
            "compare_str": ">",
            "threshold_value": 80,
            "for_time": "60s",
            "severity": "warning",
            "labels": {
                "severity": "warning"
            },
            "name": "gc后老年代所占内存率",
            "quota_type": 0,
            "status": 1,
            "service": "service",
            "forbidden": 2
        },
    ]
    rule = [
        {
            "name": "实例宕机",
            "description": '实例 {{ $labels.instance }} '
                           'monitor_agent进程丢失或主机发生宕机已超过1分钟',
            "expr": 'sum(up{job="nodeExporter", env="$env$"}) by (instance)',
            "service": "node",
        },
        {
            "name": "exporter异常",
            "description": '主机 {{ $labels.instance }} 中的 {{ $labels.app }}_exporter 已经down掉超过一分钟',
            "expr": 'exporter_status{env="$env$"}',
            "service": "service",
        },
        {
            "name": "服务状态",
            "description": '主机 {{ $labels.instance }} 中的 服务 {{ $labels.app }} been down for more than a minute.',
            "expr": 'probe_success{env="$env$"}',
            "service": "service",
        },
        {
            "name": "CPU使用率",
            "description": '主机 {{ $labels.instance }} CPU 使用率为 {{ $value | '
                           'humanize }}%, $compare_str$ 阈值 $threshold_value$%',
            "expr": '(100 - sum(avg without (cpu)(irate('
                    'node_cpu_seconds_total{mode="idle", env="$env$"}['
                    '2m])))by (instance) * 100)',
            "service": "node",
        },
        {
            "name": "内存使用率",
            "description": '主机 {{ $labels.instance }} 内存使用率为 {{ $value | '
                           'humanize }}%, $compare_str$阈值 $threshold_value$%',
            "expr": '(1 - (node_memory_MemAvailable_bytes{env="$env$"} / (node_memory_MemTotal_bytes{env="$env$"})))* 100',
            "service": "node",
        },
        {
            "name": "根分区使用率",
            "description": '主机 {{ $labels.instance }} 根分区使用率为 {{ $value | '
                           'humanize }}%, $compare_str$阈值 $threshold_value$%',
            "expr": 'max((node_filesystem_size_bytes{env="$env$",'
                    'mountpoint="/"}-node_filesystem_free_bytes{'
                    'env="$env$",mountpoint="/"})*100/('
                    'node_filesystem_avail_bytes{env="$env$",'
                    'mountpoint="/"}+(node_filesystem_size_bytes{'
                    'env="$env$",'
                    'mountpoint="/"}-node_filesystem_free_bytes{'
                    'env="$env$",mountpoint="/"})))by(instance)',
            "service": "node",
        },
        {
            "name": "消费组堆积消息",
            "description": 'Kafka 消费组{{ $labels.consumergroup }}消息堆积数过多  {{ '
                           'humanize $value}} $compare_str$阈值 $threshold_value$',
            "expr": 'sum(kafka_consumergroup_lag{env="$env$"}) by ('
                    'consumergroup,instance,job,env)',
            "service": "kafka",
        },
        {
            "name": "数据分区使用率",
            "description": '主机 {{ $labels.instance }} 数据分区使用率为 {{ $value | humanize }}%, $compare_str$阈值 $threshold_value$%',
            "expr": 'max((node_filesystem_size_bytes{env="$env$",mountpoint="$data_dir$"}-node_filesystem_free_bytes{env="$env$",mountpoint="$data_dir$"})*100/(node_filesystem_avail_bytes{env="$env$",mountpoint="$data_dir$"}+(node_filesystem_size_bytes{env="$env$",mountpoint="$data_dir$"}-node_filesystem_free_bytes{env="$env$",mountpoint="$data_dir$"}))) by (instance,env)',
            "service": "node",
        },
        {
            "name": "jvm 文件句柄使用率",
            "description": '主机 {{ $labels.instance }} jvm 文件句柄使用率为 {{ $value | humanize }}%, $compare_str$阈值 $threshold_value$%',
            "expr": '(process_files_open_files)*100/process_files_max_files',
            "service": "node",
        },
        {
            "name": "产品http请求 5XX 错误",
            "description": '主机 {{ $labels.instance }}中的服务 {{ $labels.instance_name }} ,请求方法是：{{ $labels.method }}，请求uri是 {{ $labels.uri }}发生http请求 status: {{ $labels.status }} 错误',
            "expr": 'http_server_requests_seconds_count{status=~\"5..\"}',
            "service": "node",
        },
        {
            "name": "heap 使用率过高，可能导致oom",
            "description": '主机 {{ $labels.instance }}中的服务 {{ $labels.instance_name }} ,heap内存使用率为 {{ $value | '
                           'humanize }}%, $compare_str$阈值 $threshold_value$',
            "expr": 'sum(jvm_memory_used_bytes{area=~"heap"}) by (env, instance, job)/sum(jvm_memory_max_bytes{area=~"heap"}) by (env, instance, job) * 100',
            "service": "service",
        },
        {
            "name": "gc后老年代所占内存比例过高，可能导致oom",
            "description": '主机 {{ $labels.instance }}中的服务 {{ $labels.instance_name }} ,gc后老年代所占内存比例为 {{ $value | '
                           'humanize }}%, $compare_str$阈值 $threshold_value$',
            "expr": 'sum(jvm_gc_live_data_size_bytes) by (env, instance, job)/sum(jvm_gc_max_data_size_bytes) by (env, instance, job) * 100',
            "service": "service",
        },
    ]
    try:
        for info in builtins_rules:
            hash_value = get_hash_value(info.get("expr"), info.get("severity"))
            alert = AlertRule.objects.filter(expr=info.get("expr"), severity=info.get("severity"),
                                             service=info.get("service"))
            info.update(hash_data=hash_value)
            if alert:
                alert.update(**info)
            else:
                AlertRule(**info).save()
    except Exception as e:
        print(f"初始化规则数据失败{e}")
    for rule_info in rule:
        if Rule.objects.filter(name=rule_info.get("name")).exists():
            continue
        Rule(**rule_info).save()


def create_self_healing_setting():
    """添加默认自愈策略"""
    # self_obj = SelfHealingSetting.objects.all().first()
    # if not self_obj.repair_instance:
    #     self_obj.repair_instance = ["all"]
    #     self_obj.save()


class ClearDb:

    def alert(self):
        return

    def health(self):
        return

    def __call__(self, *args, **kwargs):
        for k, v in CLEAR_DB.items():
            obj = getattr(self, k)
            if not obj:
                print("改函数未定义")
        # ToDo 暂时无其他逻辑以后补充
        data = {
            "is_on": True,
            'task_func': 'services.tasks.clear_db',
            'task_name': 'self_clear_cron_db',
            'crontab_detail': dict(
                day_of_month='*', day_of_week='*',
                hour="00", minute="00",
                month_of_year='*')
        }
        change_task(1, data)


def create_back_settings():
    init_db = [
        {"field_k": "db_name",
         "field_v": "test_db",
         "notes": "数据库名称,适用mysql,postgre"},
        {"field_k": "no_pass",
         "field_v": "true",
         "notes": "无需认证,非必填,适用mysql"},
        {
            "field_k": "need_push",
            "field_v": "true",
            "notes": "异地备份,非必填,适用全部"
        },
        {
            "field_k": "need_app",
            "field_v": "true",
            "notes": "安装路径备份,非必填,适用pg"
        }
    ]

    his_obj = BackupHistory.objects.all()

    for i in his_obj:
        if "," in i.content:
            i.delete()

    for v in init_db:
        BackupCustom.objects.get_or_create(**v)


def repair_dirty_data():
    detail_objs = DetailInstallHistory.objects.all()
    for obj in detail_objs:
        run_user = Host.objects.filter(ip=obj.service.ip).first().username
        if run_user != 'root':
            obj.install_detail_args['run_user'] = run_user
            for i in obj.install_detail_args.get('install_args', []):
                if i.get('key', '') == 'run_user':
                    i['default'] = run_user
            obj.save()
        else:
            continue
    service_obj = Service.split_objects.all()
    for ser in service_obj:
        if ser.service.app_name == "hadoop":
            ser.service_status = Service.SERVICE_STATUS_NORMAL
            ser.save()


def main():
    """
    基础数据创建流程
    :return:
    """
    # 创建默认用户
    create_default_user()
    # 创建监控配置项
    create_default_monitor_url()
    # 创建默认环境
    create_default_env()
    # 添加默认告警阈值规则
    create_threshold()
    # 添加默认自愈策略
    create_self_healing_setting()
    # 创建清理任务
    ClearDb()()
    # 添加告警策略
    create_back_settings()
    # 升级是清洗以前问题数据
    repair_dirty_data()


if __name__ == '__main__':
    main()
