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

from rest_framework.reverse import reverse

from db_models.models import (
    ApplicationHub,
)
from tests.base import AutoLoginTest
from tests.mixin import ApplicationResourceMixin


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

    def make_unique_data(self, dic):    # NOQA
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
        self.make_unique_data(app_base_1)

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
        self.make_unique_data(app_base_2)

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
        self.make_unique_data(app_base_3)

    def make_unrelease_app(self):
        app_base_4 = {
            "app_name": "test_app4",
            "app_version": "1.0",
            "is_release": "0",
            "app_dependence": json.dumps(
                [{"name": "test_app1", "version": "1.0"}]
            ),
            "extend_fields": {}
        }
        self.make_unique_data(app_base_4)

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
