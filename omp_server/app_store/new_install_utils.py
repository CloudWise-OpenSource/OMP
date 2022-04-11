# -*- coding: utf-8 -*-
# Project: new_install_utils
# Author: jon.liu@yunzhihui.com
# Create time: 2021-11-12 14:01
# IDE: PyCharm
# Version: 1.0
# Introduction:

import os
import json
import pickle
import logging
import traceback
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor

import redis
from ruamel import yaml
from django.db import transaction
from django.db.models import F
from rest_framework.exceptions import ValidationError

from omp_server.settings import PROJECT_DIR
from db_models.models import (
    ProductHub, ApplicationHub, ClusterInfo, Service, Host,
    Env, ServiceConnectInfo, Product, MainInstallHistory,
    DetailInstallHistory, PreInstallHistory, PostInstallHistory
)
from app_store.tasks import install_service as install_service_task
from app_store.deploy_mode_utils import SERVICE_MAP
from utils.common.exceptions import GeneralError
from utils.plugin.salt_client import SaltClient
from utils.parse_config import (
    BASIC_ORDER,
    OMP_REDIS_HOST,
    OMP_REDIS_PORT,
    OMP_REDIS_PASSWORD
)
from app_store.deploy_role_utils import DEPLOY_ROLE_UTILS

logger = logging.getLogger("server")

DIR_KEY = "{data_path}"
UNIQUE_KEY_ERROR = "后台无法追踪此流程或安装流程已开始,请查看安装记录或重新进入部署流程!"
WEB_CONTAINERS = ["tengine"]


class RedisDB(object):
    """
    redis数据库管理工具
    """

    def __init__(self):
        """
        获取redis连接对象
        """
        self.conn = redis.Redis(
            host=OMP_REDIS_HOST,
            port=OMP_REDIS_PORT,
            db=15,
            password=OMP_REDIS_PASSWORD
        )

    def delete_keys(self, keyword):
        """
        删除以某个关键字开头的key
        :param keyword: 关键字
        :return:
        """
        for key in self.conn.scan_iter(f"{keyword}*"):
            self.conn.delete(key)

    def set(self, name, data, timeout=60 * 60 * 8):
        """
        设置redis键值对
        :param name: redis键名称
        :param data: redis中要存储的值
        :param timeout: 超时时间
        :return:
        """
        self.conn.set(name, pickle.dumps(data), ex=timeout)
        logger.info(f"Insert data to redis:\nname:{name}\ndata:{data}")

    def get(self, name):
        """
        获取存储在redis中的值
        :param name: redis键名称
        :return:
        """
        try:
            logger.info(f"Try get data from redis by name: {name}")
            _obj = self.conn.get(name=name)
            if not _obj:
                logger.error(
                    f"Failed get data from redis by name: {name}, res is None")
                return False, None
            data = pickle.loads(_obj)
            logger.info(f"Get data from redis by name: {name}, res is {data}")
            return True, data
        except Exception as e:
            logger.error(
                f"Error while get {name} from redis: {str(e)}\n"
                f"{traceback.format_exc()}")
            return False, None


class BaseRedisData(object):
    """ redis中存储信息配置类 """

    def __init__(self, unique_key):
        self.unique_key = unique_key
        self.redis = RedisDB()

    def delete_all_keys(self):
        """
        删除unique_key相关数据
        :return:
        """
        self.redis.delete_keys(keyword=self.unique_key)

    def _get(self, key):
        """
        根据redis的key获取值
        :param key: redis的key
        :type key: str
        :return:
        """
        _flag, _data = self.redis.get(name=key)
        if not _flag:
            raise ValidationError(UNIQUE_KEY_ERROR)
        return _data

    def step_set_with_ser(self, data):
        """
        设置with服务范围，临时存储，在最终部署的时候添加回来
        [
            {"name": "xx", "version": "xxx", "with": "xxx"}
        ]
        :param data:
        :return:
        """
        self.redis.set(
            name=self.unique_key + "_with_ser",
            data=data
        )

    def get_with_ser(self):
        """
        获取 with ser服务的列表
        :return:
        """
        key = self.unique_key + "_with_ser"
        return self._get(key=key)

    def step_1_set_unique_key(self, data):
        """
        第一步 存储安装流程标志位到redis中
        data数据格式为
        {
            'data': [{'name': 'douc', 'version': ['5.3.0']}],
            'unique_key': '60649454-0149-44e8-a813-7309ffbd96ca'
        }
        :param data: 安装入口数据
        :type data: dict
        :return:
        """
        self.redis.set(name=self.unique_key, data=data)

    def get_unique_key(self):
        """
        获取安装流程标记
        :return:
        """
        _flag, _ = self.redis.get(name=self.unique_key)
        if not _flag:
            raise ValidationError(UNIQUE_KEY_ERROR)
        return self.unique_key

    def step_2_set_origin_install_data_args(self, data):  # NOQA
        """
        存储要安装的数据到redis，存储的是将要安装的服务的名称，版本以及所属产品
        入参data如下：
        {
            "unique_key": "60649454-0149-44e8-a813-7309ffbd96ca",
            "high_availability": false,
            "install_product": [
                {
                    "name": "douc",
                    "version": "5.3.0"
                }
            ],
            "data": {
                "basic": [
                    {
                        "name": "douc",
                        "version": "5.3.0",
                        "services_list": [
                            {
                                "name": "doucApi",
                                "version": "2.3.0",
                                "deploy_mode": {
                                    "default": 1,
                                    "step": 0
                                }
                            },
                            {
                                "name": "doucWeb",
                                "version": "2.3.0",
                                "deploy_mode": {
                                    "default": 1,
                                    "step": 0
                                }
                            }
                        ],
                        "error_msg": ""
                    }
                ],
                "dependence": [
                    {
                        "name": "kafka",
                        "version": "2.2.2",
                        "exist_instance": [],
                        "is_use_exist": false,
                        "is_base_env": false,
                        "deploy_mode": {
                            "default": 1,
                            "step": 1
                        }
                    },
                    {
                        "name": "jdk",
                        "version": "1.8.0",
                        "exist_instance": [],
                        "is_use_exist": true,
                        "is_base_env": false,
                        "deploy_mode": {
                            "default": 1,
                            "step": 1
                        }
                    },
                    {
                        "name": "mysql",
                        "version": "5.7.34",
                        "exist_instance": [],
                        "is_use_exist": false,
                        "is_base_env": false,
                        "deploy_mode": [
                            {
                                "key": "master-slave",
                                "name": "主从"
                            },
                            {
                                "key": "master-master",
                                "name": "主主(vip)"
                            }
                        ]
                    }
                ],
                "is_continue": true
            }
        }
        存储到redis中的数据如下：
        {
            "install": {
                "doucApi": {
                    "version": "2.3.0",
                    "product": "douc"
                },
                "kafka": {
                    "version": "2.2.2",
                    "product": null
                }
            },
            "use_exist": {}
        }

        :param data: 根据要安装的产品生成的安装参数
        :type data: dict
        :return:
        """
        basic = data.get("data", {}).get("basic")
        dependence = data.get("data", {}).get("dependence")
        _data = {
            "install": dict(),
            "use_exist": dict()
        }
        for item in basic:
            for el in item.get("services_list"):
                _data["install"][el["name"]] = {
                    "version": el["version"],
                    "product": item["name"]
                }
        for item in dependence:
            if item.get("is_use_exist"):
                _data["use_exist"][item["name"]] = item.get(
                    "exist_instance", [])
                continue
            # TODO 优化版本间若依赖选择
            _data["install"][item["name"]] = {
                # "version": item["version"],
                "version": ApplicationHub.objects.filter(
                    app_name=item["name"],
                    app_version__startswith=item["version"]
                ).last().app_version,
                "product": None
            }
        self.redis.set(
            name=self.unique_key + "_step_2_origin_data",
            data=_data
        )
        return _data

    def get_step_2_origin_data(self):
        """
        获取安装原始数据
        :return:
        """
        key = self.unique_key + "_step_2_origin_data"
        return self._get(key=key)

    def step_3_set_checked_data(self, data):
        """
        存储已被校验过的安装数据
        {
            "unique_key": "60649454-0149-44e8-a813-7309ffbd96ca",
            "data": {
                "basic": [
                    {
                        "name": "douc",
                        "version": "5.3.0",
                        "services_list": [
                            {
                                "name": "doucApi",
                                "version": "2.3.0",
                                "deploy_mode": 1
                            }
                        ],
                        "cluster_name": "douc-cluster-1"
                    }
                ],
                "dependence": [
                    {
                        "name": "kafka",
                        "version": "2.2.2",
                        "exist_instance": [],
                        "deploy_mode": 1,
                        "is_use_exist": false,
                        "is_base_env": false,
                        "cluster_name": "kafka-cluster-1"
                    }
                ],
                "is_continue": true
            }
        }
        :param data: 存储点击下一步校验的数据
        :type data: dict
        :return:
        """
        # 覆盖第一步选择的安装数据
        self.step_2_set_origin_install_data_args(data=data)
        self.redis.set(
            name=self.unique_key + "_step_3_checked_data",
            data=data
        )
        cluster_name_map = dict()
        service_vip_map = dict()
        basic = data.get("data", {}).get("basic", [])
        for item in basic:
            cluster_name_map[item["name"]] = \
                item.get("cluster_name")
            # 存储服务对应产品的集群名称
            # for el in item.get("services_list"):
            #     cluster_name_map[el["name"]] = item.get("cluster_name")
        dependence = data.get("data", {}).get("dependence", [])
        for item in dependence:
            if item.get("is_use_exist"):
                continue
            if item.get("vip"):
                service_vip_map[item.get("name")] = item.get("vip")
            cluster_name_map[item["name"]] = \
                item.get("cluster_name")
        self.redis.set(
            name=self.unique_key + "_step_3_cluster_name_map",
            data=cluster_name_map
        )
        self.redis.set(
            name=self.unique_key + "_step3_service_vip_map",
            data=service_vip_map
        )

    def get_step_3_checked_data(self):
        """
        获取校验过的安装数据值
        :return:
        """
        key = self.unique_key + "_step_3_checked_data"
        return self._get(key=key)

    def get_step_3_cluster_name_map(self):
        """
        获取将要安装的产品的实例名称及组件的集群名称映射关系
        :return:
        """
        key = self.unique_key + "_step_3_cluster_name_map"
        return self._get(key=key)

    def get_step3_service_vip_map(self):
        """
        获取要是用的 vip 名
        :return:
        """
        key = self.unique_key + "_step3_service_vip_map"
        return self._get(key=key)

    def step_4_set_service_distribution(self, data):
        """
        存储生成的服务部署数量以及服务间的绑定关系，用于前端选择服务分布
        {
            "doucApi": {
                "num": 1,
                "with": null
            },
            "doucWeb": {
                "num": 1,
                "with": "portalWeb"
            },
            "mysql": {
                "num": 1,
                "with": null
            },
            "tengine": {
                "num": 1,
                "with": null
            }
        }
        :param data: 要安装的服务及数量以及服务间with绑定关系
        :type data: dict
        :return:
        """
        self.redis.set(
            name=self.unique_key + "_step_4_service_distribution",
            data=data
        )

    def get_step_4_service_distribution(self):
        """
        获取要部署的服务的数量以及服务绑定关系
        :return:
        """
        key = self.unique_key + "_step_4_service_distribution"
        return self._get(key=key)

    def step_5_set_host_and_service_map(self, host_list, host_service_map):
        """
        存储本次安装所需要的主机列表及主机与服务的分布关系字典
        host_list:
        [
            "10.0.14.234",
            "10.0.14.231"
        ]
        host_service_map:
        {
            "10.0.14.234": [
                "doucApi",
                "doucSso",
            ],
            "10.0.14.231": [
                "portalServer",
                "kafka"
            ]
        }

        :param host_list: 本次安装涉及到的主机列表
        :type host_list: list
        :param host_service_map: 本次安装主机与服务的映射关系
        :type host_service_map: dict
        :return:
        """
        self.redis.set(
            name=self.unique_key + "_step_5_host_list",
            data=host_list
        )
        self.redis.set(
            name=self.unique_key + "_step_5_host_service_map",
            data=host_service_map
        )

    def get_step_5_host_list(self):
        """
        获取本次服务部署涉及到的主机列表
        :return:
        """
        key = self.unique_key + "_step_5_host_list"
        return self._get(key=key)

    def get_step_5_host_service_map(self):
        """
        获取本次服务部署涉及到主机与服务的映射关系
        :return:
        """
        key = self.unique_key + "_step_5_host_service_map"
        return self._get(key=key)

    def step_6_set_final_data(self, data):
        """
        设置最终要安装的服务列表
        :param data:
        :return:
        """
        self.redis.set(
            name=self.unique_key + "_step_6_set_final_data",
            data=data
        )

    def get_step_6_set_final_data(self):
        """
        获取最终要安装的服务列表
        :return:
        """
        key = self.unique_key + "_step_6_set_final_data"
        return self._get(key=key)

    def set_host_user_map(self):
        """
        设置主机与用户之间的关系
        :return:
        """
        host_user_lst = Host.objects.all().values("ip", "username")
        host_user_dic = dict()
        for item in host_user_lst:
            host_user_dic[item["ip"]] = item["username"]
        self.redis.set(self.unique_key + "_host_user_map", data=host_user_dic)

    def get_host_user_map(self):
        """
        获取主机与用户映射关系
        :return:
        """
        return self._get(self.unique_key + "_host_user_map")


