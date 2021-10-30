# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/10/28 4:59 下午
# Description:
from tests.base import AutoLoginTest
from rest_framework.reverse import reverse
from tests.test_inspection.inspection_mixin import InspectionHistoryMixin


class TestInspectionHistoryList(AutoLoginTest, InspectionHistoryMixin):
    def setUp(self):
        super(TestInspectionHistoryList, self).setUp()
        self.env = self.create_default_env()

    def tearDown(self):
        super(TestInspectionHistoryList, self).tearDown()

    def test_history_list(self):
        # 未找到
        resp = self.get(reverse("history-list")).json()
        self.assertDictEqual(resp, {
            'code': 0,
            'message': 'success',
            'data': {'count': 0, 'next': None, 'previous': None, 'results': []}
        })

        # 查询成功
        self.get_inspection_history(self.env)
        resp = self.get(reverse("history-list")).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertTrue(resp.get("data") is not None)

    def test_history_post(self):
        # 深度巡检
        data = {'env': 1,
                'execute_type': "man",
                'hosts': {},
                'inspection_name': "深度巡检",
                'inspection_operator': "admin",
                'inspection_status': '1',
                'inspection_type': "deep",
                'services': {}}
        resp = self.post(reverse("history-create"), data=data)
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertTrue(resp.get("data") is not None)

        # 主机巡检
        data = {'env': 1,
                'execute_type': "man",
                'hosts': ["10.0.9.67"],
                'inspection_name': "主机巡检",
                'inspection_operator': "admin",
                'inspection_status': '1',
                'inspection_type': "host",
                'services': {}}
        resp = self.post(reverse("history-create"), data=data)
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertTrue(resp.get("data") is not None)

        # 组件巡检
        data = {'env': 1,
                'execute_type': "man",
                'hosts': {},
                'inspection_name': "组件巡检",
                'inspection_operator': "admin",
                'inspection_status': '1',
                'inspection_type': "service",
                'services': [8]}
        resp = self.post(reverse("history-create"), data=data)
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertTrue(resp.get("data") is not None)
