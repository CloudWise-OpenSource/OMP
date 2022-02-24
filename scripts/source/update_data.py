# -*- coding: utf-8 -*-
# Project: update_data
# Author: jon.liu@yunzhihui.com
# Create time: 2021-09-18 10:36
# IDE: PyCharm
# Version: 1.0
# Introduction:

import os
import sys

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
from utils.parse_config import MONITOR_PORT
from db_models.models import Env
from db_models.models import AlertRule,Rule
from db_models.models import SelfHealingSetting


def create_default_user():
    """
    创建基础用户
    :return:
    """
    username = "admin"
    password = "Common@123"
    if UserProfile.objects.filter(username=username).count() != 0:
        return
    UserProfile.objects.create_superuser(
        username=username,
        password=password,
        email="admin@yunzhihui.com"
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
            "quota_type": 0,
            "status": 1,
            "service": "node",

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
            "quota_type": 0,
            "status": 1,
            "service": "node",

        },
        {
            "alert": "主机 CPU 使用率过高",
            "description": '主机 {{ $labels.instance }} CPU 使用率为 {{ $value | '
                           'humanize }}%, 大于阈值 5%',
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
            "quota_type": 0,
            "status": 1,
            "service": "node",
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
            "quota_type": 0,
            "status": 1,
            "service": "node",
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
            "quota_type": 0,
            "status": 1,
            "service": "node",
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
            "quota_type": 0,
            "status": 1,
            "service": "node",
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
            "quota_type": 0,
            "status": 1,
            "service": "node",
        },
        {
            "alert": "kafka消费组堆积数过多",
            "description": 'Kafka 消费组{{ $labels.consumergroup }}消息堆积数过多  {{ '
                           'humanize $value}}',
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
            "quota_type": 0,
            "status": 1,
            "service": "kafka",
        },
        {
            "alert": "kafka消费组堆积数过多",
            "description": 'Kafka 消费组{{ $labels.consumergroup }}消息堆积数过多  {{ '
                           'humanize $value}}',
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
            "quota_type": 0,
            "status": 1,
            "service": "kafka",
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
                "job": "nodeExporter",
                "severity": "critical"
            },
            "quota_type": 0,
            "status": 1,
            "service": "node",
        },
        {
            "alert": "app state",
            "description": '主机 {{ $labels.instance }} 中的 服务 {{ $labels.app }} 已经down掉超过一分钟.',
            "expr": 'probe_success{env="default"}',
            "summary": "-",
            "compare_str": "==",
            "threshold_value": 0,
            "for_time": "60s",
            "severity": "critical",
            "labels": {
                "job": "nodeExporter",
                "severity": "critical"
            },
            "quota_type": 0,
            "status": 1,
            "service": "node",
        },

    ]
    rule = [
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
            "name":"根分区使用率",
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

    ]
    for info in builtins_rules:
        if AlertRule.objects.filter(
                alert=info.get("alert"),
                severity=info.get("severity"),
                service=info.get("service"),
        ).exists():
            continue
        AlertRule(**info).save()
    for rule_info in rule:
        if Rule.objects.filter(name=rule_info.get("name")).exists():
            continue
        Rule(**rule_info).save()

def create_self_healing_setting():
    """添加默认自愈策略"""
    if SelfHealingSetting.objects.all().count() != 0:
        return
    default_setting = dict()
    default_setting = {
        "used": False,
        "alert_count": 1,
        "max_healing_count": 5,
        "env_id": 1
    }
    SelfHealingSetting(**default_setting).save()


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


if __name__ == '__main__':
    main()