def check_package_exists(app_obj):
    """
    检查安装包是否存在
    :param app_obj: 服务对象
    :type app_obj: ApplicationHub
    :return:
    """
    try:
        path = os.path.join(
            PROJECT_DIR,
            "package_hub",
            app_obj.app_package.package_path,
            app_obj.app_package.package_name
        )
        if not os.path.exists(path):
            return False, path
        return True, path
    except Exception as e:
        logger.error(
            f"check_package_exists: Exception: {str(e)}; "
            f"{traceback.format_exc()}")
        return False, f"程序错误: {str(e)}"


class ProductServiceParse(object):
    """ 解析要安装的应用服务的基础信息 """

    def __init__(
            self, pro_name, pro_version,
            high_availability=False, unique_key=None
    ):
        """
        产品、应用解析服务信息
        :param pro_name: 产品、应用名称
        :param pro_version: 产品、应用版本
        :param high_availability: 是否使用高可用
        """
        self.pro_name = pro_name
        self.pro_version = pro_version
        self.high_availability = high_availability
        self.unique_key = unique_key

    def get_default_and_step(self, app_obj):
        """
        获取服务默认数量及步长
        :param app_obj: 服务对象
        :type app_obj ApplicationHub
        :return:
        """
        if not self.high_availability:
            return 1, 1
        # 如果服务是和tengine进行强绑定的，那么需要限制其数量为1
        # TODO 当前tengine不支持高可用模式
        if "affinity" in app_obj.extend_fields and \
                app_obj.extend_fields.get("affinity") == "tengine":
            return 1, 0
        return 1, 1

    def parse_single_service(self, service_dic):
        """
        解析单个服务的数据
        :param service_dic: 服务名称、字典
        :type service_dic: dict
        :return:
        """
        _name = service_dic.get("name")
        _version = service_dic.get("version")
        app_obj = ApplicationHub.objects.filter(
            app_type=ApplicationHub.APP_TYPE_SERVICE,
            app_name=_name,
            app_version=_version
        ).last()
        # 解决服务强绑定依赖问题
        if "affinity" in app_obj.extend_fields and \
                app_obj.extend_fields["affinity"] in WEB_CONTAINERS:
            return {
                "name": _name,
                "version": _version,
                "with": app_obj.extend_fields["affinity"],
                "with_flag": True,
                "deploy_mode": {
                    "default": 1,
                    "step": 0
                }
            }
        _default_dic = {
            "name": _name,
            "version": _version,
            "deploy_mode": {
                "default": 1,
                "step": 0
            },
            "error_msg": ""
        }
        # 如果产品下的服务不存在应该返回错误信息
        if not app_obj:
            _default_dic["error_msg"] = \
                f"应用商店内无此服务 [{_name}({_version})]"
            return _default_dic
        # 如果产品下的服务的安装包对象不存在应该返回错误信息
        if not app_obj.app_package:
            _default_dic["error_msg"] = \
                f"此服务 [{_name}({_version})] 无法找到安装包"
            return _default_dic
        # 如果安装包实际不存在应该返回错误消息
        _flag, _msg = check_package_exists(app_obj=app_obj)
        if not _flag:
            _default_dic["error_msg"] = \
                f"{_name}安装包不存在，请查看 {_msg}"
            return _default_dic
        # 如果是非高可用模式，直接返回服务数据
        # 如果是高可用模式，那么前端服务步长为0，后端服务步长为1
        default, step = self.get_default_and_step(app_obj=app_obj)
        return {
            "name": _name,
            "version": _version,
            "deploy_mode": {
                "default": default,
                "step": step
            }
        }

    def get_services_list(self):
        """
        获取产品下的服务信息列表以及其默认数量及步长
        :return:
        """
        pro_obj = ProductHub.objects.filter(
            pro_name=self.pro_name,
            pro_version=self.pro_version
        ).last()
        pro_services = json.loads(pro_obj.pro_services)
        return [self.parse_single_service(el) for el in pro_services]

    def run(self):
        """
        解析入口
        :return:
        """
        error_msg_lst = list()
        services_list = self.get_services_list()
        for item in services_list:
            if "error_msg" in item and item["error_msg"]:
                error_msg_lst.append(item["error_msg"])
                item.pop("error_msg")
        _dic = {
            "name": self.pro_name,
            "version": self.pro_version,
            "services_list": services_list,
            "error_msg": "\n".join(error_msg_lst)
        }
        return _dic


