# -*- coding: utf-8 -*-
# Project: install_utils
# Author: jon.liu@yunzhihui.com
# Create time: 2021-10-24 14:11
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
安装过程中页面显示数据解析工具
"""

import os
import json
import uuid
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor

from django.db import transaction

from omp_server.settings import PROJECT_DIR
from db_models.models import (
    Env,
    Host,
    ApplicationHub,
    ProductHub,
    Product,
    Service,
    ClusterInfo,
    ServiceConnectInfo,
    MainInstallHistory,
    DetailInstallHistory
)
from app_store.tasks import install_service
from utils.common.exceptions import GeneralError
# from utils.plugin import public_utils
from utils.plugin.salt_client import SaltClient

DIR_KEY = "{data_path}"


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
        ret_lst.append(el)
        unique_dic[_unique] = True
    return ret_lst


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


def make_app_install_args(app_install_args):
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
        make_editable(el)
    return app_install_args


class DataJson(object):
    """ 生成data.json数据 """

    def __init__(self, operation_uuid):
        """
        data.json数据生成方法
        :param operation_uuid: 唯一操作uuid
        :type operation_uuid: str
        """
        self.operation_uuid = operation_uuid

    def get_ser_install_args(self, obj):    # NOQA
        """
        获取服务的安装参数
        :param obj: Service
        :type obj: Service
        :return:
        """
        deploy_detail = DetailInstallHistory.objects.get(service=obj)
        install_args = \
            deploy_detail.install_detail_args.get("app_install_args")
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
            "instance_name": obj.service_instance_name,
            "cluster_name": obj.cluster.cluster_name if obj.cluster else None,
            "ports": json.loads(obj.service_port) if obj.service_port else [],
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
        all_ser_lst = Service.objects.all()
        json_lst = list()
        for item in all_ser_lst:
            json_lst.append(self.parse_single_service(obj=item))
        # step2: 生成data.json
        self.make_data_json(json_lst=json_lst)


class SerDependenceParseUtils(object):
    """
    依赖解决工具类
    """

    def __init__(self, parse_name, parse_version):
        """
        初始化对象, 服务级别的解析，包含自研服务和基础组件服务
        :param parse_name: 要解析的名称，服务
        :type parse_name: str
        :param parse_version: 要解析的版本
        :type parse_version: str
        """
        self.parse_name = parse_name
        self.parse_version = parse_version
        self.unique_key = self.parse_name + self.parse_version

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
        # 判断当前服务的集群
        cluster_info = list(ClusterInfo.objects.filter(
            cluster_service_name=obj.app_name
        ).values("id", "cluster_name"))
        # 判断当前服务的实例信息
        instance_info = list(Service.objects.filter(
            service__app_name=obj.app_name,
            service__app_version=obj.app_version
        ).values("ip", "service_instance_name", "id"))
        is_pack_exist = False
        # 判断当前应用商店内是否包含该服务以及该服务的安装包条件
        if obj.app_package:
            path = os.path.join(
                PROJECT_DIR,
                "package_hub",
                obj.app_package.package_path,
                obj.app_package.package_name
            )
            if os.path.exists(path):
                is_pack_exist = True
        return cluster_info, instance_info, is_pack_exist

    def get_deploy_mode(self, obj):     # NOQA
        """
        解析服务的部署模式信息
        [
          {
            "key": "single",
            "name": "单实例"
          }
        ]
        :param obj: 服务对象
        :type obj: ApplicationHub
        :return: list()
        """
        if not obj.extend_fields or not obj.extend_fields.get("deploy", {}):
            return [{"key": "single", "name": "单实例"}]
        deploy_info = obj.extend_fields.get("deploy", {})
        ret_lst = list()
        if "single" in deploy_info:
            ret_lst.extend(deploy_info["single"])
        if "complex" in deploy_info:
            ret_lst.extend(deploy_info["complex"])
        return ret_lst

    def get_is_base_env(self, obj):     # NOQA
        """
        确定当前服务是否为基础环境：如 jdk 等
        :param obj: 服务对象
        :type obj: ApplicationHub
        :return:
        """
        if not obj.extend_fields:
            return False
        return obj.extend_fields.get("base_env", False)

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
            _app = ApplicationHub.objects.filter(
                app_name=_name,
                app_version=_version,
                is_release=True
            ).order_by("created").last()
            # 定义服务&版本唯一标准，防止递归错误
            unique_key = str(_name) + str(_version)
            # 如果当前服务和需要被解析的源服务重叠，那么则跳过
            # 如果当前服务的依赖关系已经被解决，那么则跳过
            if unique_key == self.unique_key or unique_key in unique_key_lst:
                continue
            unique_key_lst.append(unique_key)
            # 判断当前被依赖服务是否存在，如果不存在就直接返回，不再处理深层依赖
            if not _app:
                inner["cluster_info"] = list()
                inner["instance_info"] = list()
                inner["app_port"] = list()
                inner["app_install_args"] = list()
                inner["is_in_hub"] = False
                inner["is_base_env"] = False
                inner["is_pack_exist"] = False
                inner["deploy_mode"] = list()
                inner["process_continue"] = False
                inner["process_message"] = f"应用商店内未包含{_name}服务"
                lst.append(inner)
                continue
            # 查看当前服务是否被安装
            cluster_info, instance_info, is_pack_exist = \
                self.get_ser_instances(obj=_app)
            # 获取依赖服务的相关信息
            inner["cluster_info"] = cluster_info
            inner["instance_info"] = instance_info
            # 获取依赖服务端口及其他参数信息
            inner["app_port"] = \
                json.loads(_app.app_port) if _app.app_port else list()
            if _app.app_install_args:
                _app_install_args = json.loads(_app.app_install_args)
                inner["app_install_args"] = \
                    make_app_install_args(_app_install_args)
            else:
                inner["app_install_args"] = list()
            inner["is_in_hub"] = True
            inner["is_base_env"] = self.get_is_base_env(obj=_app)
            inner["is_pack_exist"] = is_pack_exist
            inner["deploy_mode"] = self.get_deploy_mode(obj=_app)
            if cluster_info or instance_info or is_pack_exist:
                inner["process_continue"] = True
            else:
                inner["process_continue"] = False
                inner["process_message"] = f"服务{_name}未安装且无法找到安装包"
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


class ProDependenceParseUtils(object):
    """
    依赖解决工具类
    """

    def __init__(self, parse_name, parse_version):
        """
        初始化对象, 产品级别的解析
        :param parse_name: 要解析的产品、应用名称
        :param parse_version: 要解析的版本
        """
        self.parse_name = parse_name
        self.parse_version = parse_version
        self.unique_key = self.parse_name + self.parse_version

    def get_pro_instances(self, obj):   # NOQA
        """
        获取产品的实例信息，被依赖产品是否已经被安装
        :param obj: 应用实例对象
        :type obj: ProductHub
        :return:
        """
        ret_lst = Product.objects.filter(
            product__pro_name=obj.pro_name
        ).values("id", "product_instance_name")
        return list(ret_lst)

    def get_dependence(self, lst, dep):
        """
        解决产品依赖关系核心方法
        :param lst: 存储结果的列表
        :type lst: list
        :param dep: 服务依赖关系列表
        :type dep: list
        :return: list()
        """
        unique_key_lst = list()
        for inner in dep:
            _name, _version = inner.get("name"), inner.get("version")
            _pro = ProductHub.objects.filter(
                pro_name=_name,
                pro_version=_version,
                is_release=True
            ).order_by("created").last()
            # 定义服务&版本唯一标准，防止递归错误
            unique_key = str(_name) + str(_version)
            # 如果当前产品和需要被解析的源产品重叠，那么则跳过
            # 如果当前产品的依赖关系已经被解决，那么则跳过
            if unique_key == self.unique_key or unique_key in unique_key_lst:
                continue
            unique_key_lst.append(unique_key)
            # 判断当前被依赖服务是否存在，如果不存在就直接返回，不再处理深层依赖
            if not _pro:
                inner["instance_info"] = list()
                inner["is_in_hub"] = False
                inner["process_continue"] = False
                inner["process_message"] = f"应用商店内未包含{_name}应用"
                lst.append(inner)
                continue
            # 查看当前服务是否被安装
            instance_info = self.get_pro_instances(obj=_pro)
            # 获取依赖服务的相关信息
            inner["instance_info"] = instance_info
            inner["is_in_hub"] = True
            inner["process_continue"] = True
            lst.append(inner)
            if not _pro.pro_dependence:
                continue
            _pro_dependence = json.loads(_pro.pro_dependence)
            self.get_dependence(
                lst, dep=_pro_dependence
            )

    def get_newest_pro(self):
        """
        获取最新的产品对象，同产品，同版本
        :return: ProductHub
        """
        return ProductHub.objects.filter(
            pro_name=self.parse_name,
            pro_version=self.parse_version,
            is_release=True
        ).last()

    def run_pro(self):
        """
        解析产品的依赖关系入口
        :return: 产品关系依赖列表
        """
        _pro = self.get_newest_pro()
        if not _pro or not _pro.pro_dependence:
            return list()
        ret_lst = list()
        self.get_dependence(ret_lst, json.loads(_pro.pro_dependence))
        ret_lst = make_lst_unique(ret_lst, "name", "version")
        return ret_lst


class ServiceArgsSerializer(object):
    """ 服务安装过程中参数解析类 """

    def get_app_dependence(self, obj):  # NOQA
        """
        解析服务级别的依赖关系
        :param obj: 服务对象
        :type obj: ApplicationHub
        :return:
        """
        ser = SerDependenceParseUtils(obj.app_name, obj.app_version)
        return ser.run_ser()

    def get_app_port(self, obj):    # NOQA
        """
        获取app的端口
        :param obj: 服务对象
        :type obj: ApplicationHub
        :return: list()
        """
        if not obj.app_port:
            return []
        port_lst = json.loads(obj.app_port)
        for item in port_lst:
            make_editable(item)
        return port_lst

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
        return make_app_install_args(json.loads(obj.app_install_args))

    def get_deploy_mode(self, obj):  # NOQA
        """
        解析部署模式信息
        [
          {
            "key": "single",
            "name": "单实例"
          }
        ]
        :param obj: 服务对象
        :type obj: ApplicationHub
        :return:
        """
        # 如果服务未配置部署模式相关信息，那么默认为单实例模式
        ser = SerDependenceParseUtils(obj.app_name, obj.app_version)
        return ser.get_deploy_mode(obj)

    def _process_continue_parse(self, obj):  # NOQA
        """
        解析是否能够进行的核心接口
        :param obj: 服务对象
        :type obj: ApplicationHub
        :return: (bool, str)
        """
        if not obj.app_package:
            return False, f"服务{obj.app_name}无安装包"
        # 服务级别的安装包均存在于 verified 目录内，使用 package_name 即可拼接完成
        _path = os.path.join(
            PROJECT_DIR,
            "package_hub",
            obj.app_package.package_path,
            obj.app_package.package_name
        )
        if not os.path.exists(_path):
            return False, f"服务{obj.app_name}的安装包无法找到"
        return True, "success"

    def get_process_continue(self, obj):    # NOQA
        """
        解析能否继续进行的标志接口
        :param obj: 服务对象
        :type obj: ApplicationHub
        :return: bool
        """
        flag, _ = self._process_continue_parse(obj)
        return flag

    def get_process_message(self, obj):    # NOQA
        """
        解析能否继续进行的信息接口
        :param obj: 服务对象
        :type obj: ApplicationHub
        :return:
        """
        _, msg = self._process_continue_parse(obj)
        return msg


class ValidateExistService(object):
    """ 检查已存在服务信息是否准确 """

    def __init__(self, data=None):
        """
        初始化方法
        :param data: 要被检验的服务信息
        :type data: list
        """
        if not data or not isinstance(data, list):
            raise GeneralError(
                "ValidateExistService __init__ arg error: data")
        self.data = data

    def check_cluster(self, dic):   # NOQA
        """
        校验集群信息是否准确
        :param dic: 集群信息字典
        :type dic: dict
        :return:
        """
        if ClusterInfo.objects.filter(id=dic.get("id")).exists():
            dic["check_flag"] = True
            dic["check_msg"] = "success"
            return dic
        dic["check_flag"] = False
        dic["check_msg"] = f"复用已存在集群{dic.get('id', 'UNKNOWN')}不存在"
        return dic

    def check_single(self, dic):    # NOQA
        """
        检查服务的合法性
        :param dic: 服务信息字典
        :type dic: dict
        :return:
        """
        if Service.objects.filter(id=dic.get("id")).exists():
            dic["check_flag"] = True
            dic["check_msg"] = "success"
            return dic
        dic["check_flag"] = False
        dic["check_msg"] = f"复用已存在实例{dic.get('id', 'UNKNOWN')}不存在"
        return dic

    def run(self):
        """
        运行入口
        :return:
        """
        for item in self.data:
            _type = item.get("type")
            if _type not in ("cluster", "single"):
                item["check_flag"] = False
                item["check_msg"] = "已存在的服务信息必须在single和cluster内"
                continue
            _recheck_item = getattr(self, f"check_{_type}")(item)
            item.update(_recheck_item)
        return self.data


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

    def check_service_port(self, app_port, ip):     # NOQA
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
                el["check_msg"] = f"端口 {_port} 必须为数字"
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
                el["check_msg"] = f"主机 {ip} 上的端口 {_port} 已被占用"
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
            _tobe_check_path = os.path.join(
                data_path, el.get("default", "").lstrip("/"))
            # 直接封装部署数据到数据库中
            el["default"] = _tobe_check_path
            _cmd = \
                f"test -d {_tobe_check_path} && echo 'EXISTS' || echo 'OK'"
            _flag, _msg = _salt_obj.cmd(
                target=ip,
                command=_cmd,
                timeout=10
            )
            if not _flag:
                el["check_flag"] = False
                el["check_msg"] = \
                    f"无法确定该路径状态: {_tobe_check_path}; " \
                    f"请检查主机及主机Agent状态是否正常"
                continue
            if "OK" in _msg:
                el["check_flag"] = True
                el["check_msg"] = "success"
            else:
                el["check_flag"] = False
                el["check_msg"] = f"{_tobe_check_path} 在目标主机 {ip} 上已存在"
        return app_install_args

    def check_single_service(self, dic):    # NOQA
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
            _dic["check_msg"] = f"主机 {_ip} 不存在"
            return _dic
        _data_path = _host_obj.data_folder
        service_name = _dic.get("name")
        # 检查服务是否已在该主机上安装
        if Service.objects.filter(
                service__app_name=service_name, ip=_ip).exists():
            _dic["check_flag"] = False
            _dic["check_msg"] = f"该主机 {_ip} 已安装过 {service_name}, 请勿重复安装"
            return _dic
        # 检查实例名称是否重复
        service_instance_name = _dic.get("service_instance_name")
        if Service.objects.filter(
                service_instance_name=service_instance_name).exists():
            _dic["check_flag"] = False
            _dic["check_msg"] = "实例名称重复"
            return _dic
        if "is_pack_exist" in _dic and not _dic["is_pack_exist"]:
            _dic["check_flag"] = False
            _dic["check_msg"] = f"服务 {service_name} 的安装包不存在"
            return _dic
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
        # TODO 整体服务间的关键校验
        return result_list


class CreateInstallPlan(object):
    """ 生成部署计划相关数据 """

    def __init__(self, install_data):
        """
        解析安装数据入库方法
        {
            "install_type": 0,
            "use_exist_services": [
                {
                    "name": "a",
                    "id": 1,
                    "type": "cluster",
                    "check_flag": false,
                    "check_msg": "此集群不存在"
                }
            ],
            "install_services": [
                {
                    "name": "jdk",
                    "version": "8u211",
                    "ip": "10.0.9.175",
                    "cluster_name": "test_cluster_1",
                    "product_instance_name": "aa",
                    "app_install_args": [
                        {
                            "name": "安装目录",
                            "key": "base_dir",
                            "default": "/jdk",
                            "dir_key": "{data_path}",
                            "check_flag": false,
                            "check_msg": "无法确定该路径状态: /data/jdk"
                        }
                    ],
                    "app_port": [
                        {
                            "name": "服务端口",
                            "protocol": "TCP",
                            "key": "service_port",
                            "default": 19001,
                            "check_flag": false,
                            "check_msg": "主机 10.0.9.175 上的端口 19001 已被占用"
                        }
                    ],
                    "service_instance_name": "jdk-1-1"
                }
            ],
            "is_valid_flag": false,
            "is_valid_msg": "数据校验出错"
        }
        :param install_data: 安装解析数据
        :type install_data: dict
        """
        self.install_data = install_data
        self.install_type = install_data["install_type"]
        self.install_services = install_data["install_services"]

    def get_app_obj_for_service(self, dic):     # NOQA
        """
        获取服务实例表中关联的app对象
        :param dic: 服务数据
        :type dic: dict
        :return:
        """
        return ApplicationHub.objects.filter(
            app_name=dic["name"], app_version=dic["version"]
        ).last()

    def get_app_port_for_service(self, dic):    # NOQA
        """
        获取服务实例上设置的端口信息
        :param dic: 服务数据
        :type dic: dict
        :return:
        """
        return json.dumps(dic["app_port"]) if dic["app_port"] else None

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
        install_args = dic["app_install_args"]
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

    def create_connect_info(self, dic):     # NOQA
        """
        创建或获取服务的用户名、密码信息
        :param dic: 服务数据
        :type dic: dict
        :return:
        """
        username = password = username_enc = password_enc = ""
        for item in dic["app_install_args"]:
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
            service_instance_name=dic["service_instance_name"],
            service=self.get_app_obj_for_service(dic),
            service_port=self.get_app_port_for_service(dic),
            service_controllers=self.get_controllers_for_service(dic),
            cluster=self.create_cluster(dic),
            env=self.get_env_for_service(),
            service_status=6,
            service_connect_info=self.create_connect_info(dic)
        )
        _ser_obj.save()
        return _ser_obj

    def create_product_instance(self, dic):     # NOQA
        """
        创建产品实例
        :param dic: 服务数据
        :type dic: dict
        :return:
        """
        if "product_instance_name" not in dic or \
                not self.get_app_obj_for_service(dic):
            return
        product_instance_name = dic["product_instance_name"]
        Product.objects.get_or_create(
            product_instance_name=product_instance_name,
            product=self.get_app_obj_for_service(dic).product
        )

    def check_if_has_post_action(self, ser):    # NOQA
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

    def run(self):
        """
        服务部署信息入库操作
        :return:
        """
        with transaction.atomic():
            try:
                # step0: 生成
                # step1: 生成操作唯一uuid，创建主安装记录
                operation_uuid = str(uuid.uuid4())
                main_obj = MainInstallHistory(
                    operation_uuid=operation_uuid,
                    install_status=0,
                    install_args=self.install_data
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
                _json_obj = DataJson(operation_uuid=operation_uuid)
                _json_obj.run()
                # 调用安装异步任务，并回写异步任务到
                task_id = install_service.delay(main_obj.id)
                MainInstallHistory.objects.filter(id=main_obj.id).update(
                    task_id=task_id
                )
            except Exception as e:
                return False, f"生成部署计划失败: {str(e)}"
        return True, operation_uuid
