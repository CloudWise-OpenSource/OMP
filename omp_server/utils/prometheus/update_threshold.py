# -*- coding: utf-8 -*-
import argparse
import os

import requests
import yaml
import logging

from omp_server.settings import PROJECT_DIR


logger = logging.getLogger("server")

description = {
    "cpu_used": "主机 {{ $labels.instance }} CPU 使用率为 {{ $value | humanize }}%, 大于阈值 $condition_value$%",
    "memory_used": "主机 {{ $labels.instance }} 内存使用率为 {{ $value | humanize }}%，大于阈值 $condition_value$%",
    "disk_root_used": "主机 {{ $labels.instance }} 根分区使用率为 {{ $value | humanize }}%, 大于 阈值 $condition_value$%",
    "disk_data_used": "主机 {{ $labels.instance }} 数据分区使用率为 {{ $value | humanize }}%, 大于 阈值 $condition_value$%",
    "kafka_consumergroup_lag": "Kafka 消费组{{ $labels.consumergroup }}消息堆积数过多  {{ humanize $value }}"
}
expr = {
    "cpu_used": "(100 - sum(avg without (cpu)(irate(node_cpu_seconds_total{mode='idle', "
                "env=\"$env_name$\"}[2m]))) by (instance) * 100) $condition$ $condition_value$",
    "memory_used": "(1 - (node_memory_MemAvailable_bytes{env=\"$env_name$\"} / (node_"
                   "memory_MemTotal_bytes{env=\"$env_name$\"}))) * 100 $condition$ $condition_value$",
    "disk_root_used": "max((node_filesystem_size_bytes{env=\"$env_name$\","
                      "mountpoint=\"/\"}-node_filesystem_free_bytes"
                      "{env=\"$env_name$\",mountpoint=\"/\"}) *100/(node_filesystem_avail_"
                      "bytes{env=\"$env_name$\",mountpoint=\"/\"}+(node_filesystem_size_bytes{"
                      "env=\"$env_name$\",mountpoint=\"/\"}-node"
                      "_filesystem_free_bytes{env=\"$env_name$\",mountpoint=\"/\"})))by(instance)"
                      " $condition$ $condition_value$",
    "disk_data_used": "max((node_filesystem_size_bytes{env=\"$env_name$\","
                      "mountpoint=\"$disk_data_path$\"}-node_filesystem_free_bytes"
                      "{env=\"$env_name$\",mountpoint=\"$disk_data_path$\"}) *100/(node_filesystem_avail_"
                      "bytes{env=\"$env_name$\",mountpoint=\"$disk_data_path$\"}+(node_filesystem_size_bytes{"
                      "env=\"$env_name$\",mountpoint=\"$disk_data_path$\"}-node"
                      "_filesystem_free_bytes{env=\"$env_name$\",mountpoint=\"$disk_data_path$\"})))by(instance)"
                      " $condition$ $condition_value$",
    "kafka_consumergroup_lag": "sum(kafka_consumergroup_lag{env=\"$env_name$\"}) by (consumergroup,instance,job,env) $condition$ $condition_value$"

}


def gen_summary(index_type):
    return replace_value("$index_type$ (instance {{ $labels.instance }})", index_type=index_type)


def replace_value(line, env_name=None, condition=None, condition_value=None, alert_level=None, index_type=None,
                  disk_data_path=None):
    if env_name:
        line = line.replace("$env_name$", str(env_name))
    if condition:
        line = line.replace("$condition$", str(condition))
    if condition_value:
        line = line.replace("$condition_value$", str(condition_value))
    if alert_level:
        line = line.replace("$alert_level$", str(alert_level))
    if index_type:
        line = line.replace("$index_type$", str(index_type))
    if disk_data_path:
        line = line.replace("$disk_data_path$", str(disk_data_path))
    return line


def update_node_rule_yaml(quotes_info):
    """
    更新主机指标文件
    """
    env_name = quotes_info.get("env_name")
    node_rule_yml_path = os.path.join(PROJECT_DIR, 'component',
                                      'prometheus/conf/rules',
                                      '{}_node_rule.yml'.format(env_name))
    instance_alert = {
        "alert": "instance down",
        "annotations": {
            "consignee": "{}".format(""),  # TODO
            "description": "实例 {{ $labels.instance }} monitor_agent进程丢失或主机发生宕机已超过1分钟",
            "summary": "instance down alert({{ $labels.instance }})"
        },
        "expr": "sum(up{job=\"nodeExporter\", env=\'%s\'}) by (instance) < 1" % env_name,
        "for": "1m",
        "labels": {
            "job": "nodeExporter",
            "severity": "critical"
        }
    }
    node_rules = {"name": "node alert", "rules": [instance_alert]}
    dict_total_rules = {"groups": [node_rules]}
    node_quotes = quotes_info.get("hosts")
    env_name = quotes_info.get("env_name")
    disk_data_path = quotes_info.get("disk_data_path", None)
    try:
        for host_quote_info in node_quotes:
            index_type = host_quote_info.get("index_type")
            if index_type == "disk_data_used":
                if not disk_data_path:
                    continue
            alert_level = host_quote_info.get("alert_level")
            condition_value = host_quote_info.get("condition_value")
            condition = host_quote_info.get("condition")
            quote_info = {
                "alert": "host {} alert".format(index_type),
                "annotations": {
                    "consignee": "{}".format(""),  # TODO
                    "description": replace_value(description.get(index_type), condition_value=condition_value),
                    "summary": gen_summary(index_type=index_type),
                },
                "expr": replace_value(expr.get(index_type), env_name=env_name, condition=condition,
                                      condition_value=condition_value, disk_data_path=disk_data_path),
                "for": "1m",
                "labels": {
                    "job": "nodeExporter",
                    "severity": alert_level,
                }

            }
            logger.info(quote_info)
            node_rules["rules"].append(quote_info)
        logger.info('开始更新告警规则文件{}'.format(node_rule_yml_path))

        with open(node_rule_yml_path, "w") as fw:
            yaml.dump(dict_total_rules, fw, allow_unicode=True)
        logger.info("更新主机告警规则文件成功")
        return True
    except Exception as e:
        logger.error(e)
        return False