class ComponentServiceParse(object):
    """组件服务安祖昂解析"""

    def __init__(
            self, ser_name, ser_version,
            high_availability=False, unique_key=None
    ):
        """
        产品、应用解析服务信息
        :param ser_name: 组件名称
        :param ser_version: 组件版本
        :param high_availability: 是否使用高可用
        """
        self.ser_name = ser_name
        self.ser_version = ser_version
        self.high_availability = high_availability
        self.unique_key = unique_key

    def get_deploy_mode(self, app_obj):
        """
        获取服务默认数量及步长
        :param app_obj: 服务对象
        :type app_obj ApplicationHub
        :return:
        """
        pass

    def parse_single_service(self):
        """
        解析单个服务的数据
        :return:
        """
        app_obj = ApplicationHub.objects.filter(
            # app_type=ApplicationHub.APP_TYPE_COMPONENT,
            app_name=self.ser_name,
            app_version=self.ser_version
        ).last()
        # 解决服务强绑定依赖问题
        _default_dic = {
            "name": self.ser_name,
            "version": self.ser_version,
            "deploy_mode": self.get_deploy_mode(app_obj=app_obj),
        }
        # 如果产品下的服务不存在应该返回错误信息
        if not app_obj:
            _default_dic["error_msg"] = \
                f"应用商店内无此服务 [{self.ser_name}({self.ser_version})]"
            return _default_dic
        _, is_pack_exist, msg = SerDependenceParseUtils(
            parse_name=self.ser_name, parse_version=self.ser_version,
            high_availability=self.high_availability
        ).get_ser_instances(obj=app_obj)
        if not is_pack_exist:
            _default_dic["error_msg"] = \
                f"{self.ser_name}安装包不存在，请查看 {msg}"
        _default_dic["is_pack_exist"] = is_pack_exist
        _default_dic["is_use_exist"] = False
        _default_dic["exist_instance"] = list()
        _default_dic["is_base_env"] = SerDependenceParseUtils(
            parse_name=self.ser_name, parse_version=self.ser_version,
            high_availability=self.high_availability
        ).get_is_base_env(obj=app_obj)
        _default_dic["deploy_mode"] = SerDeployModeUtils(
            ser_name=self.ser_name,
            high_availability=self.high_availability
        ).get()
        return _default_dic

    def run(self):
        """
        解析入口
        :return:
        """
        return self.parse_single_service()


def make_lst_unique(lst, key_1, key_2):
    """
    去重列表内的字典
        lst = [{"name": "1", "version": "1"}, {"name": "1", "version": "1"}]
        lst = make_lst_unique(lst, "name", "version")
    :param lst: 被操作对象
    :param key_1: 关键key1
    :param key_2: 关键key2
    :return:
    """
    unique_dic = dict()
    ret_lst = list()
    for el in lst:
        _unique = el.get(key_1, "") + "_" + el.get(key_2, "")
        if _unique in unique_dic:
            continue
        # 服务版本模糊判断逻辑 jon.liu 20211225
        _app = ApplicationHub.objects.filter(
            app_name=el.get(key_1),
            app_version__startswith=el.get(key_2)
        ).last()
        if not _app or el.get(key_1) + "_" + el.get(key_2) not in unique_dic:
            unique_dic[el.get(key_1) + "_" + el.get(key_2)] = True
            ret_lst.append(el)
            continue
        _unique = _app.app_name + "_" + _app.app_version
        if _unique in unique_dic:
            continue
        # 更新弱校验的服务版本
        el["version"] = _app.app_version
        ret_lst.append(el)
        unique_dic[_unique] = True
    return ret_lst


class SerDependenceParseUtils(object):
    """
    依赖解决工具类
    """

    def __init__(self, parse_name, parse_version, high_availability=False):
        """
        初始化对象, 服务级别的解析，包含自研服务和基础组件服务
        :param parse_name: 要解析的名称，服务
        :type parse_name: str
        :param parse_version: 要解析的版本
        :type parse_version: str
        :param high_availability: 是否使用高可用模式
        :type high_availability: bool
        """
        self.high_availability = high_availability
        self.parse_name = parse_name
        self.parse_version = parse_version
        self.unique_key = self.parse_name + self.parse_version
        self.host_num = Host.objects.all().count()

    def get_newest_ser(self):
        """
        获取最新的服务对象，同服务，同版本
        :return: ApplicationHub
        """
        return ApplicationHub.objects.filter(
            app_name=self.parse_name,
            app_version=self.parse_version,
            is_release=True
        ).last()

    def get_ser_instances(self, obj):  # NOQA
        """
        查看服务是否已经被安装以及应用商店内是否具备安装条件
        返回值含义：
            cluster_info：当前服务的集群信息
            instance_info：当前服务的实例对象信息
            is_pack_exist：当前服务的安装包是否存在
        :param obj: ApplicationHub实例
        :type obj: ApplicationHub
        :return: cluster_info, instance_info, is_pack_exist
        """
        is_pack_exist, msg = check_package_exists(app_obj=obj)
        if self.get_is_base_env(obj=obj):
            return list(), is_pack_exist, msg
        exist_instance = list()
        # 判断当前服务的集群
        cluster_info = list(ClusterInfo.objects.filter(
            cluster_service_name=obj.app_name
        ).values("id", "cluster_name"))
        exist_instance.extend(
            [
                {
                    "id": el.get("id"),
                    "name": el.get("cluster_name"),
                    "type": "cluster"
                } for el in cluster_info
            ]
        )
        # 判断当前服务的实例信息
        instance_info = list(Service.split_objects.filter(
            service__app_name=obj.app_name,
            service__app_version=obj.app_version,
            cluster__isnull=True
        ).values("service_instance_name", "id"))
        exist_instance.extend(
            [
                {
                    "id": el.get("id"),
                    "name": el.get("service_instance_name"),
                    "type": "single"
                } for el in instance_info
            ]
        )
        return exist_instance, is_pack_exist, msg

    def get_is_base_env(self, obj):  # NOQA
        """
        确定当前服务是否为基础环境：如 jdk 等
        :param obj: 服务对象
        :type obj: ApplicationHub
        :return:
        """
        if obj.is_base_env:
            return True
        if not obj.extend_fields:
            return False
        is_base_env = obj.extend_fields.get("base_env", False)
        if is_base_env:
            if isinstance(is_base_env, bool):
                return is_base_env
            if isinstance(is_base_env, str) and \
                    is_base_env.upper().strip() == "TRUE":
                return True
        return False

    def get_dependence(self, lst, dep):
        """
        解决服务依赖关系核心方法
        :param lst: 存储结果的列表
        :param dep: 服务依赖关系列表
        :return: list()
        """
        unique_key_lst = list()
        for inner in dep:
            _name, _version = inner.get("name"), inner.get("version")
            # 服务版本弱依赖逻辑 jon.liu 20211225
            _app = ApplicationHub.objects.filter(
                app_name=_name,
                app_version__startswith=_version,
                is_release=True
            ).order_by("created").last()
            if _app:
                inner["version"] = _app.app_version
                _version = _app.app_version
            # 定义服务&版本唯一标准，防止递归错误
            unique_key = str(_name) + str(_version)
            # 如果当前服务和需要被解析的源服务重叠，那么则跳过
            # 如果当前服务的依赖关系已经被解决，那么则跳过
            if unique_key == self.unique_key or unique_key in unique_key_lst:
                continue
            unique_key_lst.append(unique_key)
            # 判断当前被依赖服务是否存在，如果不存在就直接返回，不再处理深层依赖
            if not _app:
                inner["exist_instance"] = list()
                inner["deploy_mode"] = list()
                inner["error_msg"] = f"应用商店内无此服务 [{_name}({_version})]"
                inner["is_base_env"] = False
                lst.append(inner)
                continue
            # 查看当前服务是否被安装
            exist_instance, is_pack_exist, msg = \
                self.get_ser_instances(obj=_app)
            # 获取依赖服务的相关信息
            inner["exist_instance"] = exist_instance
            if inner["exist_instance"]:
                inner["is_use_exist"] = True
            else:
                inner["is_use_exist"] = False
            if not is_pack_exist:
                inner["error_msg"] = f"{_name}安装包不存在，请查看 {msg}"
            inner["is_base_env"] = self.get_is_base_env(obj=_app)
            # TODO 获取当前服务的部署模式
            inner["deploy_mode"] = SerDeployModeUtils(
                ser_name=_name,
                high_availability=self.high_availability,
                host_num=self.host_num
            ).get()
            lst.append(inner)
            if not _app.app_dependence:
                continue
            _app_dependence = json.loads(_app.app_dependence)
            self.get_dependence(
                lst, dep=_app_dependence
            )

    def run_ser(self):
        """
        解析服务的依赖关系入口
        :return: 服务依赖关系列表
        """
        _ser = self.get_newest_ser()
        if not _ser or not _ser.app_dependence:
            return list()
        app_dep_lst = json.loads(_ser.app_dependence)
        ret_lst = list()
        self.get_dependence(lst=ret_lst, dep=app_dep_lst)
        ret_lst = make_lst_unique(ret_lst, "name", "version")
        return ret_lst


