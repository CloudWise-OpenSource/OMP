# -*- coding: utf-8 -*-
# Project: crontab_utils
# Author: jon.liu@yunzhihui.com
# Create time: 2021-10-14 11:35
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
定时周期性任务设置方法
"""

import json
import pytz
from copy import deepcopy


from django_celery_beat.models import PeriodicTask
from django_celery_beat.models import CrontabSchedule
from django_celery_beat.models import IntervalSchedule
from django.core.exceptions import ObjectDoesNotExist

from omp_server.settings import TIME_ZONE


class CrontabUtils(object):
    """ 定时、周期性任务创建工具 """

    def __init__(
            self, task_name=None, task_func="",
            task_args=None, task_kwargs=None, task_timeout=None):
        """
        定时任务初始化方法
        :param task_name: 任务名称，全局唯一
        :param task_func: 任务执行方法
        :param task_args: 任务执行位置参数
        :param task_kwargs: 任务执行关键字参数
        :param task_timeout: 任务超时时间(暂时未定)
        """
        self.task_name = task_name
        self.task_func = task_func
        self.task_args = task_args if task_args else ()
        self.task_kwargs = task_kwargs if task_kwargs else {}
        self.task_time = task_timeout
        self.create_task_obj_dic = {
            "name": self.task_name,
            "task": self.task_func,
            "args": json.dumps(self.task_args),
            "kwargs": json.dumps(self.task_kwargs)
        }

    def create_crontab_job(
            self, minute="*", hour="*", day_of_month="*",
            month_of_year="*", day_of_week="*", job_timezone=TIME_ZONE):
        """
        创建定时任务
        如果定时任务正在执行，但是在指定频率内未完成，那么新任务仍能下发
        :param minute: 分钟
        :param hour: 小时
        :param day_of_month: 每月的第几天
        :param month_of_year: 每年的第几个月
        :param day_of_week: 每周的第几天
        :param job_timezone: 时区
        :return: (flag, msg)
        """
        if self.check_task_exist():
            return False, f"{self.task_name} already exist!"
        _schedule, _created = CrontabSchedule.objects.get_or_create(
            minute=minute,
            hour=hour,
            day_of_week=day_of_week,
            day_of_month=day_of_month,
            month_of_year=month_of_year,
            timezone=pytz.timezone(job_timezone)
        )
        _dic = deepcopy(self.create_task_obj_dic)
        _dic.update({"crontab": _schedule})
        job_obj = PeriodicTask.objects.create(**_dic)
        return True, job_obj.name

    def create_internal_job(self, num, unit_type="minutes"):
        """
        创建周期性任务
        周期类型有
            DAYS = DAYS
            HOURS = HOURS
            MINUTES = MINUTES
            SECONDS = SECONDS
        :param num: 周期时长
        :param unit_type: 周期类型
        :return:
        """
        if self.check_task_exist():
            return False, f"{self.task_name} already exist!"
        if not num or not isinstance(num, int):
            return False, "num must be integer"
        period = getattr(IntervalSchedule, unit_type.upper(), None)
        if not period:
            return False, "unit_type must be one of DAYS/HOURS/MINUTES/SECONDS"
        _schedule, _created = IntervalSchedule.objects.get_or_create(
            every=10,
            period=IntervalSchedule.SECONDS
        )
        _dic = deepcopy(self.create_task_obj_dic)
        _dic.update({"interval": _schedule})
        job_obj = PeriodicTask.objects.create(**_dic)
        return True, job_obj.name

    def check_task_exist(self):
        """
        检查task是否存在，从task name来
        :return:
        """
        return PeriodicTask.objects.filter(name=self.task_name).exists()

    def delete_job(self):
        """
        删除定时任务
        :return:
        """
        try:
            PeriodicTask.objects.get(name=self.task_name).delete()
            return True, "success"
        except ObjectDoesNotExist:
            return False, f"{self.task_name} not exists!"
