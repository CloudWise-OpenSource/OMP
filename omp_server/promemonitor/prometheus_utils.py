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
import requests
import logging

from omp_server.settings import PROJECT_DIR
from utils.parse_config import MONITOR_PORT

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
            PROJECT_DIR, "package_hub/prometheus_rules_template/node_rule.yml")
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

    def add_rules(self, rule_type, env="default"):
        """
        更新prometheus rules规则
        :param rule_type: 更新方式
        :param env: 环境信息
        :return:
        """
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
        elif rule_type == "status":
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
        添加主机到自监控系统
        :param nodes_data: 新增的主机信息
        :return:
        """
        if not nodes_data:
            return False, "nodes_data can not be null"
        node_target_list = list()
        for item in nodes_data:
            node_target_ele = {
                "targets": [item["ip"] + ":" + str(self.monitor_port)],
                "labels": {
                    "instance": item["ip"],
                    "env": item["env"]}
            }
            node_target_list.append(node_target_ele)
            self.add_rules("exporter", item["env"])

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
            return None
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

    @staticmethod
    def get_service_port(service_exporter_name):
        """
        获取服务对应的exporter端口
        :param service_exporter_name:服务名
        :return:
        """
        # 补充获取服务exporter数据
        port = MONITOR_PORT.get(service_exporter_name)
        return port

    def request_to_agent(self, dest_ip, dest_url, data):
        """
        更新Agent中的服务配置
        :param dest_ip: 目标主机ip
        :param dest_url: 目标主机Agent的url
        :param data: 请求数据
        :return:
        """
        try:
            result = requests.post(
                dest_url, headers=self.agent_request_header,
                data=data
            ).json()
            if result["return_code"] == 0:
                logger.info(f"向{dest_ip}更新服务配置成功！")
                return True, "success"
            logger.error(f"向{dest_ip}更新服务配置失败！")
            return False, "failed"
        except requests.exceptions.ConnectionError:
            logger.error(
                f"向{dest_ip}更新服务配置失败! Agent ConnectionError")
            return False, "failed"

    def _add_agent_service(self, dest_ip, services_data):
        """
        向Agent上添加服务信息
        :param dest_ip: 目标ip
        :param services_data: 服务数据
        :return:
        """
        json_content = list()
        json_dict = dict()
        dest_url = \
            f"{AGREE}://{dest_ip}:{self.monitor_port}/update/service/add"
        for sd in services_data:
            service_temp_data = dict()
            service_temp_data["service_port"] = sd.get("port")
            if sd.get("service_name") in EXPORTERS:
                service_temp_data["exporter_port"] = self.get_service_port(
                    "{}Exporter".format(sd.get("service_name")))
            else:
                service_temp_data["exporter_port"] = sd.get("metrics", 0)
            if sd.get("service_name") in METRICS.keys():
                service_temp_data["exporter_metric"] = METRICS.get(
                    sd.get("service_name"), 0)
            else:
                service_temp_data["exporter_metric"] = "metrics"
            service_temp_data["username"] = sd.get("username", '')
            service_temp_data["password"] = sd.get("password", '')
            service_temp_data["name"] = sd.get("service_name")
            service_temp_data["only_process"] = sd.get("only_process")
            service_temp_data["process_key_word"] = sd.get(
                "process_key_word")
            json_content.append(service_temp_data)
        json_dict["services"] = json.dumps(json_content)
        return self.request_to_agent(dest_ip, dest_url, json_dict)

    def _delete_agent_service(self, dest_ip, services_data):
        """
        请求监控agent，删除部分服务
        :param dest_ip: 目标ip
        :param services_data: 服务数据
        :return:
        """
        json_content = list()
        json_dict = dict()
        dest_url = \
            f"{AGREE}://{dest_ip}:{self.monitor_port}/update/service/delete"
        for sd in services_data:
            json_content.append(sd.get("service_name"))
        json_dict["services"] = json.dumps(json_content)
        return self.request_to_agent(dest_ip, dest_url, json_dict)

    def update_agent_service(self, dest_ip, action, services_data):
        """
        接收omp传来的参数，解析后发送到monitor_agent
        :param action: 更新动作 add or delete
        :param services_data: 要更新的服务信息
        :param dest_ip:
        :return:
        """
        if action not in ("add", "delete"):
            return False, "not support action!"
        if action == "add":
            return self._add_agent_service(dest_ip, services_data)
        else:
            return self._delete_agent_service(dest_ip, services_data)

    def add2self_exporter(self, service_data):
        """
        添加有exporter的组件信息到各自的exporter监控
        :param service_data: 服务信息
        :return:
        """
        with open(self.prometheus_conf_path, "r") as fr:
            fr_content = fr.read()
        job_name_str = "{}Exporter".format(service_data.get("service_name"))
        if job_name_str not in fr_content:  # TODO 采用读写yaml文件的方式
            new_job_chunk = \
                "" \
                "\n  - job_name: {}Exporter" \
                "\n    metrics_path: /metrics/monitor/{}" \
                "\n    scheme: http" \
                "\n    file_sd_configs:" \
                "\n    - refresh_interval: 30s" \
                "\n      files:" \
                "\n      - targets/{}Exporter_all.json".format(
                    service_data.get("service_name"),
                    service_data.get("service_name"),
                    service_data.get("service_name"))
            fw_content = fr_content + new_job_chunk
            with open(self.prometheus_conf_path, "w") as fw:
                fw.write(fw_content)
        self_exporter_target_file = os.path.join(
            self.prometheus_targets_path,
            "{}Exporter_all.json".format(service_data["service_name"]))
        self_target_list = list()
        self_target_ele = {
            "labels": {
                "instance": "{}".format(service_data["ip"]),
                "env": "{}".format(service_data["env"])
            },
            "targets": [
                "{}:{}".format(service_data["ip"], self.monitor_port)
            ]
        }
        self_target_list.append(self_target_ele)

        if os.path.exists(self_exporter_target_file):
            with open(self_exporter_target_file, "r") as f:
                content = f.read()
                if content:
                    old_self_target_list = json.loads(content)
                    self_target_list.extend(old_self_target_list)
        self_target_list = self.json_distinct(self_target_list)

        with open(self_exporter_target_file, "w") as f2:
            json.dump(self_target_list, f2, ensure_ascii=False, indent=4)

    def add_service(self, services_data):
        """
        添加服务到自监控
        :param services_data: 要增加的服务信息
        :return:
        """
        if not services_data:
            return False, "services_data can not be null"

        for sd in services_data:
            if not sd:
                continue
            self.add2self_exporter(sd)
            self.update_agent_service(sd.get("ip"), "add", [sd])
            self.add_rules("status", sd.get("env"))
        # 重载prometheus
        reload_prometheus_cmd = "curl -X POST http://localhost:19011/-/reload"
        os.system(reload_prometheus_cmd)

    def delete_from_self_exporter(self, service_data):
        """
        从自有的exporter中删除对应的服务信息
        :param service_data:
        :return:
        """
        self_exporter_target_file = os.path.join(
            self.prometheus_targets_path,
            "{}Exporter_all.json".format(service_data["service_name"]))
        if not service_data:
            return False, "service_data can not be null"
        self_target_list = list()
        if os.path.exists(self_exporter_target_file):
            with open(self_exporter_target_file, 'r') as f:
                content = f.read()
                if content:
                    self_target_list = json.loads(content)
        else:
            logger.error("{}不存在！".format(self_exporter_target_file))
            return False, "service_data can not be null"
        try:
            instance = service_data['ip']
            env = service_data['env']
            for service in self_target_list:
                if (instance == service["labels"]["instance"]) and (
                        env == service["labels"]["env"]):
                    self_target_list.remove(service)
        except KeyError as func_e:
            logger.error(func_e)

        with open(self_exporter_target_file, 'w') as f2:
            json.dump(self_target_list, f2, ensure_ascii=False, indent=4)

    def delete_service(self, services_data):
        """
        从自监控删除指定的服务
        :param services_data: 服务数据
        :return:
        """
        if not services_data:
            return False, "services_data can not be null"

        for sd in services_data:
            if not sd:
                continue
            self.delete_from_self_exporter(sd)
            self.update_agent_service(sd.get('ip'), 'delete', [sd])
