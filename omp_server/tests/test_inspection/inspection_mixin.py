# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/10/29 10:26 上午
# Description:
import random
from rest_framework.reverse import reverse
from tests.mixin import ServicesResourceMixin
from db_models.models import InspectionHistory, InspectionCrontab


class InspectionHistoryMixin:
    @staticmethod
    def get_inspection_history(env):
        h_bulk = list()
        inspection_type = ["host", "deep", "service"]
        inspection_status = [1, 2, 3]
        for i in range(12):
            h_dict = {'inspection_name': '深度巡检202110271',
                      'inspection_type': random.choices(inspection_type)[0],
                      'inspection_status': random.choices(inspection_status)[0],
                      'execute_type': 'man', 'inspection_operator': 'admin',
                      'hosts': ["10.0.7.146"], 'env': env}
            h_bulk.append(InspectionHistory(**h_dict))

        InspectionHistory.objects.bulk_create(h_bulk)
        return h_bulk

    @staticmethod
    def create_inspection_crontab(env):
        _ = {'crontab_detail': {'hour': "09", 'minute': "41", 'month': "*",
                                'day_of_week': "*", 'day': "*"},
             'env': env,
             'is_start_crontab': 0,
             'job_name': "深度分析",
             'job_type': 0}
        return InspectionCrontab.objects.create(**_)

    @staticmethod
    def update_inspection_crontab():
        _ = {'crontab_detail': {'hour': "09", 'minute': "41", 'month': "*",
                                'day_of_week': "*", 'day': "*"},
             'env': 1,
             'is_start_crontab': 0,
             'job_name': "深度分析",
             'job_type': 0}
        InspectionCrontab.objects.filter(job_type=_.get('job_type')).update(**_)

    @staticmethod
    def get_inspection_crontab():
        _ = InspectionCrontab.objects.filter(job_type=0).first()
        return _
