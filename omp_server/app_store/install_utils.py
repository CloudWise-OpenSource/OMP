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
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor

from omp_server.settings import PROJECT_DIR
from db_models.models import (
    ApplicationHub,
    ProductHub,
    Product,
    Service,
    ClusterInfo
)
from utils.common.exceptions import GeneralError


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


class SerDependenceParseUtils(object):
    """
    依赖解决工具类
    """

    def __init__(self, parse_name, parse_version):
        """
        初始化对象, 服务级别的解析，包含自研服务和基础组件服务
        :param parse_name: 要解析的名称，服务
        :param parse_version: 要解析的版本
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
                inner["is_in_hub"] = False
                inner["is_pack_exist"] = False
                inner["ser_deploy_mode"] = list()
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
            inner["is_in_hub"] = True
            inner["is_pack_exist"] = is_pack_exist
            inner["ser_deploy_mode"] = self.get_deploy_mode(obj=_app)
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
        :param dep: 服务依赖关系列表
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
        """ 解析服务级别的依赖关系 """
        ser = SerDependenceParseUtils(obj.app_name, obj.app_version)
        return ser.run_ser()

    def get_app_port(self, obj):    # NOQA
        """ 获取app的端口 """
        if not obj.app_port:
            return []
        return json.loads(obj.app_port)

    def get_app_install_args(self, obj):  # NOQA
        """ 解析安装参数信息
        [
          {
            "default": 18080,
            "key": "http_port",
            "name": "服务端口"
          }
        ]
        """
        ret_lst = list()
        # 标记安装过程中涉及到的数据目录，通过此标记给前端
        # 给与前端提示信息，此标记对应于主机中的数据目录 data_folder
        # 在后续前端提供出安装参数后，我们应该检查其准确性
        DIR_KEY = "{data_path}"
        # TODO 暂时屏蔽拼接服务端口配置信息
        # if obj.app_port:
        #     ret_lst.extend(json.loads(obj.app_port))
        if obj.app_install_args:
            ret_lst.extend(json.loads(obj.app_install_args))
        for item in ret_lst:
            if isinstance(item.get("default"), str) and \
                    DIR_KEY in item.get("default"):
                item["default"] = item["default"].replace(DIR_KEY, "")
                item["dir_key"] = DIR_KEY
        return ret_lst

    def get_deploy_mode(self, obj):  # NOQA
        """ 解析部署模式信息
        [
          {
            "key": "single",
            "name": "单实例"
          }
        ]
        """
        # 如果服务未配置部署模式相关信息，那么默认为单实例模式
        ser = SerDependenceParseUtils(obj.app_name, obj.app_version)
        return ser.get_deploy_mode(obj)

    def _process_continue_parse(self, obj):  # NOQA
        """ 解析是否能够进行的核心接口 """
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
        """ 解析能否继续进行的标志接口 """
        flag, _ = self._process_continue_parse(obj)
        return flag

    def get_process_message(self, obj):    # NOQA
        """ 解析能否继续进行的信息接口 """
        _, msg = self._process_continue_parse(obj)
        return msg


class ValidateExistService(object):
    """ 检查已存在服务信息是否准确 """

    def __init__(self, data=None):
        """
        初始化方法
        :param data: 要被检验的服务信息
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
        if ClusterInfo.objects.filter(
                id=dic.get("id"),
                cluster_name=dic.get("cluster_name")
        ).exists():
            return True
        return False

    def check_single(self, dic):    # NOQA
        """
        检查服务的合法性
        :param dic: 服务信息字典
        :type dic: dict
        :return:
        """
        if Service.objects.filter(
            id=dic.get("id"),
            service_instance_name=dic.get("service_instance_name")
        ).exists():
            return True
        return False

    def run(self):
        """
        运行入口
        :return:
        """
        for item in self.data:
            _type = item.get("type")
            if _type not in ("cluster", "single"):
                return False
            flag = getattr(self, f"check_{_type}")(item)
            if not flag:
                return False
        return True


class ValidateInstallService(object):
    """ 检查要安装的服务信息是否准确 """

    def __init__(self, data=None):
        """
        初始化方法
        :param data: 要被检验的服务信息
        """
        if not data or not isinstance(data, list):
            raise GeneralError(
                "ValidateInstallService __init__ arg error: data"
            )
        self.data = data

    def check_single_service(self, dic):    # NOQA
        """
        检查单个服务的安装信息
        :param dic: 服务安装信息
        :type dic: dict
        :return:
        """
        _dic = deepcopy(dic)
        _dic["error_dic"] = dict()
        # 检查实例名称是否重复
        service_instance_name = _dic.get("service_instance_name")
        if Service.objects.filter(
                service_instance_name=service_instance_name).exists():
            _dic["error_dic"]["service_instance_name"] = "实例名称重复"
        # app_install_args = _dic.get("app_install_args", [])

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
        error_flag = False
        for el in result_list:
            if not el.get("check_flag"):
                error_flag = True
        if error_flag:
            return False, result_list
        return True, result_list