class SerDeployModeUtils(object):
    """ 针对开源组件服务部署模式的获取及校验工具 """

    def __init__(self, ser_name, high_availability=False, host_num=0):
        self.ser_name = ser_name
        self.high_availability = high_availability
        self.host_num = Host.objects.all().count()

    def get(self):
        """
        获取服务的部署模式
        :return:
        """
        if self.ser_name in SERVICE_MAP:
            return SERVICE_MAP[self.ser_name](
                host_num=self.host_num,
                high_availability=self.high_availability
            ).get()
        # 如果服务不在SERVICE_MAP中，说明omp本身还未支持该服务，给出默认值
        return {
            "default": 1,
            "step": 1
        }


class SerRoleUtils(object):
    """ 针对开源组件角色分配类 """

    @staticmethod
    def get(install_services):
        """
        获取服务的部署模式
        :return:
        """
        tmp_dict = {}
        cp_service = deepcopy(install_services)
        for item in cp_service:
            if item['name'] in DEPLOY_ROLE_UTILS.keys():
                tmp_dict[item['name']] = tmp_dict.get(
                    item['name'], []) + [item]
                if item["name"] != "mysql":
                    install_services.remove(item)
        for name, obj in tmp_dict.items():
            # 发现有需要分role的实例
            if name == "mysql":
                install_services = DEPLOY_ROLE_UTILS[name]().update_service(
                    install_services
                )
            else:
                install_services.extend(
                    DEPLOY_ROLE_UTILS[name]().update_service(obj))
        return install_services


class SerVipUtils(object):
    """ 针对开源组件进行vip绑定处理 """

    def __init__(
            self,
            install_services, service_vip_map, host_user_map, run_user):
        self.install_services = install_services
        self.service_vip_map = service_vip_map
        self.host_user_map = host_user_map
        self.run_user = run_user

    def get_keep_alive(self, ip, data_folder, name):
        _tmp_ser = dict()
        _app = ApplicationHub.objects.filter(
            app_name="keepalived",
        ).last()
        install_args = ServiceArgsPortUtils(
            ip=ip,
            data_folder=data_folder,
            run_user=self.run_user,
            host_user_map=self.host_user_map
        ).remake_install_args(obj=_app)
        ports = ServiceArgsPortUtils(
            ip=ip,
            data_folder=data_folder,
            run_user=self.run_user,
            host_user_map=self.host_user_map
        ).get_app_port(obj=_app)
        _tmp_ser["name"] = _app.app_name
        _tmp_ser["version"] = _app.app_version
        instance_name = \
            "keepalived" + "-" + "-".join(ip.split(".")[-2:])
        _tmp_ser["ip"] = ip
        _tmp_ser["data_folder"] = data_folder
        _tmp_ser["run_user"] = self.run_user
        _tmp_ser["install_args"] = install_args
        _tmp_ser["ports"] = ports
        _tmp_ser["instance_name"] = instance_name
        _tmp_ser["cluster_name"] = None
        _tmp_ser["roles"] = name
        return _tmp_ser

    def run(self):
        """
        处理服务的 vip 模式
        :return:
        """
        keep_alive_lst = list()
        for item in self.install_services:
            if item.get("name") in self.service_vip_map:
                _ser = self.get_keep_alive(
                    ip=item.get("ip"),
                    data_folder=item.get("data_folder"),
                    name=item.get("name")
                )
                _ser["vip"] = self.service_vip_map[item["name"]]
                keep_alive_lst.append(_ser)
        return keep_alive_lst


class SerWithUtils(object):
    """ 服务强绑定关系解析类 """

    def __init__(self, ser_name, ser_version):
        """

        :param ser_name: 服务名称
        :type ser_name: str
        """
        self.ser_name = ser_name
        self.ser_version = ser_version

    def run(self):
        """
        获取服务绑定关系
        :return:
        """
        app_obj = ApplicationHub.objects.filter(
            app_name=self.ser_name,
            app_version=self.ser_version
        ).last()
        if not app_obj or not app_obj.extend_fields:
            return None
        if "affinity" in app_obj.extend_fields and \
                app_obj.extend_fields["affinity"]:
            return app_obj.extend_fields["affinity"]
        return None


class ServiceArgsPortUtils(object):
    """ 服务安装过程中参数解析类 """

    def __init__(self, ip=None, data_folder=None,
                 run_user=None, host_user_map=None):
        self.ip = ip
        self.data_folder = data_folder
        self.run_user = run_user
        self.host_user_map = host_user_map

    @staticmethod
    def get_product_config():
        """
        获取产品配置信息，读取 config/product.yaml 配置文件
        :return:
        """
        config_path = os.path.join(PROJECT_DIR, "config/product.yaml")
        if not os.path.exists(config_path):
            return dict(), dict()
        with open(config_path, "r") as fp:
            product_config = yaml.load(fp, Loader=yaml.SafeLoader)
        return product_config.get("install", dict()), \
               product_config.get("ports", dict())

    @staticmethod
    def inner_replace_args(target_lst, config_lst):
        """
        更新配置参数方法
        :param target_lst: 源配置列表
        :param config_lst: 需要更新的配置列表
        :return:
        """
        try:
            config_dic = {el["key"]: el for el in config_lst}
            new_lst = list()
            for item in target_lst:
                if item.get("key") in config_dic:
                    new_lst.append(config_dic[item.get("key")])
                else:
                    new_lst.append(item)
            return new_lst
        except Exception as e:
            raise GeneralError(
                f"更新安装参数错误, "
                f"请检查 {os.path.join(PROJECT_DIR, 'config/product.yaml')} "
                f"数据格式是否符合规则, 错误信息: {str(e)}"
            )

    def make_product_config_overwrite(self, app_name, rep_type, lst):
        """
        覆盖原有数据库中的yaml，利用 config/product.yaml 中的配置文件覆盖相关参数
        :param app_name: 服务名称
        :param rep_type: 替换类型, app_install_args | app_ports
        :param lst: 替换参数列表
        :return:
        """
        app_install_args_dic, app_ports_dic = self.get_product_config()
        if rep_type == "app_install_args" and app_name in app_install_args_dic:
            return self.inner_replace_args(
                target_lst=lst, config_lst=app_install_args_dic[app_name]
            )
        elif rep_type == "app_ports" and app_name in app_ports_dic:
            return self.inner_replace_args(
                target_lst=lst, config_lst=app_ports_dic[app_name]
            )
        return lst

    @staticmethod
    def make_editable(element):
        """
        处理参数是否可编辑
        :param element: 参数字典
        :return:
        """
        if element.get("editable") is False or \
                str(element.get("editable")).lower() == "false":
            element["editable"] = False
        else:
            element["editable"] = True

    def get_app_dependence(self, obj):  # NOQA
        """
        解析服务级别的依赖关系
        :param obj: 服务对象
        :type obj: ApplicationHub
        :return:
        """
        ser = SerDependenceParseUtils(obj.app_name, obj.app_version)
        return ser.run_ser()

    def get_app_port(self, obj):  # NOQA
        """
        获取app的端口
        :param obj: 服务对象
        :type obj: ApplicationHub
        :return: list()
        """
        if not obj.app_port:
            return []
        origin_ports = json.loads(obj.app_port)
        final_ports = self.make_product_config_overwrite(
            app_name=obj.app_name,
            rep_type="app_ports",
            lst=origin_ports
        )
        for item in final_ports:
            self.make_editable(item)
        return final_ports

    def format_app_install_args(self, app_install_args):  # NOQA
        """
        构建安装参数
        :param app_install_args: 服务安装参数
        :type app_install_args: list
        :return:
        """
        for el in app_install_args:
            if isinstance(el.get("default"), str) and \
                    DIR_KEY in el.get("default"):
                el["default"] = el["default"].replace(DIR_KEY, "")
                el["dir_key"] = DIR_KEY
        return app_install_args

    def get_app_install_args(self, obj):  # NOQA
        """
        解析安装参数信息
        :param obj: 服务对象
        :type obj: ApplicationHub
        :return: list()
        """
        # 标记安装过程中涉及到的数据目录，通过此标记给前端
        # 给与前端提示信息，此标记对应于主机中的数据目录 data_folder
        # 在后续前端提供出安装参数后，我们应该检查其准确性
        if not obj.app_install_args:
            return list()
        origin_args = json.loads(obj.app_install_args)
        final_args = self.make_product_config_overwrite(
            app_name=obj.app_name,
            rep_type="app_install_args",
            lst=origin_args
        )
        for item in final_args:
            self.make_editable(item)
        return self.format_app_install_args(final_args)

    def reformat_install_args(self, install_args):
        """
        重新格式化前端已经修改过了的install_args参数
        :param install_args: 前端修改过的安装参数
        :type install_args: list
        :return:
        """
        return self._parse(app_install_args=install_args)

    def remake_install_args(self, obj):
        """
        重新生成部署时需要使用的参数，相当于直接从数据库中解析完整的安装参数
        :param obj: ApplicationHub对象
        :type obj: ApplicationHub
        :return:
        """
        if not obj.app_install_args:
            return list()
        app_install_args = self.make_product_config_overwrite(
            app_name=obj.app_name,
            rep_type="app_install_args",
            lst=json.loads(obj.app_install_args)
        )
        return self._parse(app_install_args)

    def _parse(self, app_install_args):
        """
        格式化解析安装参数数据
        :param app_install_args: 安装参数
        :type app_install_args: list
        :return:
        """
        for el in app_install_args:
            if DIR_KEY in el.get("default") or "dir_key" in el:
                el["default"] = os.path.join(
                    self.data_folder,
                    el["default"].replace(DIR_KEY, "").lstrip("/")
                )
                el["dir_key"] = DIR_KEY
            if el.get("key") == "run_user":
                if self.host_user_map[self.ip] != "root":
                    el["default"] = self.host_user_map[self.ip]
                    continue
                if self.run_user:
                    el["default"] = self.run_user
        return app_install_args


