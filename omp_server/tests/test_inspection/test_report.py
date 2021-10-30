# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/10/28 4:59 下午
# Description:
from tests.base import AutoLoginTest
from rest_framework.reverse import reverse
from tests.test_inspection.inspection_mixin import InspectionReportMixin


class TestInspectionReportList(AutoLoginTest, InspectionReportMixin):
    def setUp(self):
        super(TestInspectionReportList, self).setUp()
        self.env = self.create_default_env()

    def tearDown(self):
        super(TestInspectionReportList, self).tearDown()

    def test_crontab_read(self):
        inst_id = self.create_inspection_report(self.env)
        self.update_inspection_report(inst_id=inst_id)
        resp = self.get(
            f"/api/inspection/report/{inst_id}/", data={'inst_id': inst_id}
        ).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertTrue(resp.get("data") is not None)