def update_service_rule_yaml(quotes_info):
    """
    更新服务指标文件
    """
    env_name = quotes_info.get("env_name")
    service_rule_yml_path = os.path.join(PROJECT_DIR, 'component',
                                         'prometheus/conf/rules',
                                         '{}_service_status_rule.yml'.format(env_name))
    instance_alert = {
        "alert": "app state",
        "annotations": {
            "consignee": "{}".format(""),  # TODO
            "description": "主机 {{ $labels.instance }} 中的 服务 {{ $labels.app }} 已经down掉超过一分钟.",
            "summary": "app state(instance {{ $labels.instance }})"
        },
        "expr": "probe_success{env=\'%s\'} == 0 " % env_name,
        "for": "1m",
        "labels": {
            "severity": "critical"
        }
    }
    service_rules = {"name": "App state", "rules": [instance_alert]}
    dict_total_rules = {"groups": [service_rules]}
    service_quotes = quotes_info.get("services")
    try:
        for service_name, service_quote_info in service_quotes.items():
            for service_quote in service_quote_info:
                index_type = service_quote.get("index_type")
                alert_level = service_quote.get("alert_level")
                condition_value = service_quote.get("condition_value")
                condition = service_quote.get("condition")
                quote_info = {
                    "alert": "{} {} alert".format(service_name, index_type),
                    "annotations": {
                        "consignee": "{}".format(""),  # TODO
                        "description": replace_value(description.get(index_type), condition_value=condition_value),
                        "summary": gen_summary(index_type=index_type),
                    },
                    "expr": replace_value(expr.get(index_type), env_name=env_name, condition=condition,
                                          condition_value=condition_value),
                    "for": "1m",
                    "labels": {
                        "severity": alert_level,
                    }

                }
                logger.info(quote_info)
                service_rules["rules"].append(quote_info)
        logger.info('开始更新服务告警规则文件{}'.format(service_rule_yml_path))
        with open(service_rule_yml_path, "w") as fw:
            yaml.dump(dict_total_rules, fw, allow_unicode=True)
        logger.info("更新服务告警规则文件成功")
        return True
    except Exception as e:
        logger.error(e)
        return False


def config_update(quotes_info):
    """
    :param quotes_info: 相关指标阈值信息
    :return:
    {"env_name": "env_name",
    "hosts": [
        {"index_type": "cpu_used","condition": ">=","condition_value": "80","alert_level": "warning"},
        {"index_type": "cpu_used","condition": ">=","condition_value": "90","alert_level": "critical"},
        {"index_type": "memory_used","condition": ">=","condition_value": "80","alert_level": "warning"},
        {"index_type": "memory_used","condition": ">=","condition_value": "90","alert_level": "critical"},
        {"index_type": "disk_root_used","condition": ">=","condition_value": "80","alert_level": "warning"},
        {"index_type": "disk_root_used","condition": ">=","condition_value": "90","alert_level": "critical"},
        {"index_type": "disk_data_used","condition": ">","condition_value": "80","alert_level": "warning"},
        {"index_type": "disk_data_used","condition": ">","condition_value": "90","alert_level": "critical"}
            ],
    "services": {
        "kafka": [
            {"index_type": "kafka_consumergroup_lag","condition": ">","condition_value": 400,"alert_level": "warning"},
            {"index_type": "kafka_consumergroup_lag","condition": ">","condition_value": 600,"alert_level": "critical"}
                ]
                }
    }
    """
    logger.info('收到阈值更新json：{}'.format(quotes_info))
    # quotes_info = json.loads(quotes_info)
    # 更新主机规则文件
    update_node_mark = update_node_rule_yaml(quotes_info)
    if not update_node_mark:
        logger.error("更新主机告警规则失败")
    # 更新服务规则文件
    update_service_mark = update_service_rule_yaml(quotes_info)
    if not update_service_mark:
        logger.error("更新服务告警规则失败")
    try:
        from promemonitor.prometheus import Prometheus
        url = "http://{}/-/reload".format(Prometheus.get_prometheus_config())  # NOQA
        response = requests.request("POST", url)
        if response.status_code == 200:
            logger.info('重载prometheus配置成功！')
        else:
            logger.error('重载prometheus配置失败！')
    except ConnectionRefusedError:
        logger.error('重载prometheus配置失败！')
    return True, None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        usage="it's usage tip.", description="help info.")
    parser.add_argument("--threshold-json",
                        dest="threshold_json", help="the json of threshold")
    args = parser.parse_args()

    threshold_json = args.threshold_json

    config_update(threshold_json)