class ValidateInstallService(object):
    """ 检查要安装的服务信息是否准确 """

    def __init__(self, data=None):
        """
        初始化方法
        :param data: 要被检验的服务信息
        :type data: list
        """
        if not data or not isinstance(data, list):
            raise GeneralError(
                "ValidateInstallService __init__ arg error: data"
            )
        self.data = data

    def check_service_port(self, app_port, ip):  # NOQA
        """
        检查服务端口
        :param app_port: 服务端口列表
        :type app_port: list
        :param ip: 主机ip地址
        :type ip: str
        :return:
        """
        salt_obj = SaltClient()
        for el in app_port:
            _port = el.get("default", "")
            if not _port or not str(_port).isnumeric():
                el["check_flag"] = False
                el["error_msg"] = f"端口 {_port} 必须为数字"
                continue
            # method1: 从OMP本机查看端口是否已被占用
            # _flag, _msg = public_utils.check_ip_port(ip=ip, port=int(_port))
            # method2: 从目标服务器查看端口是否被占用
            _flag, _msg = salt_obj.cmd(
                target=ip,
                command=f"</dev/tcp/{ip}/{_port}",
                timeout=10
            )
            if _flag:
                el["error_msg"] = f"主机 {ip} 上的端口 {_port} 已被占用"
        return app_port

    def check_service_args(self, app_install_args, data_path, ip):  # NOQA
        """
        检查服务的安装参数，路径检查
        :param app_install_args: 服务安装参数
        :type app_install_args: list
        :param data_path: 主机数据目录
        :type data_path: str
        :param ip: 主机ip地址
        :type ip: str
        :return:
        """
        _salt_obj = SaltClient()
        for el in app_install_args:
            if "dir_key" not in el:
                continue
            # 直接封装部署数据到数据库中
            _tobe_check_path = el["default"]
            _cmd = \
                f"test -d {_tobe_check_path} && echo 'EXISTS' || echo 'OK'"
            _flag, _msg = _salt_obj.cmd(
                target=ip,
                command=_cmd,
                timeout=10
            )
            if not _flag:
                el["error_msg"] = \
                    f"无法确定该路径状态: {_tobe_check_path}; " \
                    f"请检查主机及主机Agent状态是否正常"
                continue
            if "OK" not in _msg:
                el["check_flag"] = False
                el["error_msg"] = f"{_tobe_check_path} 在目标主机 {ip} 上已存在"
        return app_install_args

    def check_single_service(self, dic):  # NOQA
        """
        检查单个服务的安装信息
        :param dic: 服务安装信息
        :type dic: dict
        :return:
        """
        _dic = deepcopy(dic)
        _ip = _dic.get("ip")
        _host_obj = Host.objects.filter(ip=_ip).last()
        if not _host_obj:
            _dic["error_msg"] = f"主机 {_ip} 不存在"
            return _dic
        _data_path = _host_obj.data_folder
        # 检查端口是否被占用
        app_port = self.check_service_port(
            app_port=_dic.get("app_port", []),
            ip=_ip
        )
        # 校验安装参数
        app_install_args = self.check_service_args(
            app_install_args=_dic.get("app_install_args", []),
            data_path=_data_path,
            ip=_ip
        )
        _dic["app_port"] = app_port
        _dic["app_install_args"] = app_install_args
        return _dic

    def run(self):
        """
        运行检查入口函数
        :return:
        """
        thread_p = ThreadPoolExecutor(
            max_workers=10, thread_name_prefix="check_install_service_"
        )
        # futures_list:[(item, future)]
        futures_list = list()
        for item in self.data:
            future = thread_p.submit(self.check_single_service, item)
            futures_list.append((item.get("service_instance_name"), future))
        # result_list:[{}, ...]
        result_list = list()
        for f in futures_list:
            result_list.append(f[1].result())
        thread_p.shutdown(wait=True)
        return result_list


class BaseEnvServiceUtils(object):
    """ 解决base_env服务的安装事宜 """

    def __init__(self, all_install_service_lst, host_user_map):
        """
        解决依赖于base_env服务的安装操作
        :param all_install_service_lst: 所有需要安装的服务
        :type all_install_service_lst: list
        """
        self.all = all_install_service_lst
        self.host_user_map = host_user_map

    def _dep_parse(self, dep_lst, base_env_dic, base_env_ser_lst, item):  # NOQA
        """
        解析依赖关系
        :param dep_lst: 服务依赖列表
        :param base_env_dic: 基础依赖字典，去重作用
        :param base_env_ser_lst: 所有基础依赖服务数据
        :param item: 要安装的某个服务的信息
        :return:
        """
        for el in dep_lst:
            # 服务版本弱依赖逻辑 jon.liu 20211225
            _dep_obj = ApplicationHub.objects.filter(
                app_name=el["name"],
                app_version__startswith=el["version"]
            ).last()
            if not _dep_obj.is_base_env:
                continue
            # 当被依赖的基础服务已经被安装时，使用如下方法进行过滤处理
            # 服务版本弱依赖逻辑 jon.liu 20211225
            if Service.split_objects.filter(
                    ip=item["ip"],
                    service__app_name=el["name"],
                    service__app_version__startswith=el["version"]
            ).count() > 0:
                continue
            if item["ip"] in base_env_dic and \
                    el["name"] in base_env_dic[item["ip"]]:
                continue
            _ins_name = \
                el["name"] + "-" + "-".join(item["ip"].split(".")[-2:])
            base_env_ser_lst.append({
                "name": el["name"],
                "version": el["version"],
                "ip": item["ip"],
                "install_args": ServiceArgsPortUtils(
                    ip=item["ip"],
                    data_folder=item["data_folder"],
                    run_user=item["run_user"],
                    host_user_map=self.host_user_map
                ).remake_install_args(obj=_dep_obj),
                "ports": ServiceArgsPortUtils(
                    ip=item["ip"],
                    data_folder=item["data_folder"],
                    run_user=item["run_user"],
                    host_user_map=self.host_user_map
                ).get_app_port(obj=_dep_obj),
                "instance_name": _ins_name
            })
            if item["ip"] not in base_env_dic:
                base_env_dic[item["ip"]] = list()
            base_env_dic[item["ip"]].append(el["name"])

    def run(self):
        """
        解析base_env数据入口
        :return:
        """
        base_env_dic = dict()
        base_env_ser_lst = list()
        for item in self.all:
            app_obj = ApplicationHub.objects.filter(
                app_name=item["name"],
                app_version=item["version"]
            ).last()
            # 当前服务没有依赖的情况
            if not app_obj.app_dependence or \
                    not json.loads(app_obj.app_dependence):
                continue
            _dep_lst = json.loads(app_obj.app_dependence)
            self._dep_parse(
                dep_lst=_dep_lst,
                base_env_dic=base_env_dic,
                base_env_ser_lst=base_env_ser_lst,
                item=item
            )
        return base_env_ser_lst


