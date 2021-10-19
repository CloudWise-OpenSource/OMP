# -*- coding: utf-8 -*-
# Project: prometheus_utils
# Author: jon.liu@yunzhihui.com
# Create time: 2021-10-11 14:31
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
prometheus更新监控项使用的工具集
"""

import os
import json
import pickle
import shutil
import logging

# import requests
from ruamel.yaml import YAML

from omp_server.settings import PROJECT_DIR
# from utils.parse_config import MONITOR_PORT

logger = logging.getLogger("server")

AGREE = "http"
# 内置exporter列表
EXPORTERS = [
    "beanstalk",
    "clickhouse",
    "elasticsearch",
    "httpd",
    "kafka",
    "mysql",
    "node",
    "postgreSql",
    "redis",
    "tengine",
    "zookeeper",
]

METRICS = {
    "arangodb": "_admin/metrics",
    "nacos": "nacos/actuator/prometheus",
}


class PrometheusUtils(object):
    """ prometheus工具集 """

    def __init__(self):
        self.prometheus_conf_path = os.path.join(
            PROJECT_DIR, "component/prometheus/conf/prometheus.yml")
        self.prometheus_rules_path = os.path.join(
            PROJECT_DIR, "component/prometheus/conf/rules")
        self.prometheus_targets_path = os.path.join(
            PROJECT_DIR, "component/prometheus/conf/targets")
        self.prometheus_node_rule_tpl = os.path.join(
            PROJECT_DIR,
            "package_hub/prometheus_rules_template/node_rule.yml")
        self.prometheus_node_data_rule_tpl = os.path.join(
            PROJECT_DIR,
            "package_hub/prometheus_rules_template/node_data_rule.yml")
        self.prometheus_service_status_rule_tpl = os.path.join(
            PROJECT_DIR,
            "package_hub/prometheus_rules_template/service_status_rule.yml")
        self.prometheus_exporter_status_rule_tpl = os.path.join(
            PROJECT_DIR,
            "package_hub/prometheus_rules_template/exporter_status_rule.yml")
        # 邮件地址
        self.email_address = "omp@cloudwise.com"
        self.monitor_port = 19031
        self.node_exporter_targets_file = os.path.join(
            self.prometheus_targets_path,
            "nodeExporter_all.json"
        )
        self.agent_request_header = {}

    @staticmethod
    def replace_placeholder(path, placeholder_list):
        """
        替换文件中的占位符
        :param path: 要替换的文件路径
        :param placeholder_list: 占位符字典列表 [{"key":"value"}]
        :return:
        """
        if not os.path.isfile(path):
            return False, f"{path} not exists!"
        with open(path, "r") as f:
            data = f.read()
            for item in placeholder_list:
                for k, v in item.items():
                    placeholder = "${{{}}}".format(k)
                    data = data.replace(placeholder, str(v))
        with open(path, "w") as f:
            f.write(data)

    @staticmethod
    def json_distinct(iterable_lst):
        """
        json元素去重
        :param iterable_lst: 去重对象
        :return: 去重后的对象
        """
        res = []
        for instance in iterable_lst:
            res.append(pickle.dumps(instance))
        res = set(res)
        return [pickle.loads(i) for i in res]

    @staticmethod
    def get_dic_from_yaml(file_path):
        """
        从yaml中获取字典
        :param file_path: 文件路径
        :return:
        """
        with open(file_path, "r", encoding="utf8") as fp:
            content = fp.read()
        my_yaml = YAML()
        return my_yaml.load(content)

    @staticmethod
    def write_dic_to_yaml(dic, file_path):
        """
        将字典写入yaml
        :param dic: 字典数据
        :param file_path: yaml文件路径
        :return:
        """
        my_yaml = YAML()
        with open(file_path, "w", encoding="utf8") as fp:
            my_yaml.dump(dic, fp)

    @staticmethod
    def get_expr(num, env, data_path):
        """
        获取prometheus数据分区匹配规则
        :param num:
        :param env:
        :param data_path:
        :return:
        """
        _expr = \
            """max((node_filesystem_size_bytes{env="ENV",
            mountpoint="DATA_PATH"}-node_filesystem_free_bytes{env="ENV",
            mountpoint="DATA_PATH"})*100/(node_filesystem_avail_bytes{
            env="ENV",mountpoint="DATA_PATH"}+(node_filesystem_size_bytes{
            env="ENV",mountpoint="DATA_PATH"}-node_filesystem_free_bytes{
            env="ENV",mountpoint="DATA_PATH"})))by(instance,env)>= """
        return _expr.replace("ENV", env).replace(
            "DATA_PATH", data_path).replace("\n", "").replace(
            " ", ""
        ) + str(num)

    def make_data_node_rule(self, level, data_path, env="default"):
        """
        生成数据分区告警规则
        :param level: 告警级别
        :param data_path: 数据分区路径
        :param env: 主机所属环境
        :return:
        """
        des = "主机 {{ $labels.instance }} 数据分区使用率为 " \
              "{{ $value | humanize }}%, 大于阈值 "
        return {
            "alert": "host disk_data_used alert",
            "annotations": {
                "disk_data_path": f"{data_path}",
                "consignee": f"{self.email_address}",
                "description":
                    des + "90%" if level == "critical" else des + "80%",
                "summary": "disk_data_used (instance {{ $labels.instance }})"
            },
            "expr": self.get_expr(
                90 if level == "critical" else 80, env, data_path),
            "for": "1m",
            "labels": {
                "job": "nodeExporter",
                "severity": level
            }
        }

    def update_node_data_rule(self, data_path, env="default"):
        """
        更新主机data disk分区告警规则，当添加主机时使用
        :rtype: tuple
        :param data_path: 数据分区地址
        :param env: 主机所属环境
        :return:
        """
        logger.info(f"Start update_node_data_rule: {data_path}; {env}")
        data_rule_path = os.path.join(
            self.prometheus_rules_path, f"{env}_node_data_rule.yml")
        _critical = self.make_data_node_rule("critical", data_path, env)
        _warning = self.make_data_node_rule("warning", data_path, env)
        _critical_flag = True
        _warning_flag = True
        if not os.path.exists(data_rule_path):
            node_data_rule_dic = {
                "groups": [
                    {
                        "name": "node data disk alert",
                        "rules": [
                            _critical, _warning
                        ]
                    }
                ]
            }
            self.write_dic_to_yaml(node_data_rule_dic, data_rule_path)
            return True, "success by new create"
        node_data_rule_dic = self.get_dic_from_yaml(data_rule_path)
        for item in node_data_rule_dic.get("groups", []):
            for el in item.get("rules", []):
                if el.get("annotations", {}).get("disk_data_path") \
                        == data_path and el.get("labels", {}).get("severity") \
                        == "critical":
                    _critical_flag = False
                if el.get("annotations", {}).get("disk_data_path") \
                        == data_path and el.get("labels", {}).get(
                    "severity") \
                        == "warning":
                    _warning_flag = False
        for item in node_data_rule_dic.get("groups", []):
            if _critical_flag:
                item["rules"].append(_critical)
            if _warning_flag:
                item["rules"].append(_warning)
        self.write_dic_to_yaml(node_data_rule_dic, data_rule_path)
        return True, "success"

    def add_rules(self, rule_type, env="default"):
        """
        rule_type:
            node: 主机告警规则
            service: 服务状态告警规则
            exporter: exporter状态告警规则
        更新prometheus rules规则, 建议在安装prometheus时进行更新
        :param rule_type: 更新方式
        :param env: 环境信息
        :return:
        """
        logger.info(f"Start add rules: {rule_type}; {env}")
        rules_file_placeholder_script = [
            {"ENV": env},
            {"EMAIL_ADDRESS": self.email_address}
        ]
        if rule_type == "node":
            node_rule_yml_file = os.path.join(
                self.prometheus_rules_path,
                f"{env}_node_rule.yml"
            )
            if not os.path.exists(node_rule_yml_file):
                shutil.copy(
                    self.prometheus_node_rule_tpl,
                    node_rule_yml_file
                )
                self.replace_placeholder(
                    node_rule_yml_file,
                    rules_file_placeholder_script
                )
        elif rule_type == "service":
            status_rule_yml_file = os.path.join(
                self.prometheus_rules_path,
                f"{env}_service_status_rule.yml"
            )
            if not os.path.exists(status_rule_yml_file):
                shutil.copy(
                    self.prometheus_service_status_rule_tpl,
                    status_rule_yml_file
                )
                self.replace_placeholder(
                    status_rule_yml_file,
                    rules_file_placeholder_script
                )
        elif rule_type == "exporter":
            exporter_rule_yml_file = os.path.join(
                self.prometheus_rules_path,
                f"{env}_exporter_status_rule.yml")
            if not os.path.exists(exporter_rule_yml_file):
                shutil.copy(
                    self.prometheus_exporter_status_rule_tpl,
                    exporter_rule_yml_file
                )
                self.replace_placeholder(
                    exporter_rule_yml_file,
                    rules_file_placeholder_script
                )
        else:
            return False, "not support!"
        return True, "success"

    def delete_rules(self, rule_type, env="default"):
        """
        删除prometheus rules的规则
        :param rule_type: 删除类型
        :param env: 环境名称
        :return:
        """
        if rule_type not in ("node", "service", "exporter"):
            return False, "not support!"
        if rule_type == "node":
            rule_yml_file = os.path.join(
                self.prometheus_rules_path,
                f"{env}_node_rule_yml"
            )
        else:
            rule_yml_file = os.path.join(
                self.prometheus_rules_path,
                f"{env}_{rule_type}_status_rule.yml"
            )
        if os.path.exists(rule_yml_file):
            os.remove(rule_yml_file)
        return True, "success"

    def add_node(self, nodes_data):
        """
        nodes_data = [
            {
                "data_path": "/data",
                "env": "default",
                "ip": "127.0.0.1"
            }
        ]
        添加主机到自监控系统
        :param nodes_data: 新增的主机信息
        :return:
        """
        logger.info(f"Start add node: {nodes_data}")
        if not nodes_data:
            return False, "nodes_data can not be null"
        node_target_list = list()
        # 遍历主机数据，添加主机层的告警规则
        for item in nodes_data:
            node_target_ele = {
                "targets": [item["ip"] + ":" + str(self.monitor_port)],
                "labels": {
                    "instance": item["ip"],
                    "env": item["env"]}
            }
            node_target_list.append(node_target_ele)
            # 更新主机node rule
            self.add_rules("node", item["env"])
            # 更新exporter的告警规则
            self.add_rules("exporter", item["env"])
            # 更新数据分区的告警规则
            if item["data_path"]:
                self.update_node_data_rule(item["data_path"], item["env"])
        # 增加主机的target配置文件(prometheus/conf/targets)
        if os.path.exists(self.node_exporter_targets_file):
            with open(self.node_exporter_targets_file, "r") as f:
                content = f.read()
                if content:
                    old_node_target_list = json.loads(content)
                    node_target_list.extend(old_node_target_list)
        node_target_list = self.json_distinct(node_target_list)
        with open(self.node_exporter_targets_file, "w") as f2:
            json.dump(node_target_list, f2, ensure_ascii=False, indent=4)
        return True, "success"

    def delete_node(self, nodes_data):
        """
        从自监控系统删除主机信息
        :param nodes_data: 要删除的主机信息
        :return:
        """
        if not nodes_data:
            return False, "nodes_data can not be null"
        if os.path.exists(self.node_exporter_targets_file):
            with open(self.node_exporter_targets_file, "r") as f:
                content = f.read()
                if content:
                    node_target_list = json.loads(content)
                else:
                    node_target_list = list()
        else:
            return False, f"{self.node_exporter_targets_file} not exists!"
        if not node_target_list:
            return True, "success"
        for item in nodes_data:
            ip = item["ip"]
            for node in node_target_list:
                if ip in node["labels"]["instance"]:
                    node_target_list.remove(node)
                    break
        with open(self.node_exporter_targets_file, "w") as f2:
            json.dump(node_target_list, f2, ensure_ascii=False, indent=4)
        return True, "success"
