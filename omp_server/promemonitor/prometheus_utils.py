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
import hashlib

# import requests
import yaml
from ruamel.yaml import YAML

from db_models.models import HostThreshold, ServiceCustomThreshold, AlertRule
from omp_server.settings import PROJECT_DIR
from utils.parse_config import MONITOR_PORT, PROMETHEUS_AUTH, LOKI_CONFIG

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
        self.basic_auth = (PROMETHEUS_AUTH.get(
            "username", "omp"), PROMETHEUS_AUTH.get("plaintext_password", ""))

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
        try:
            from db_models.models import HostThreshold
            warning_obj = HostThreshold.objects.filter(env_id=1, index_type="disk_data_used",
                                                       alert_level="warning").first()
            critical_obj = HostThreshold.objects.filter(env_id=1, index_type="disk_data_used",
                                                        alert_level="critical").first()
            warning_threshold = warning_obj.condition_value if warning_obj else "0"
            critical_threshold = critical_obj.condition_value if critical_obj else "100"
        except Exception as e:
            warning_threshold = "80"
            critical_threshold = "90"
            logger.error(f"更新数据分区告警于是失败！详情为：{e}")
        des = "主机 {{ $labels.instance }} 数据分区使用率为 " \
              "{{ $value | humanize }}%, 大于阈值 "
        return {
            "alert": "主机数据分区磁盘使用率过高",
            "annotations": {
                "disk_data_path": f"{data_path}",
                "consignee": f"{self.email_address}",
                "description": des + f"{critical_threshold}%" if level == "critical" else des + f"{warning_threshold}%",
                "summary": "disk_data_used (instance {{ $labels.instance }})"
            },
            "expr": self.get_expr(
                critical_threshold if level == "critical" else warning_threshold, env, data_path),
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
        # _critical_flag = True
        # _warning_flag = True
        if not os.path.exists(data_rule_path):
            node_data_rule_dic = {
                "groups": [
                    {
                        "name": "主机数据分区磁盘使用率过高",
                        "rules": [
                            _critical, _warning
                        ]
                    }
                ]
            }
            self.write_dic_to_yaml(node_data_rule_dic, data_rule_path)
            return True, "success by new create"
        node_data_rule_dic = self.get_dic_from_yaml(data_rule_path)
        groups = node_data_rule_dic.get("groups", []).copy()
        for item_index, item in enumerate(groups):
            rules = item.get("rules", []).copy()
            for el_index, el in enumerate(rules):
                if el.get("annotations", {}).get("disk_data_path") \
                        == data_path and el.get("labels", {}).get("severity") \
                        == "critical":
                    # _critical_flag = False
                    item.get("rules", [])[el_index] = _critical
                if el.get("annotations", {}).get("disk_data_path") \
                        == data_path and el.get("labels", {}).get(
                    "severity") \
                        == "warning":
                    # _warning_flag = False
                    item.get("rules", [])[el_index] = _warning
            node_data_rule_dic.get("groups", [])[item_index] = item
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
            print("添加数据分区", item["data_path"])
            # 需要像数据库添加数据分区的的规则
            if item["data_path"]:
                self.add_data_disk_rules(item["data_path"], item["env"])
            # # 更新主机node rule
            # self.add_rules("node", item["env"])
            # # 更新exporter的告警规则
            # self.add_rules("exporter", item["env"])
            # # 更新数据分区的告警规则
            # if item["data_path"]:
            #     self.update_node_data_rule(item["data_path"], item["env"])
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
        self.reload_prometheus()
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
                    service_temp_data['exporter_port'] = sd.get(
                        'metric_port', 0)
                if sd.get('service_name') in METRICS.keys():
                    service_temp_data['exporter_metric'] = METRICS.get(
                        sd.get('service_name'), 0)
                else:
                    service_temp_data['exporter_metric'] = 'metrics'
                service_temp_data['username'] = sd.get('username', '')
                service_temp_data['password'] = sd.get('password', '')
                service_temp_data['name'] = sd.get('service_name')
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
                ip=dest_ip).values_list('agent_dir', flat=True)[0]
            json_dict["services"] = json.loads(json_dict["services"])
            json_dict['promtail_config'] = {
                'http_listen_port': MONITOR_PORT.get('promtail'),
                'loki_url': f'http://{LOCAL_IP}:{MONITOR_PORT.get("loki")}/loki/api/v1/push'  # NOQA
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
            "metric_port": "19018"
        }
        添加有exporter的组件信息到各自的exporter监控
        :param service_data: 新增的服务信息
        :return:
        """
        if not service_data:
            return False, "args cant be null"

        logger.info(f'收到信息：{service_data}')
        job_name_str = "{}Exporter".format(service_data.get('service_name'))
        prom_job_dict = {
            "job_name": job_name_str,
            "metrics_path": f"/metrics/monitor/{service_data.get('service_name')}",
            "file_sd_configs": [
                {
                    "refresh_interval": "30s",
                    "files": [
                        f"targets/{service_data.get('service_name')}Exporter_all.json"
                    ]
                }
            ]
        }
        with open(self.prometheus_conf_path, "r") as fr:
            content = yaml.load(fr.read(), yaml.Loader)
        content.get("scrape_configs").append(prom_job_dict)
        with open(self.prometheus_conf_path, "w", encoding="utf8") as fw:
            yaml.dump(data=content, stream=fw,
                      allow_unicode=True, sort_keys=False)
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
        service_data["scrape_log_level"] = LOKI_CONFIG.get("scrape_log_level")
        flag, msg = self.update_agent_service(
            service_data.get('ip'), 'add', [service_data])
        if not flag:
            return False, msg
        # self.add_rules('service', service_data.get('env'))
        reload_prometheus_url = 'http://localhost:19011/-/reload'
        # TODO 确认重载prometheus动作在哪执行
        try:
            requests.post(reload_prometheus_url, auth=self.basic_auth)
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
            requests.post(reload_prometheus_url, auth=self.basic_auth)
        except Exception as e:
            logger.error(e)
            logger.error("重载prometheus配置失败！")
        return True, "success"

    def update_host_threshold(self, env="default", env_id=1):
        rules_file_placeholder_script = [
            {"ENV": env},
            {"EMAIL_ADDRESS": self.email_address}
        ]

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
        from utils.prometheus.update_threshold import config_update
        try:
            # 调用自监控脚本更新环境阈值
            host_thresholds = HostThreshold.objects.filter(
                env_id=env_id).values(
                'index_type', 'condition', 'condition_value', 'alert_level')
            services_objs = ServiceCustomThreshold.objects.filter(
                env_id=env_id
            ).order_by("service_name", "index_type", "condition_value").values(
                "service_name", "index_type", "condition",
                "condition_value", "alert_level")
            services_dict = {}
            for services_obj in services_objs:
                service_name = services_obj.pop("service_name")
                info = services_dict.get(service_name)
                if not info:
                    services_dict[service_name] = [services_obj]
                else:
                    services_dict[service_name].append(services_obj)
            params = {
                'env_name': env,
                'hosts': list(host_thresholds),
                'services': services_dict
            }
            # data_dir = get_path_dir(env_id)
            # if data_dir:
            #     params.update(disk_data_path=data_dir)  # TODO 补充替换数据分区阈值的逻辑
            update_result = config_update(params)
            if not update_result:
                return False, "failed"
            return True, "success"
        except Exception as e:
            import traceback
            logger.error(f"同步监控指标出错:{e}{traceback.format_exc()}")
            return False, "failed"

    def gen_one_rule(self, **kwargs):  # NOQA
        """
        生成单个规则

        """
        expr = kwargs.get("expr")
        compare_str = kwargs.get("compare_str")
        for_time = kwargs.get("for_time")
        alert = kwargs.get("alert")
        summary = kwargs.get("summary")
        description = kwargs.get("description")
        threshold_value = kwargs.get("threshold_value")
        expr_data = f"{expr} {compare_str} {threshold_value}"
        labels = kwargs.get("labels")
        one_rule = {
            "alert": alert,
            "annotations": {
                "description": description,
                "summary": summary,
            },
            "expr": expr_data,
            "for": for_time,
            "labels": labels
        }
        return one_rule

    def get_hash_value(self, expr, severity):  # NOQA
        data = expr + severity
        hash_data = hashlib.md5(data.encode(encoding='UTF-8')).hexdigest()
        return hash_data

    def add_data_disk_rules(self, data_path, env="default"):
        """
        """
        # threshold = "80" if level == "warning" else 90
        logger.error("开始添加数据分区规则")
        threshold_list = [("warning", "80"), ("critical", "90")]
        for i in range(2):
            info = threshold_list[i]
            level = info[0]
            threshold = info[1]
            expr = 'max((node_filesystem_size_bytes{env="ENV",' \
                   'mountpoint="DATA_PATH"}-node_filesystem_free_bytes{env="ENV",' \
                   'mountpoint="DATA_PATH"})*100/(node_filesystem_avail_bytes{' \
                   'env="ENV",mountpoint="DATA_PATH"}+(node_filesystem_size_bytes{' \
                   'env="ENV",mountpoint="DATA_PATH"}-node_filesystem_free_bytes{' \
                   'env="ENV",mountpoint="DATA_PATH"}))) by (instance,env)'.replace(
                       "ENV", env).replace("DATA_PATH", data_path)
            data = {
                "alert": f"主机数据分区{data_path}磁盘使用率",
                "description": '主机 {{ $labels.instance }} 数据分区使用率为 {{ $value | humanize }}%, 大于阈值 $threshold$%'.replace(
                    "$threshold$", threshold),
                "expr": expr,
                "compare_str": ">=",
                "threshold_value": threshold,
                "for_time": "60s",
                "severity": level,
                "labels": {
                    "job": "nodeExporter",
                    "severity": level
                },
                "name": "数据分区使用率",
                "quota_type": 0,
                "status": 1,
                "service": "node",
                "forbidden": 2,

            }
            hash_data = self.get_hash_value(expr=expr, severity=level)
            if AlertRule.objects.filter(expr=expr, severity=level, hash_data=hash_data).exists():
                continue
            try:
                data.update(hash_data=hash_data)
                AlertRule(**data).save()
            except Exception as e:
                logger.error(f"更新数据分区错误:{e}")
        self.update_rule_file(env=env)
        return True

    def update_rule_file(self, add_data=None, add=False, update=False, delete=False, env="default", rule_id=0,
                         env_id=1):
        """
        更新规则文件
        """
        rule_file_path = os.path.join(
            self.prometheus_rules_path, f"{env}_rule.yml")
        try:
            all_rules = AlertRule.objects.filter(status=1).all()
            if delete or update:
                all_rules = AlertRule.objects.filter(
                    status=1).exclude(id=rule_id).all()
            init_data = {"groups": [
                {
                    "name": "OMP Alert",
                    "rules": []
                }
            ]}
            for rule in all_rules:
                content = {
                    "alert": rule.alert,
                    "annotations": {
                        "description": rule.description,
                        "summary": rule.summary,
                    },
                    "expr": f"{rule.expr} {rule.compare_str} {rule.threshold_value}",
                    "for": rule.for_time,
                    "labels": rule.labels,
                }
                init_data["groups"][0]["rules"].append(content)
            if add or update:
                init_data["groups"][0]["rules"].append(
                    self.gen_one_rule(**add_data)
                )
            my_yaml = YAML()
            with open(rule_file_path, "w", encoding="utf8") as fp:
                my_yaml.dump(init_data, fp)

            return True
        except Exception as e:
            logger.error(f"生成规则文件{rule_file_path}失败{e}")
            return False

    def reload_prometheus(self):
        """
        重载prometheus
        """
        reload_prometheus_url = 'http://localhost:19011/-/reload'
        # TODO 确认重载prometheus动作在哪执行
        try:
            response = requests.post(
                reload_prometheus_url, auth=self.basic_auth)
            logger.error(f"重载成功 {response.text}")
            return True
        except Exception as e:
            logger.error(e)
            logger.error("重载prometheus配置失败！")
            return False
