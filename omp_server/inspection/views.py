# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/10/13 6:06 下午
# Description: 巡检视图

from rest_framework import status
from rest_framework.response import Response
from utils.common.paginations import PageNumberPager
from rest_framework.viewsets import GenericViewSet
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework.mixins import (
    ListModelMixin, CreateModelMixin, UpdateModelMixin, RetrieveModelMixin)
from db_models.models import Env
from utils.plugin.crontab_utils import CrontabUtils
from inspection.tasks import get_prometheus_host_data
from inspection.models import (
    InspectionHistory, InspectionCrontab, InspectionReport)
from inspection.filters import (
    InspectionHistoryFilter, InspectionCrontabFilter, InspectionReportFilter)
from inspection.serializers import (
    InspectionHistorySerializer, InspectionCrontabSerializer,
    InspectionReportSerializer)


class InspectionHistoryView(ListModelMixin, GenericViewSet, CreateModelMixin):
    """
        list:  查询巡检记录历史记录列表
    """
    queryset = InspectionHistory.objects.all()
    serializer_class = InspectionHistorySerializer
    pagination_class = PageNumberPager
    # 过滤字段
    filter_backends = (DjangoFilterBackend,)
    filter_class = InspectionHistoryFilter
    # 操作描述信息
    get_description = "查询巡检历史记录列表"

    def create(self, request, *args, **kwargs):
        data_dict = request.data
        # 一、创建巡检历史表数据
        env_obj = Env.objects.filter(id=data_dict['env']).first()
        data_dict['env'] = env_obj
        his_obj = InspectionHistory(**data_dict)
        his_obj.save()
        # 二、创建巡检记录历史表关联的报告表的数据
        rep_dict = {'inst_id': his_obj}
        rep_obj = InspectionReport(**rep_dict)
        rep_obj.save()
        # 三、手动序列化数据，不是json的不能response
        data_dict.update({'id': his_obj.id, 'env': data_dict['env'].id})
        # 四、下发celery异步任务
        # target为实例方法，目的是统一执行实例方法并统一返回值
        target = ['rate_cpu', 'rate_memory', 'rate_max_disk',
                  'rate_exchange_disk', 'run_time', 'avg_load',
                  'total_file_descriptor', 'rate_io_wait',
                  'network_bytes_total', 'disk_io']
        get_prometheus_host_data(
            env=env_obj.name, hosts=his_obj.hosts,
            history_id=his_obj.id, report_id=rep_obj.id, target=target)
        return Response(data_dict, status=status.HTTP_200_OK)


class InspectionCrontabView(RetrieveModelMixin, ListModelMixin, GenericViewSet,
                            CreateModelMixin, UpdateModelMixin):
    """
        list: 查询巡检任务列表
        create: 创建一个新巡检任务
        update: 更新一个现有巡检任务
    """
    queryset = InspectionCrontab.objects.all()
    serializer_class = InspectionCrontabSerializer
    pagination_class = PageNumberPager
    # 过滤字段
    lookup_field = 'job_type'
    filter_backends = (DjangoFilterBackend,)
    filter_class = InspectionCrontabFilter
    # 操作描述信息
    get_description = "查询巡检任务配置列表"
    post_description = "新建巡检任务配置列表"
    put_description = "更新巡检任务配置列表"

    def create(self, request, *args, **kwargs):
        # 判断是否需要下发任务到celery：0-开启，1-关闭
        is_success = True
        if request.data.get('is_start_crontab') == 0:
            task_name = 'inspection_cron_task'
            task_func = 'inspection.tasks.inspection_crontab'
            cron_obj = CrontabUtils(task_name=task_name, task_func=task_func,
                                    task_kwargs=request.data)
            cron_args = {
                'minute': request.data.get('crontab_detail').get('minute'),
                'hour': request.data.get('crontab_detail').get('hour'),
                'day_of_month': request.data.get('crontab_detail').get('day'),
                'month_of_year':
                    request.data.get('crontab_detail').get('month'),
                'day_of_week':
                    request.data.get('crontab_detail').get('day_of_week')
            }
            is_success, job_name = cron_obj.create_crontab_job(**cron_args)
        else:
            pass

        if is_success:
            # 只是想在增加时加个判断及对应操作，增加还是执行父类的create
            return CreateModelMixin.create(self, request, *args, **kwargs)
        else:
            return Response(data={'code': 500, 'message': '定时任务创建失败，请勿重复操作'},
                            status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        # 判断是否需要下发任务到celery：0-开启，1-关闭
        is_success = True
        if request.data.get('is_start_crontab') == 0:
            task_name = 'inspection_cron_task'
            task_func = 'inspection.tasks.inspection_crontab'
            cron_obj = CrontabUtils(task_name=task_name, task_func=task_func,
                                    task_kwargs=request.data)
            cron_args = {
                'minute': request.data.get('crontab_detail').get('minute'),
                'hour': request.data.get('crontab_detail').get('hour'),
                'day_of_month': request.data.get('crontab_detail').get('day'),
                'month_of_year':
                    request.data.get('crontab_detail').get('month'),
                'day_of_week':
                    request.data.get('crontab_detail').get('day_of_week')
            }
            # 删除定时任务
            cron_obj.delete_job()
            # 增加定时任务
            is_success, job_name = cron_obj.create_crontab_job(**cron_args)
        else:
            pass

        if is_success:
            # 只是想在修改时加个判断及对应操作，修改还是执行父类的update
            return UpdateModelMixin.update(self, request, *args, **kwargs)
        else:
            return Response(data={'code': 500, 'message': '定时任务修改失败，请重试'},
                            status=status.HTTP_200_OK)


class InspectionReportView(GenericViewSet, RetrieveModelMixin):
    """
        list: 查询巡检报告列表
    """
    queryset = InspectionReport.objects.all()
    serializer_class = InspectionReportSerializer
    # 过滤字段
    lookup_field = 'inst_id'
    # filter_backends = (DjangoFilterBackend,)
    # filter_class = InspectionReportFilter
    # 操作描述信息
    get_description = "查询巡检任务配置列表"
