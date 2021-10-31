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
import requests

# import requests
from ruamel.yaml import YAML

from omp_server.settings import PROJECT_DIR
from utils.parse_config import MONITOR_PORT

# from utils.parse_config import MONITOR_PORT

logger = logging.getLogger("server")

CW_TOKEN = {
    'CWAccessToken': 'FnQGiEXrYr6n8diKuY6cc61Zw3MMyLW9icwiUlHjyoAkBsBKCDIqmDZbf'}

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

    @staticmethod
    def get_service_port(service_name):
        port = MONITOR_PORT.get(service_name)
        return port

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
                "ip": "127.0.0.1",
                "instance_name": "instance"
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
                    "instance_name": "{}".format(item.get("instance_name")),
                    "service_type": "host",
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

    def update_agent_service(self, dest_ip, action, services_data):
        """
        接收omp传来的参数，解析后发送到monitor_agent
        :param action: 更新动作 add or delete
        :param services_data: 要更新的服务信息
        :param dest_ip:
        :return:
        """
        json_dict = dict()
        json_content = list()
        headers = CW_TOKEN
        dest_url = ''
        if action == 'add':
            dest_url = 'http://{}:{}/update/service/add'.format(dest_ip, self.monitor_port)  # NOQA
            for sd in services_data:
                service_temp_data = dict()
                service_temp_data['service_port'] = sd.get('listen_port')
                if sd.get('service_name') in EXPORTERS:
                    service_temp_data['exporter_port'] = self.get_service_port(
                        '{}Exporter'.format(sd.get('service_name')))
                else:
                    service_temp_data['exporter_port'] = 0
                if sd.get('service_name') in METRICS.keys():
                    service_temp_data['exporter_metric'] = METRICS.get(
                        sd.get('service_name'), 0)
                else:
                    service_temp_data['exporter_metric'] = 'metrics'
                service_temp_data['username'] = sd.get('username', '')
                service_temp_data['password'] = sd.get('password', '')
                service_temp_data['name'] = sd.get('service_name')
                # omp1.3 新增对有进程无端口服务的监控
                service_temp_data['only_process'] = sd.get('only_process')
                service_temp_data['process_key_word'] = sd.get(
                    'process_key_word')
                service_temp_data['instance'] = dest_ip
                service_temp_data['env'] = sd.get('env')
                service_temp_data['log_path'] = sd.get('log_path')
                json_content.append(service_temp_data)
        elif action == 'delete':
            dest_url = 'http://{}:{}/update/service/delete'.format(dest_ip, self.monitor_port)  # NOQA
            for sd in services_data:
                json_content.append(sd.get('service_name'))

        json_dict['services'] = json.dumps(json_content)
        try:
            logger.info(f'向agent发送数据{json_dict}')
            result = requests.post(
                dest_url, headers=headers, data=json_dict).json()
            if result.get('return_code') == 0:
                logger.info('向{}更新服务{}配置成功！'.format(
                    dest_ip, services_data[0].get('service_name')))
            else:
                logger.error('向{}更新服务{}配置失败！'.format(
                    dest_ip, services_data[0].get('service_name')))
                return False, result.get('return_message')
        except requests.exceptions.ConnectionError as e:
            logger.error('向{}更新服务{}配置失败！'.format(
                dest_ip, services_data[0].get('service_name')))
            return False, e
        try:
            from utils.parse_config import MONITOR_PORT, LOCAL_IP
            from db_models.models import Host
            update_agent_promtail_url = f'http://{dest_ip}:{self.monitor_port}/update/promtail/add'  # NOQA
            host_agent_dir = Host.objects.filter(
                ip=dest_ip).values_list('agent_dir')[0]
            json_dict["services"] = json.loads(json_dict["services"])
            json_dict['promtail_config'] = {
                'http_listen_port': MONITOR_PORT.get('promtail'),
                'loki_url': f'http://{LOCAL_IP}:{MONITOR_PORT.get("loki")}/loki/api/v1/push'   # NOQA
            }
            json_dict['agent_dir'] = host_agent_dir
            logger.info(f'向agent发送数据{json_dict}')
            promtail_result = requests.post(
                update_agent_promtail_url, headers=headers, data=json.dumps(json_dict)).json()
            if promtail_result.get('return_code') == 0:
                logger.info('向{}更新服务{}日志监控配置成功！'.format(
                    dest_ip, services_data[0].get('service_name')))
            else:
                logger.error('向{}更新服务{}日志监控配置失败！'.format(
                    dest_ip, services_data[0].get('service_name')))
                return False, promtail_result.get('return_message')
        except Exception as e:
            logger.error(e)
            logger.error('向{}更新服务{}日志监控失败！'.format(
                dest_ip, services_data[0].get('service_name')))
            return False, e

        return True, 'success'

    def add_service(self, service_data):
        """
        service_data = {
            "service_name": "mysql",
            "instance_name": "mysql_dosm",
            "data_path": "/data/appData/mysql",
            "log_path": "/data/logs/mysql",
            "env": "default",
            "ip": "127.0.0.1",
            "listen_port": "3306"
        }
        添加有exporter的组件信息到各自的exporter监控
        :param service_data: 新增的服务信息
        :return:
        """
        if not service_data:
            return False, "args cant be null"

        logger.info(f'收到信息：{service_data}')
        with open(self.prometheus_conf_path, 'r') as fr:
            fr_content = fr.read()
        job_name_str = "'{}Exporter".format(service_data.get('service_name'))
        if job_name_str not in fr_content:  # TODO 采用读写yaml文件的方式
            new_job_chunk = "\n  - job_name: '{}Exporter'\n    metrics_path: /metrics/monitor/{}\n    scheme: http\n    file_sd_configs:\n    - refresh_interval: 30s\n      files:\n      - targets/{}Exporter_all.json".format(
                service_data.get('service_name'), service_data.get(
                    'service_name'),
                service_data.get('service_name'))
            fw_content = fr_content + new_job_chunk
            with open(self.prometheus_conf_path, 'w') as fw:
                fw.write(fw_content)
        self_exporter_target_file = os.path.join(self.prometheus_targets_path,
                                                 "{}Exporter_all.json".format(service_data["service_name"]))
        self_target_list = list()
        self_target_ele = ""
        try:
            self_target_ele = {
                "labels": {
                    "instance": "{}".format(service_data["ip"]),
                    "instance_name": "{}".format(service_data.get("instance_name")),
                    "service_type": "service",
                    "env": "{}".format(service_data["env"])
                },
                "targets": [
                    "{}:{}".format(service_data["ip"], self.monitor_port)
                ]
            }
        except KeyError as func_e:
            logger.error(func_e)
        self_target_list.append(self_target_ele)

        if os.path.exists(self_exporter_target_file):
            with open(self_exporter_target_file, 'r') as f:
                content = f.read()
                if content:
                    old_self_target_list = json.loads(content)
                    self_target_list.extend(old_self_target_list)
        self_target_list = self.json_distinct(self_target_list)

        with open(self_exporter_target_file, 'w') as f2:
            json.dump(self_target_list, f2, ensure_ascii=False, indent=4)

        flag, msg = self.update_agent_service(
            service_data.get('ip'), 'add', [service_data])
        if not flag:
            return False, msg
        self.add_rules('status', service_data.get('env'))
        reload_prometheus_url = 'http://localhost:19011/-/reload'
        # TODO 确认重载prometheus动作在哪执行
        try:
            requests.post(reload_prometheus_url)
        except Exception as e:
            logger.error(e)
            logger.error("重载prometheus配置失败！")
        return True, "success"

    def delete_service(self, service_data):
        """
        从自有的exporter中删除对应的服务信息
        :param service_data:
        :return:
        """
        if not service_data:
            return False, "args cant be null"

        self_exporter_target_file = os.path.join(self.prometheus_targets_path,
                                                 "{}Exporter_all.json".format(service_data["service_name"]))

        self_target_list = list()
        if os.path.exists(self_exporter_target_file):
            with open(self_exporter_target_file, 'r') as f:
                content = f.read()
                if content:
                    self_target_list = json.loads(content)
        else:
            logger.error("{}不存在！".format(self_exporter_target_file))
            return False, "Failed"
        try:
            instance = service_data['ip']
            env = service_data['env']
            for service in self_target_list:
                if (instance == service["labels"]["instance"]) and (env == service["labels"]["env"]):
                    self_target_list.remove(service)
        except KeyError as func_e:
            logger.error(func_e)

        with open(self_exporter_target_file, 'w') as f2:
            json.dump(self_target_list, f2, ensure_ascii=False, indent=4)
        flag, msg = self.update_agent_service(
            service_data.get('ip'), 'delete', [service_data])
        if not flag:
            return False, msg
        reload_prometheus_url = 'http://localhost:19011/-/reload'
        # TODO 确认重载prometheus动作在哪执行
        try:
            requests.post(reload_prometheus_url)
        except Exception as e:
            logger.error(e)
            logger.error("重载prometheus配置失败！")
        return True, "success"