class WithServiceUtils(object):
    """ 解决带有with的服务场景 """

    def __init__(self, all_install_service_lst,
                 unique_key=None, run_user=None, host_user_map=None):
        """
        解决依赖于base_env服务的安装操作
        :param all_install_service_lst: 所有需要安装的服务
        :type all_install_service_lst: list
        :param unique_key: 安装标识
        :type unique_key: str
        :param run_user: 运行用户
        :type run_user: str
        :param host_user_map: 主机与运行用户关系
        :type host_user_map: str
        """
        self.all = all_install_service_lst
        self.unique_key = unique_key
        self.run_user = run_user
        self.host_user_map = host_user_map

    def parse_single_service(self, ser_dic):
        """
        解析单个服务的with场景，并拼接为最终可安装的数据格式
        :param ser_dic: 服务信息
        :type ser_dic: dict
        :return:
        """
        _ser = {
            "name": ser_dic.get("name"),
            "version": ser_dic.get("version")
        }
        _ser_lst = list()
        with_ser = ser_dic.get("with")
        is_found_flag = False  # 是否已经找到with服务的标识
        for item in self.all:
            _tmp_ser = deepcopy(_ser)
            # 当需要被with的服务在需要安装的服务列表中时
            if item.get("name") == with_ser:
                ip = item.get("ip")
                data_folder = item.get("data_folder")
                run_user = item.get("run_user")
                _app = ApplicationHub.objects.filter(
                    app_name=_tmp_ser["name"],
                    app_version=_tmp_ser["version"]
                ).last()
                install_args = ServiceArgsPortUtils(
                    ip=ip,
                    data_folder=data_folder,
                    run_user=run_user,
                    host_user_map=self.host_user_map
                ).remake_install_args(obj=_app)
                ports = ServiceArgsPortUtils(
                    ip=ip,
                    data_folder=data_folder,
                    run_user=run_user,
                    host_user_map=self.host_user_map
                ).get_app_port(obj=_app)
                instance_name = \
                    _tmp_ser["name"] + "-" + "-".join(ip.split(".")[-2:])
                _tmp_ser["ip"] = ip
                _tmp_ser["data_folder"] = data_folder
                _tmp_ser["run_user"] = run_user
                _tmp_ser["install_args"] = install_args
                _tmp_ser["ports"] = ports
                _tmp_ser["instance_name"] = instance_name
                _tmp_ser["cluster_name"] = None
                _ser_lst.append(_tmp_ser)
                is_found_flag = True
        # 如果没有找到，则证明被with的服务是在复用的列表内的，需要查看当前系统内的该服务信息
        if not is_found_flag:
            with_ser_ips = Service.split_objects.filter(
                service__app_name=with_ser).values("ip")
            with_ser_ips = [el["ip"] for el in with_ser_ips]
            for _ip in with_ser_ips:
                _tmp_ser = deepcopy(_ser)
                data_folder = Host.objects.filter(ip=_ip).last().data_folder
                run_user = self.run_user
                _app = ApplicationHub.objects.filter(
                    app_name=_tmp_ser["name"],
                    app_version=_tmp_ser["version"]
                ).last()
                install_args = ServiceArgsPortUtils(
                    ip=_ip,
                    data_folder=data_folder,
                    run_user=run_user,
                    host_user_map=self.host_user_map
                ).remake_install_args(obj=_app)
                ports = ServiceArgsPortUtils(
                    ip=_ip,
                    data_folder=data_folder,
                    run_user=run_user,
                    host_user_map=self.host_user_map
                ).get_app_port(obj=_app)
                instance_name = \
                    _tmp_ser["name"] + "-" + "-".join(_ip.split(".")[-2:])
                _tmp_ser["ip"] = _ip
                _tmp_ser["data_folder"] = data_folder
                _tmp_ser["run_user"] = run_user
                _tmp_ser["install_args"] = install_args
                _tmp_ser["ports"] = ports
                _tmp_ser["instance_name"] = instance_name
                _tmp_ser["cluster_name"] = None
                _ser_lst.append(_tmp_ser)
        return _ser_lst

    def run(self):
        """
        运行方法
        :return:
        """
        with_ser_lst = BaseRedisData(
            unique_key=self.unique_key).get_with_ser()
        ret_lst = list()
        for item in with_ser_lst:
            ret_lst.extend(self.parse_single_service(ser_dic=item))
        return ret_lst


class DataJson(object):
    """ 生成data.json数据 """

    def __init__(self, operation_uuid, service_obj=None):
        """
        data.json数据生成方法
        :param operation_uuid: 唯一操作uuid
        :param service_obj: service 操作对象，可为空
        :type operation_uuid: str
        """
        self.operation_uuid = operation_uuid
        self.service_obj = service_obj

    def get_ser_install_args(self, obj):  # NOQA
        """
        获取服务的安装参数
        :param obj: Service
        :type obj: Service
        :return:
        """
        deploy_detail = DetailInstallHistory.objects.get(service=obj)
        install_args = \
            deploy_detail.install_detail_args.get("install_args")
        deploy_mode = \
            deploy_detail.install_detail_args.get("deploy_mode")
        return {
            "install_args": install_args,
            "deploy_mode": deploy_mode
        }

    def parse_single_service(self, obj):
        """
        解析单个服务数据
        :param obj: Service
        :type obj: Service
        :return:
        """
        _ser_dic = {
            "ip": obj.ip,
            "name": obj.service.app_name,
            "role": obj.service_role if obj.service_role else "master",
            "instance_name": obj.service_instance_name,
            "cluster_name": obj.cluster.cluster_name if obj.cluster else None,
            "ports": json.loads(obj.service_port) if obj.service_port else [],
            "dependence": json.loads(obj.service_dependence) if
            obj.service_dependence else [],
            "vip": obj.vip
        }
        _others = self.get_ser_install_args(obj)
        _ser_dic.update(_others)
        return _ser_dic

    def make_data_json(self, json_lst):
        """
        创建data.json数据文件
        :param json_lst: 服务及分布信息组成的列表
        :type json_lst: list
        :return:
        """
        _path = os.path.join(
            PROJECT_DIR,
            "package_hub/data_files",
            f"{self.operation_uuid}.json"
        )
        if not os.path.exists(os.path.dirname(_path)):
            os.makedirs(os.path.dirname(_path))
        with open(_path, "w", encoding="utf8") as fp:
            fp.write(json.dumps(json_lst, indent=2, ensure_ascii=False))

    def run(self):
        """
        生成data.json方法入口
        :return:
        """
        # step1: 获取所有的服务列表
        # edit by vum:
        # 服务中表中会有残留 base_env 服务的情况，类似 jdk，此时不宜获取所有服务
        if self.service_obj:
            all_ser_lst = self.service_obj
        else:
            all_ser_lst = Service.split_objects.all()
        json_lst = list()
        for item in all_ser_lst:
            json_lst.append(self.parse_single_service(obj=item))
        # 在json文件中标记该服务所在主机上的agent的地址
        ip_agent_dir_dir = {
            el["ip"]: el["agent_dir"] for el in
            Host.objects.values("ip", "agent_dir")
        }
        for item in json_lst:
            item["agent_dir"] = ip_agent_dir_dir.get(item.get("ip"))
        # step2: 生成data.json
        self.make_data_json(json_lst=json_lst)


