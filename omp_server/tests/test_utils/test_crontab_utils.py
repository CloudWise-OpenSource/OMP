# -*- coding: utf-8 -*-
# Project: test_crontab_utils
# Author: jon.liu@yunzhihui.com
# Create time: 2021-10-15 21:18
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
定时任务单元测试代码
"""

import uuid

from django_celery_beat.models import PeriodicTask

from tests.base import BaseTest
from utils.plugin.crontab_utils import CrontabUtils


class CrontabUtilTest(BaseTest):
    def setUp(self):
        super(CrontabUtilTest, self).setUp()
        self.task_dic = {
            "task_name": str(uuid.uuid4()),
            "task_func": "test.test.func",
            "task_args": (1, ),
            "task_kwargs": {"test": "a"},
            "task_timeout": None
        }

    def test_create_crontab_job(self):
        cron_obj = CrontabUtils(**self.task_dic)
        flag, msg = cron_obj.create_crontab_job()
        self.assertEqual(flag, True)
        is_exist = PeriodicTask.objects.filter(
            name=self.task_dic.get("task_name")).exists()
        self.assertEqual(is_exist, True)
        flag, msg = cron_obj.create_crontab_job()
        self.assertEqual(flag, False)
        flag, msg = cron_obj.delete_job()
        self.assertEqual(flag, True)
        flag, msg = cron_obj.delete_job()
        self.assertEqual(flag, False)

    def test_create_internal_job(self):
        cron_obj = CrontabUtils(**self.task_dic)
        flag, msg = cron_obj.create_internal_job(10)
        self.assertEqual(flag, True)
        is_exist = PeriodicTask.objects.filter(
            name=self.task_dic.get("task_name")).exists()
        self.assertEqual(is_exist, True)
        flag, msg = cron_obj.create_internal_job(10)
        self.assertEqual(flag, False)

    def test_create_internal_failed(self):
        cron_obj = CrontabUtils(**self.task_dic)
        flag, msg = cron_obj.create_internal_job("test")
        self.assertEqual(flag, False)
        flag, msg = cron_obj.create_internal_job(10, "test")
        self.assertEqual(flag, False)
