# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/10/28 4:59 下午
# Description:
from tests.base import AutoLoginTest
from rest_framework.reverse import reverse
from tests.test_inspection.inspection_mixin import InspectionHistoryMixin


class TestInspectionCrontabList(AutoLoginTest, InspectionHistoryMixin):
    def setUp(self):
        super(TestInspectionCrontabList, self).setUp()
        self.env = self.create_default_env()

    def tearDown(self):
        super(TestInspectionCrontabList, self).tearDown()

    def test_crontab_read(self):
        _ = self.create_inspection_crontab(self.env)
        resp = self.get(
            f"{reverse('crontab-list')}0/", data={'job_type': 0}).json()
        self.assertEqual(_.id, resp.get('data').get('id'))

    def test_crontab_create(self):
        _ = {'crontab_detail': {'hour': "09", 'minute': "41", 'month': "*",
                                'day_of_week': "1", 'day': "*"},
             'env': self.env,
             'is_start_crontab': 0,
             'job_name': "深度分析",
             'job_type': 0}
        resp = self.post(reverse("crontab-list"), data=_).json()
        _obj = self.get_inspection_crontab()
        self.assertEqual(_obj.id, resp.get('data').get('id'))

    def test_crontab_update(self):
        _ = {'env': self.env, 'is_start_crontab': 0, 'job_name': "深度分析",
             'job_type': 0,
             'crontab_detail': {'hour': "09", 'minute': "41", 'month': "*",
                                'day_of_week': "1", 'day': "*"}
             }
        resp_add = self.post(reverse("crontab-list"), data=_).json()
        self.assertEqual(resp_add.get("code"), 0)
        self.assertEqual(resp_add.get("message"), "success")
        self.assertTrue(resp_add.get("data") is not None)

        _ = {'crontab_detail': {'hour': "10", 'minute': "41", 'month': "*",
                                'day_of_week': "1", 'day': "*"},
             'env': 1,
             'is_start_crontab': 0,
             'job_name': "深度分析2",
             'job_type': 0}
        resp_upd = self.put(
            f"{reverse('crontab-list')}0/?job_type=0", data=_).json()
        self.assertEqual(resp_upd.get('data').get('job_name'), "深度分析2")