class CreateInstallPlan(object):
    """ 生成部署计划相关数据 """

    def __init__(self, all_install_service_lst, unique_key=None):
        """

        :param all_install_service_lst:
        """
        logger.info(f"CreateInstallPlan.__init__: {all_install_service_lst}")
        self.install_services = all_install_service_lst
        self.unique_key = unique_key

    def get_app_obj_for_service(self, dic):  # NOQA
        """
        获取服务实例表中关联的app对象
        :param dic: 服务数据
        :type dic: dict
        :return:
        """
        return ApplicationHub.objects.filter(
            app_name=dic["name"], app_version__startswith=dic["version"]
        ).last()

    def get_controllers_for_service(self, dic):  # NOQA
        """
        获取服务控制脚本信息
        :param dic: 服务数据
        :type dic: dict
        :return:
        """
        # 获取关联application对象
        _app = self.get_app_obj_for_service(dic)
        # TODO 确定application表内的app_controllers字段存储类型
        _app_controllers = json.loads(_app.app_controllers)
        # 获取服务家目录
        install_args = dic["install_args"]
        _home = ""
        data_folder = Host.objects.filter(ip=dic["ip"]).last().data_folder
        for el in install_args:
            if "dir_key" in el and el["key"] == "base_dir":
                _home = el["default"]
        real_home = os.path.join(data_folder, _home.rstrip("/"))
        _new_controller = dict()
        # 更改服务控制脚本、拼接相对路径
        for key, value in _app_controllers.items():
            if not value:
                continue
            _new_controller[key] = os.path.join(real_home, value)
        # 如果该服务需要在整体安装完成后有一些操作，那么需要重新构建post_action
        # 在每次安装完所有服务后，需要搜索出相应的post_action并统一执行
        if "post_action" in _app.extend_fields and \
                _app.extend_fields["post_action"]:
            _new_controller["post_action"] = os.path.join(
                real_home, _app.extend_fields["post_action"]
            )
        return _new_controller

    def get_env_for_service(self):  # NOQA
        """
        获取当前环境
        :return:
        """
        # TODO 暂时使用默认环境
        return Env.objects.last()

    def create_connect_info(self, dic):  # NOQA
        """
        创建或获取服务的用户名、密码信息
        :param dic: 服务数据
        :type dic: dict
        :return:
        """
        username = password = username_enc = password_enc = ""
        for item in dic["install_args"]:
            if not item["default"]:
                continue
            if item["key"] == "username":
                username = item["default"]
            if item["key"] == "password":
                password = item["default"]
            if item["key"] == "username_enc":
                username_enc = item["default"]
            if item["key"] == "password_enc":
                password_enc = item["default"]
        if username or password or username_enc or password_enc:
            _ser_conn_obj, _ = ServiceConnectInfo.objects.get_or_create(
                service_name=dic["name"],
                service_username=username,
                service_password=password,
                service_username_enc=username_enc,
                service_password_enc=password_enc
            )
            return _ser_conn_obj
        return None

    def create_cluster(self, dic):  # NOQA
        """
        创建集群信息
        :param dic: 服务数据
        :type dic: dict
        :return:
        """
        if "cluster_name" not in dic or not dic["cluster_name"]:
            return None
        _app_obj = self.get_app_obj_for_service(dic)
        # 根据要安装的服务是组件还是应用，这里仅做组件级别的集群
        if _app_obj.app_type != 0:
            return None
        # 如果存在则获取、如果不存在则创建
        cluster_obj, _ = ClusterInfo.objects.get_or_create(
            cluster_service_name=dic["name"],
            cluster_name=dic["cluster_name"],
            service_connect_info=self.create_connect_info(dic)
        )
        return cluster_obj

    def _get_exist_dep(self, inner):
        """
        获取已存在依赖信息
        :param inner:
        :type inner: dict
        :return:
        """
        if inner.get("type") == "cluster":
            cl_obj = ClusterInfo.objects.filter(id=inner["id"]).last()
            return {
                "name": cl_obj.cluster_service_name,
                "cluster_name": cl_obj.cluster_name,
                "instance_name": None
            }
        ser_obj = Service.split_objects.filter(id=inner["id"]).last()
        return {
            "name": ser_obj.service.app_name,
            "cluster_name": None,
            "instance_name": ser_obj.service_instance_name
        }

    def _get_install_dep(self, inner):
        """
        获取将要安装服务中的被依赖项
        :param inner:
        :return:
        """
        _ser_name = inner["name"]
        _ser_version = inner["version"]
        for el in self.install_services:
            if el.get("name") == _ser_name and \
                    el.get("version").startswith(_ser_version):
                cluster_name = el.get("cluster_name")
                instance_name = el.get("instance_name")
                if cluster_name:
                    instance_name = None
                else:
                    cluster_name = None
                return {
                    "name": el.get("name"),
                    "cluster_name": cluster_name,
                    "instance_name": instance_name
                }
        raise ValidationError(
            f"无法找到被依赖的服务[{_ser_name}({_ser_version})]")

    def get_dependence(self, dic):
        """
        获取服务依赖的实例信息
        :param dic:
        :return:
        """
        _obj = self.get_app_obj_for_service(dic)
        _dep_lst = list()
        if not _obj.app_dependence or not json.loads(_obj.app_dependence):
            return []
        lst = json.loads(_obj.app_dependence)

        exist_data = BaseRedisData(
            unique_key=self.unique_key
        ).get_step_2_origin_data().get("use_exist")
        for item in lst:
            # 已存在的base_env服务依赖
            _dep_obj = ApplicationHub.objects.filter(
                app_name=item.get("name"),
                app_version__startswith=item.get("version")
            ).last()
            if _dep_obj.is_base_env:
                _ser_obj = Service.split_objects.filter(
                    service=_dep_obj, ip=dic.get("ip")
                ).last()
                if _ser_obj:
                    _dep_lst.append({
                        "name": item.get("name"),
                        "cluster_name": None,
                        "instance_name": _ser_obj.service_instance_name
                    })
                    continue
            if item.get("name") in exist_data:
                _de = exist_data[item["name"]]
                _dep_lst.append(self._get_exist_dep(_de))
            else:
                _dep_lst.append(self._get_install_dep(item))
        return _dep_lst

    def create_service(self, dic):
        """
        创建服务实例
        :param dic: 服务数据
        :type dic: dict
        :return:
        """
        # 创建服务实例对象，默认从安装来的服务的状态为 安装中
        _ser_obj = Service(
            ip=dic["ip"],
            service_instance_name=dic["instance_name"],
            service=self.get_app_obj_for_service(dic),
            service_port=json.dumps(dic.get("ports")),
            service_role=dic.get("roles", ""),
            service_controllers=self.get_controllers_for_service(dic),
            cluster=self.create_cluster(dic),
            env=self.get_env_for_service(),
            service_status=6,
            service_connect_info=self.create_connect_info(dic),
            service_dependence=json.dumps(self.get_dependence(dic)),
            vip=dic.get("vip")
        )
        _ser_obj.save()
        return _ser_obj

    def create_product_instance(self, dic):  # NOQA
        """
        创建产品实例
        :param dic: 服务数据
        :type dic: dict
        :return:
        """
        _obj = self.get_app_obj_for_service(dic)
        if not _obj or _obj.app_type != ApplicationHub.APP_TYPE_SERVICE:
            return
        _data = BaseRedisData(
            unique_key=self.unique_key).get_step_3_checked_data()
        for item in _data.get("data", {}).get("basic", []):
            if _obj.product.pro_name == item.get("name") and \
                    _obj.product.pro_version == item.get("version"):
                product_instance_name = item.get("cluster_name")
                Product.objects.get_or_create(
                    product_instance_name=product_instance_name,
                    product=_obj.product
                )

    def check_if_has_post_action(self, ser):  # NOQA
        """
        检测是否需要执行安装后的动作
        :param ser: 服务对象
        :type ser Service
        :return:
        """
        if "post_action" in ser.service_controllers and \
                ser.service_controllers.get("post_action"):
            return True
        return False

    def create_pre_install_history(self, main_obj):
        """
        创建安装计划，在执行安装计划时，优先执行此处的操作记录
        :param main_obj:
        :return:
        """
        _data = list(DetailInstallHistory.objects.filter(
            main_install_history=main_obj
        ).values_list("service__ip", flat=True))

        for item in set(_data):
            PreInstallHistory(
                main_install_history=main_obj,
                ip=item
            ).save()

    def create_post_install_history(self, main_obj):
        """
        创建安装后的行为规范
        :param main_obj:
        :return:
        """
        # 在安装完成后，需要执行一些操作
        # 在这里进行定制化处理，所有的安装操作都需要执行下重新加载nacos和tengine的配置
        # 此处专为 云智慧 进行定制
        PostInstallHistory(main_install_history=main_obj).save()
        # post_action_queryset = DetailInstallHistory.objects.select_related(
        #     "service", "service__service", "service__service__app_package"
        # ).filter(main_install_history=main_obj).exclude(
        #     post_action_flag__in=[2, 4]
        # )
        # if post_action_queryset.exists():
        #     PostInstallHistory(main_install_history=main_obj).save()
        #     return
        # logger.info(f"Do execute_post_install for {main_obj.operation_uuid}")
        # if DetailInstallHistory.objects.filter(
        #         main_install_history=main_obj,
        #         service__service__app_type=ApplicationHub.APP_TYPE_SERVICE
        # ).exists():
        #     PostInstallHistory(main_install_history=main_obj).save()

    def run(self):
        """
        服务部署信息入库操作
        :return:
        """
        try:
            logger.info("start CreateInstallPlan.run!")
            with transaction.atomic():
                # step0: 生成
                # step1: 生成操作唯一uuid，创建主安装记录
                operation_uuid = self.unique_key
                main_obj = MainInstallHistory(
                    operation_uuid=operation_uuid,
                    install_status=0,
                    install_args=self.install_services
                )
                main_obj.save()
                # step2: 创建安装细节表
                for item in self.install_services:
                    # 创建服务实例对象
                    ser_obj = self.create_service(item)
                    # 创建产品实例对象
                    self.create_product_instance(item)
                    post_action_flag = 0 if self.check_if_has_post_action(
                        ser_obj) else 4
                    DetailInstallHistory(
                        service=ser_obj,
                        main_install_history=main_obj,
                        install_detail_args=item,
                        post_action_flag=post_action_flag
                    ).save()
                # 创建安装前的操作记录
                self.create_pre_install_history(main_obj)
                # 创建安装后操作日志
                self.create_post_install_history(main_obj)
                _json_obj = DataJson(operation_uuid=operation_uuid)
                _json_obj.run()
                # 调用安装异步任务，并回写异步任务到
                task_id = install_service_task.delay(main_obj.id)
                MainInstallHistory.objects.filter(id=main_obj.id).update(
                    task_id=task_id
                )
                # 删除redis中缓存的安装临时数据
                BaseRedisData(unique_key=self.unique_key).delete_all_keys()
                # 更新主机上的服务数量
                _ser_ip_lst = DetailInstallHistory.objects.filter(
                    main_install_history=main_obj,
                    service__service__is_base_env=False
                ).values("service__ip")
                _tmp_dic = dict()
                for item in _ser_ip_lst:
                    if item["service__ip"] not in _tmp_dic:
                        _tmp_dic[item["service__ip"]] = 0
                    _tmp_dic[item["service__ip"]] += 1
                for key, value in _tmp_dic.items():
                    Host.objects.filter(ip=key).update(
                        service_num=F("service_num") + value)
        except Exception as e:
            logger.error(
                f"CreateInstallPlan.run failed with error: \n"
                f"{traceback.format_exc()}")
            return False, e
        return True, operation_uuid


