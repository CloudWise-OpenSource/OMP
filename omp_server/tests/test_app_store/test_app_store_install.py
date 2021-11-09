# -*- coding: utf-8 -*-
# Project: test_app_store_install
# Author: jon.liu@yunzhihui.com
# Create time: 2021-10-23 09:05
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
组件、应用安装入口使用的解析方法测试
"""

import json
import datetime
import os
from unittest import mock

from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from django.test import TransactionTestCase

from db_models.models import (
    ApplicationHub, ProductHub, UploadPackageHistory, Host,
    Env, UserProfile
)
from omp_server.settings import PROJECT_DIR
from app_store.tasks import install_service
from utils.plugin.salt_client import SaltClient
from tests.base import AutoLoginTest
from tests.mixin import (
    ApplicationResourceMixin,
    ProductResourceMixin
)


class ComponentEntranceTest(AutoLoginTest, ApplicationResourceMixin):
    def setUp(self):
        super(ComponentEntranceTest, self).setUp()
        self.componentEntrance_url = reverse(
            "componentEntrance-list")

    def test_null_ret_success(self):
        res = self.get(self.componentEntrance_url).json()
        self.assertDictEqual(
            res,
            {'code': 0, 'message': 'success', 'data': []}
        )

    def test_normal_res(self):
        self.get_application()
        res = self.get(self.componentEntrance_url).json()
        self.assertEqual(res.get("code"), 0)
        self.assertEqual(len(res.get("data", [])) != 0, True)
        self.destroy_application()
        self.destroy_labels()

    def make_unique_app_data(self, dic):  # NOQA
        obj_dic = {
            "is_release": 1,
            "app_type": 0,
            "app_logo": "app log svg data...",
            "app_description": "应用描述，省略一万字...",
            "app_port": json.dumps(
                [{"default": 18080, "key": "http_port", "name": "服务端口"}]
            ),
            "app_install_args": json.dumps(
                [
                    {"name": "安装目录", "key": "install_dir",
                     "default": "{data_path}/abc"},
                    {"name": "数据目录", "key": "data_dir",
                     "default": "{data_path}/data/test_app1"}
                ]
            )
        }
        obj_dic.update(dic)
        ApplicationHub(**obj_dic).save()

    def destroy_app(self):  # NOQA
        ApplicationHub.objects.filter(app_name__icontains="test_app").delete()

    def make_base_app_1(self):  # NOQA
        app_base_1 = {
            "app_name": "test_app1",
            "app_version": "8u211",
            "extend_fields": {"base_env": True}
        }
        self.make_unique_app_data(app_base_1)

    def make_base_app_2(self):  # NOQA
        app_base_2 = {
            "app_name": "test_app2",
            "app_version": "1.0",
            "app_dependence": json.dumps(
                [{"name": "test_app1", "version": "8u211"}]
            ),
            "extend_fields": {
                "deploy": {
                    "single": [{"key": "single", "name": "单实例"}],
                    "complex": [{"key": "master_slave", "name": "主从模式",
                                 "nodes": {"step": 1, "start": 2}}]
                },
            }
        }
        self.make_unique_app_data(app_base_2)

    def make_base_app_3(self):  # NOQA
        app_base_3 = {
            "app_name": "test_app3",
            "app_version": "1.0",
            "app_dependence": json.dumps(
                [
                    {"name": "test_app2", "version": "1.0"},
                    {"name": "test_app4", "version": "1.0"}
                ]
            ),
            "extend_fields": {}
        }
        self.make_unique_app_data(app_base_3)

    def make_unrelease_app(self):  # NOQA
        app_base_4 = {
            "app_name": "test_app4",
            "app_version": "1.0",
            "is_release": "0",
            "app_dependence": json.dumps(
                [{"name": "test_app1", "version": "1.0"}]
            ),
            "extend_fields": {}
        }
        self.make_unique_app_data(app_base_4)

    def test_dependence_one_level(self):
        """ 一层依赖信息单元测试 """
        self.make_base_app_1()
        self.make_base_app_2()
        res = self.get(self.componentEntrance_url).json()
        self.assertEqual(res.get("code"), 0)
        self.assertEqual(len(res.get("data")), 2)
        for item in res.get("data"):
            if item.get("app_name") == "test_app2":
                self.assertEqual(len(item.get("app_dependence")), 1)
        self.destroy_app()

    def test_dependence_two_level(self):
        """ 二层依赖信息单元测试 """
        self.make_base_app_1()
        self.make_base_app_2()
        self.make_base_app_3()
        res = self.get(self.componentEntrance_url).json()
        self.assertEqual(res.get("code"), 0)
        self.assertEqual(len(res.get("data")), 3)
        for item in res.get("data"):
            if item.get("app_name") == "test_app3":
                self.assertEqual(len(item.get("app_dependence")), 3)
        self.destroy_app()

    def test_no_release_app_dependence(self):
        """ 测试缺少服务依赖信息场景 """
        self.make_base_app_1()
        self.make_base_app_2()
        self.make_base_app_3()
        self.make_unrelease_app()
        res = self.get(self.componentEntrance_url).json()
        process_continue = True
        for item in res.get("data"):
            for el in item.get("app_dependence"):
                if not el.get("process_continue"):
                    process_continue = False
        self.assertEqual(process_continue, False)


class ProductEntranceTest(ComponentEntranceTest, ProductResourceMixin):

    def setUp(self):
        super(ProductEntranceTest, self).setUp()
        self.productEntrance_url = reverse(
            "productEntrance-list")

    def test_normal_res(self):
        self.get_application()
        self.get_product()
        res = self.get(self.productEntrance_url).json()
        self.assertEqual(res.get("code"), 0)
        self.assertEqual(len(res.get("data", [])) != 0, True)
        self.destroy_application()
        self.destroy_labels()
        self.destroy_product()

    def make_pro_1(self):  # NOQA
        """
        创建不依赖其他应用的应用，应用下具备2个服务
        :return:
        """
        # 创建产品下的服务
        test_pro_ser_1 = {
            "app_name": "test_pro_ser_1",
            "app_version": "1.0",
            "app_dependence": json.dumps(
                [{"name": "test_app1", "version": "8u211"}]
            )
        }
        self.make_unique_app_data(test_pro_ser_1)
        test_pro_ser_2 = {
            "app_name": "test_pro_ser_2",
            "app_version": "1.0",
            "app_dependence": json.dumps(
                [{"name": "test_app1", "version": "8u211"}]
            )
        }
        self.make_unique_app_data(test_pro_ser_2)
        pro_dic = {
            "is_release": 1,
            "pro_name": "test_pro_1",
            "pro_version": "1.0",
            "pro_dependence": json.dumps([
                {"name": "test_pro_2", "version": "1.0"},
                {"name": "test_pro_30", "version": "1.0"},
            ]),
            "pro_services": json.dumps([
                {"name": "test_pro_ser_1", "version": "1.0"},
                {"name": "test_pro_ser_2", "version": "1.0"}
            ])
        }
        ProductHub(**pro_dic).save()

    def make_pro_2(self):  # NOQA
        pro_dic = {
            "is_release": 1,
            "pro_name": "test_pro_2",
            "pro_version": "1.2",
            "pro_dependence": json.dumps([
                {"name": "test_pro_1", "version": "1.0"},
                {"name": "test_pro_2", "version": "1.0"},
            ]),
            "pro_services": json.dumps([
                {"name": "test_pro_ser_3", "version": "2.0"},
                {"name": "test_pro_ser_4", "version": "2.0"},
                {"name": "test_pro_ser_5", "version": "3.0"},
            ])
        }
        ProductHub(**pro_dic).save()

    def make_pro_3(self):  # NOQA
        pro_dic = {
            "is_release": 1,
            "pro_name": "test_pro_3",
            "pro_version": "1.2",
            "pro_dependence": json.dumps([
                {"name": "test_pro_1", "version": "1.0"},
            ]),
            "pro_services": json.dumps([
                {"name": "test_pro_ser_3", "version": "2.0"},
                {"name": "test_pro_ser_4", "version": "2.0"},
                {"name": "test_pro_ser_5", "version": "3.0"},
            ])
        }
        ProductHub(**pro_dic).save()

    def test_pro_component_dependence(self):
        self.make_pro_1()
        res = self.get(self.productEntrance_url).json()
        self.assertEqual(res.get("code"), 0)

    def test_pro_pro_dependence(self):
        """ 测试产品间有依赖场景 """
        self.make_pro_1()
        self.make_pro_2()
        self.make_pro_3()
        res = self.get(self.productEntrance_url).json()
        self.assertEqual(res.get("code"), 0)


def create_host():
    """
    创建测试使用主机
    :return:
    """
    env = Env(name="default")
    env.save()
    test_host = {
        'created': datetime.datetime(2021, 10, 26, 17, 59, 45, 248976),
        'modified': datetime.datetime(2021, 10, 26, 17, 59, 45, 553447),
        'is_deleted': False,
        'instance_name': '127.0.0.1',
        'ip': '127.0.0.1',
        'port': 22,
        'username': 'root',
        'password': 'lEJBI-Pt8Ih321eaawzf1kHj8YvMTRpMYnNFD2YS7MA',
        'data_folder': '/data',
        'service_num': 0,
        'alert_num': 0,
        'operate_system': 'CentOS',
        'host_name': None,
        'memory': None,
        'cpu': None,
        'disk': None,
        'host_agent': '0',
        'monitor_agent': '4',
        'host_agent_error': None,
        'monitor_agent_error': '',
        'is_maintenance': False,
        'agent_dir': '/data',
        'env': env
    }
    Host(**test_host).save()


def create_base_app():
    """
    创建安装过程中使用的app
    :return:
    """
    test_app_1_upload_history = {
        'created': datetime.datetime(2021, 10, 25, 10, 39, 59, 239807),
        'modified': datetime.datetime(2021, 10, 25, 10, 40, 7, 191114),
        'is_deleted': False,
        'operation_uuid': '1635129600184',
        'operation_user': 'admin',
        'package_name': 'testApp-1.0.1-35144e57a59d774869ccc218539db8c7.tar.gz',
        'package_md5': '35144e57a59d774869ccc218539db8c7',
        'package_path': 'verified',
        'package_status': 3,
        'error_msg': None,
        'package_parent_id': None
    }

    test_app_1_application_hub = {
        'created': datetime.datetime(2021, 10, 25, 10, 40, 29, 981060),
        'modified': datetime.datetime(2021, 10, 25, 10, 40, 29, 988651),
        'is_release': True,
        'app_type': 0,
        'app_name': 'testApp',
        'app_version': '1.0.1',
        'app_description': 'Java Development Kit (JDK) 是Sun公司（已被Oracle收购）'
                           '针对Java开发员的软件开发工具包'
                           'Java SDK（Software development kit）。',
        'app_port': json.dumps([
            {"default": 8080, "key": "http_port", "name": "业务端口"},
            {"default": 8081, "key": "metric_port", "name": "监控端口"}
        ]),
        'app_dependence': None,
        'app_install_args': json.dumps([
            {"name": "安装目录", "key": "base_dir", "default": "{data_path}/jdk"},
            {"name": "数据目录", "key": "data_dir",
             "default": "{data_path}/data/jdk"},
            {"name": "日志目录", "key": "log_dir",
             "default": "{data_path}/log/jdk"},
            {"name": "用户名", "key": "username", "default": "jon"},
            {"name": "密码", "key": "password", "default": "jon_password"},
        ]),
        'app_controllers': json.dumps(
            {
                "start": "./bin/testApp start",
                "stop": "./bin/testApp stop",
                "restart": "./bin/testApp restart",
                "reload": "./bin/testApp reload",
                "install": "./scripts/install.py",
                "init": ""
            }
        ),
        'app_package_id': 1,
        'product_id': None,
        'app_logo': None,
        'extend_fields': {
            'deploy': {
                "single": [{"name": "单实例", "key": "single"}],
                "complex": [{"name": "主从模式", "key": "master_slave"}]
            },
            'monitor': None,
            'base_env': True,
            'resources': None,
            'auto_launch': False
        }
    }

    up_obj = UploadPackageHistory(**test_app_1_upload_history)
    up_obj.save()

    test_app_1_application_hub["app_package_id"] = up_obj.id
    app_obj = ApplicationHub(**test_app_1_application_hub)
    app_obj.save()


class ExecuteInstallTest(TransactionTestCase):
    def setUp(self):
        super(ExecuteInstallTest, self).setUp()
        self.executeInstall_url = reverse(
            "executeInstall-list")
        create_host()
        create_base_app()
        user = UserProfile.objects.create(username="admin")
        self.client = APIClient()
        self.client.force_authenticate(user)
        self.test_data = {
            "install_type": 0,
            "use_exist_services": [
            ],
            "install_services": [
                {
                    "name": "testApp",
                    "version": "1.0.1",
                    "ip": "127.0.0.1",
                    "app_install_args": [
                        {"name": "安装目录", "key": "base_dir",
                         "dir_key": "{data_path}", "default": "/jdk"},
                        {"name": "数据目录", "key": "data_dir",
                         "dir_key": "{data_path}", "default": "/data/jdk"},
                        {"name": "日志目录", "key": "log_dir",
                         "dir_key": "{data_path}", "default": "/log/jdk"},
                        {"name": "用户名", "key": "username",
                         "default": "jon"},
                        {"name": "密码", "key": "password",
                         "default": "jon_password"},
                    ],
                    "app_port": [
                        {"default": 8000, "key": "http_port", "name": "业务端口"},
                        {"default": 8081, "key": "metric_port", "name": "监控端口"}
                    ],
                    "service_instance_name": "testApp-jon",
                    "deploy_mode": {
                        "key": "single",
                        "name": "单实例"
                    }
                }
            ]
        }

    @mock.patch.object(SaltClient, "cmd", return_value=(True, "OK"))
    @mock.patch.object(install_service, "delay", return_value=None)
    @mock.patch.object(SaltClient, "cmd", return_value=(False, "OK"))
    # @mock.patch(
    #     "utils.plugin.public_utils.check_ip_port", return_value=(False, ""))
    def test_main_success(self, *args, **kwargs):

        res = self.client.post(
            self.executeInstall_url,
            data=json.dumps(self.test_data),
            content_type="application/json"
        ).json()
        self.assertEqual(res.get("code"), 0)
        # operation_uuid = res.get("data", {}).get("operation_uuid")
        # self.assertTrue(operation_uuid)
        # 删除json文件
        os.system(f"rm -rf {PROJECT_DIR}/package_hub/data_files/*.json")

    @mock.patch.object(SaltClient, "cmd", return_value=(False, ""))
    @mock.patch.object(install_service, "delay", return_value=None)
    # @mock.patch(
    #     "utils.plugin.public_utils.check_ip_port", return_value=(False, ""))
    @mock.patch.object(SaltClient, "cmd", return_value=(False, "OK"))
    def test_failed_path_exist(self, *args, **kwargs):
        res = self.client.post(
            self.executeInstall_url,
            data=json.dumps(self.test_data),
            content_type="application/json"
        ).json()
        self.assertEqual(res.get("code"), 0)
        # 删除json文件
        os.system(f"rm -rf {PROJECT_DIR}/package_hub/data_files/*.json")


class InstallHistoryTest(ExecuteInstallTest):
    def setUp(self):
        super(InstallHistoryTest, self).setUp()
        self.installHistory_url = reverse(
            "installHistory-list")

    def test_success(self):
        self.test_main_success()
        res = self.client.get(self.installHistory_url).json()
        self.assertEqual(res.get("code"), 0)