class MakeServiceOrder(object):
    def __init__(self, all_service):
        self.all_service = all_service

    def run(self):
        return self.make_install_order()

    def make_install_order(self):
        """
        :return:
        """
        final_lst = list()
        # 对基础组件进行排序处理，其中基础配置中的 BASIC_ORDER 为基础组件的排序等级
        # 如果有其他组件需要安装，怎需要在配置中进行额外的配置
        for i in range(10):
            if i not in BASIC_ORDER:
                break
            _lst = [
                el for el in self.all_service
                if el.get("name") in BASIC_ORDER[i]
            ]
            final_lst.extend(_lst)
        all_self_app = ApplicationHub.objects.filter(
            app_type=ApplicationHub.APP_TYPE_SERVICE
        ).values("app_name", "app_version", "extend_fields")
        all_ser_dic = {
            el["app_name"] + "_" + el["app_version"]: el for el in all_self_app
        }
        level_0_lst = list()
        level_1_lst = list()
        for item in self.all_service:
            _key = item["name"] + "_" + item["version"]
            if _key not in all_ser_dic:
                continue
            if str(all_ser_dic[_key]["extend_fields"].get("level")) == "0":
                level_0_lst.append(item)
            else:
                level_1_lst.append(item)
        final_lst.extend(level_0_lst)
        final_lst.extend(level_1_lst)
        return final_lst


class ValidateInstallServicePortArgs(object):
    """ 检查要安装的服务信息是否准确 """

    def __init__(self, data=None):
        """
        初始化方法
        :param data: 要被检验的服务信息
        :type data: list
        """
        if not data or not isinstance(data, list):
            raise GeneralError(
                "ValidateInstallService __init__ arg error: data"
            )
        self.data = data

    def check_service_port(self, app_port, ip):  # NOQA
        """
        检查服务端口
        :param app_port: 服务端口列表
        :type app_port: list
        :param ip: 主机ip地址
        :type ip: str
        :return:
        """
        salt_obj = SaltClient()
        for el in app_port:
            _port = el.get("default", "")
            if not _port or not str(_port).isnumeric():
                el["check_flag"] = False
                el["error_msg"] = f"端口 {_port} 必须为数字"
                continue
            # method1: 从OMP本机查看端口是否已被占用
            # _flag, _msg = public_utils.check_ip_port(ip=ip, port=int(_port))
            # method2: 从目标服务器查看端口是否被占用
            _flag, _msg = salt_obj.cmd(
                target=ip,
                command=f"</dev/tcp/{ip}/{_port}",
                timeout=10
            )
            if _flag:
                el["check_flag"] = False
                el["error_msg"] = f"主机 {ip} 上的端口 {_port} 已被占用"
        return app_port

    def check_service_args(self, app_install_args, data_path, ip):  # NOQA
        """
        检查服务的安装参数，路径检查
        :param app_install_args: 服务安装参数
        :type app_install_args: list
        :param data_path: 主机数据目录
        :type data_path: str
        :param ip: 主机ip地址
        :type ip: str
        :return:
        """
        _salt_obj = SaltClient()
        for el in app_install_args:
            if el.get("key") == "instance_name" and Service.split_objects.filter(
                    service_instance_name=el.get("default")
            ).count() != 0:
                el["check_flag"] = False
                el["error_msg"] = f"实例名称 {el.get('default')} 已存在"
                continue
            if "dir_key" not in el:
                continue
            _tobe_check_path = el.get("default", "")
            _cmd = \
                f"test -d {_tobe_check_path} && echo 'EXISTS' || echo 'OK'"
            _flag, _msg = _salt_obj.cmd(
                target=ip,
                command=_cmd,
                timeout=10
            )
            if not _flag:
                el["check_flag"] = False
                el["error_msg"] = \
                    f"无法确定该路径状态: {_tobe_check_path}; " \
                    f"请检查主机及主机Agent状态是否正常"
                continue
            if "OK" not in _msg:
                el["check_flag"] = False
                el["error_msg"] = f"{_tobe_check_path} 在目标主机 {ip} 上已存在"
        return app_install_args

    def check_single_service(self, dic):  # NOQA
        """
        检查单个服务的安装信息
        :param dic: 服务安装信息
        :type dic: dict
        :return:
        """
        _dic = deepcopy(dic)
        _ip = _dic.get("ip")
        _host_obj = Host.objects.filter(ip=_ip).last()
        if not _host_obj:
            _dic["check_flag"] = False
            _dic["error_msg"] = f"主机 {_ip} 不存在"
            return _dic
        _data_path = _host_obj.data_folder
        # 检查端口是否被占用
        app_port = self.check_service_port(
            app_port=_dic.get("ports", []),
            ip=_ip
        )
        # 校验安装参数
        app_install_args = self.check_service_args(
            app_install_args=_dic.get("install_args", []),
            data_path=_data_path,
            ip=_ip
        )
        _dic["ports"] = app_port
        _dic["install_args"] = app_install_args
        return _dic

    def run(self):
        """
        运行检查入口函数
        :return:
        """
        thread_p = ThreadPoolExecutor(
            max_workers=10, thread_name_prefix="check_install_service_"
        )
        # futures_list:[(item, future)]
        futures_list = list()
        for item in self.data:
            future = thread_p.submit(self.check_single_service, item)
            futures_list.append((item.get("instance_name"), future))
        # result_list:[{}, ...]
        result_list = list()
        for f in futures_list:
            result_list.append(f[1].result())
        thread_p.shutdown(wait=True)
        # TODO 整体服务间的关键校验
        return result_list
