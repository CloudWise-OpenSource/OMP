# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/10/13 6:06 下午
# Description: 巡检视图
import datetime
import logging
import traceback

from django.core.validators import EmailValidator
from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from inspection.inspection_utils import send_report_email
from utils.common.paginations import PageNumberPager
from rest_framework.viewsets import GenericViewSet
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework.mixins import (
    ListModelMixin, CreateModelMixin, UpdateModelMixin, RetrieveModelMixin)
from utils.plugin.crontab_utils import CrontabUtils
from inspection.tasks import get_prometheus_data
from db_models.models import (
    Env, Service, InspectionHistory, InspectionCrontab, InspectionReport, ModuleSendEmailSetting)
from inspection.filters import (
    InspectionHistoryFilter, InspectionCrontabFilter, )
from inspection.serializers import (
    InspectionHistorySerializer, InspectionCrontabSerializer,
    InspectionReportSerializer)
from rest_framework.filters import OrderingFilter
from inspection.joint_json_report import joint_json_data

logger = logging.getLogger('server')


class InspectionServiceView(ListModelMixin, GenericViewSet):
    """
        list: 组件巡检 组件列表
    """

    def list(self, request, *args, **kwargs):
        # 只能是安装成功的组件
        rets = list()
        _ = Service.objects.filter(service__is_base_env=False).exclude(service__app_port=None).exclude(
            service_status__in=[5, 6, 7])
        for i in _:
            rets.append({'service__id': i.id,
                         'service__app_name': i.service_instance_name})

        return Response(data=rets, status=status.HTTP_200_OK)


class InspectionHistoryView(ListModelMixin, GenericViewSet, CreateModelMixin):
    """
        list:  查询巡检记录历史记录列表
    """
    queryset = InspectionHistory.objects.all()
    serializer_class = InspectionHistorySerializer
    pagination_class = PageNumberPager
    # 过滤字段
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_class = InspectionHistoryFilter
    # 动态排序字段
    dynamic_fields = ("start_time",)
    # 操作描述信息
    get_description = "查询巡检历史记录列表"

    def list(self, request, *args, **kwargs):
        # 获取序列化数据列表
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(
            self.paginate_queryset(queryset), many=True)
        serializer_data = serializer.data

        # 获取请求中 ordering 字段
        query_field = request.query_params.get("ordering", "")
        reverse_flag = False
        if query_field.startswith("-"):
            reverse_flag = True
            query_field = query_field[1:]
        # 若排序字段在类视图 dynamic_fields 中，则对根据动态数据进行排序
        none_ls = list(filter(
            lambda x: x.get(query_field) is None,
            serializer_data))
        exists_ls = list(filter(
            lambda x: x.get(query_field) is not None,
            serializer_data))
        if query_field in self.dynamic_fields:
            exists_ls = sorted(
                exists_ls,
                key=lambda x: x.get(query_field),
                reverse=reverse_flag)
        exists_ls.extend(none_ls)

        return self.get_paginated_response(exists_ls)

    @staticmethod
    def joint_inspection_name(data_dict):
        now = datetime.datetime.now()
        num = InspectionHistory.objects.filter(
            start_time__year=now.year, start_time__month=now.month,
            start_time__day=now.day).count()
        tp = {'deep': '深度巡检', 'host': '主机巡检', 'service': '组件巡检'}
        name = f"{tp.get(data_dict.get('inspection_type'))}-" \
               f"{now.strftime('%Y%m%d')}{num + 1}"
        return name

    def create(self, request, *args, **kwargs):
        data_dict = request.data
        # 一、创建巡检历史表数据
        env_obj = Env.objects.filter(id=data_dict['env']).first()
        data_dict['env'] = env_obj
        data_dict['inspection_name'] = self.joint_inspection_name(data_dict)
        his_obj = InspectionHistory(**data_dict)
        his_obj.save()
        # 二、创建巡检记录历史表关联的报告表的数据
        rep_obj = InspectionReport(**{'inst_id': his_obj})
        rep_obj.save()
        # 三、手动序列化数据，不是json的不能response
        data_dict.update({'id': his_obj.id, 'env': data_dict['env'].id})
        # 四、下发celery异步任务
        handle = data_dict.get('inspection_type')
        # 异步下发
        get_prometheus_data.delay(
            env_id=env_obj.id, hosts=his_obj.hosts, services=his_obj.services,
            history_id=his_obj.id, report_id=rep_obj.id, handle=handle)
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

    @staticmethod
    def transfer_week(request):
        """
        因前端day_of_week参数传递 不符合规范，只能适配了呗
        """
        day_of_week = request.data.get('crontab_detail').get('day_of_week')
        if day_of_week == '6':
            day_of_week = '0'
        elif day_of_week == '*':
            pass
        else:
            day_of_week = str(int(day_of_week) + 1)

        return day_of_week

    def create(self, request, *args, **kwargs):
        # 判断是否需要下发任务到celery：0-开启，1-关闭
        is_success = True
        request.data['job_type'] = int(request.data.get('job_type'))
        if request.data.get('is_start_crontab') == 0:
            tp = {0: 'deep', 1: 'host', 2: 'service'}
            task_name = \
                f"inspection_cron_task_{tp.get(request.data.get('job_type'))}"
            task_func = "inspection.tasks.inspection_crontab"
            cron_obj = CrontabUtils(task_name=task_name, task_func=task_func,
                                    task_kwargs=request.data)
            cron_args = {
                'minute': request.data.get('crontab_detail').get('minute'),
                'hour': request.data.get('crontab_detail').get('hour'),
                'day_of_month': request.data.get('crontab_detail').get('day'),
                'month_of_year':
                    request.data.get('crontab_detail').get('month'),
                'day_of_week': self.transfer_week(request)
            }
            is_success, job_name = cron_obj.create_crontab_job(**cron_args)
        else:
            pass

        if is_success:
            # 只是想在增加时加个判断及对应操作，增加还是执行父类的create
            return CreateModelMixin.create(self, request, *args, **kwargs)
        else:
            return Response(data='定时任务已存在，请勿重复操作',
                            status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        # 判断是否需要下发任务到celery：0-开启，1-关闭
        is_success = True
        request.data['job_type'] = int(request.data.get('job_type'))
        if request.data.get('is_start_crontab') == 0:
            tp = {0: 'deep', 1: 'host', 2: 'service'}
            task_name = \
                f"inspection_cron_task_{tp.get(request.data.get('job_type'))}"
            task_func = 'inspection.tasks.inspection_crontab'
            cron_obj = CrontabUtils(task_name=task_name, task_func=task_func,
                                    task_kwargs=request.data)
            cron_args = {
                'minute': request.data.get('crontab_detail').get('minute'),
                'hour': request.data.get('crontab_detail').get('hour'),
                'day_of_month': request.data.get('crontab_detail').get('day'),
                'month_of_year':
                    request.data.get('crontab_detail').get('month'),
                'day_of_week': self.transfer_week(request)
            }
            # 删除定时任务
            cron_obj.delete_job()
            # 增加定时任务
            is_success, job_name = cron_obj.create_crontab_job(**cron_args)
        else:
            tp = {0: 'deep', 1: 'host', 2: 'service'}
            task_name = \
                f"inspection_cron_task_{tp.get(request.data.get('job_type'))}"
            task_func = 'inspection.tasks.inspection_crontab'
            cron_obj = CrontabUtils(task_name=task_name, task_func=task_func,
                                    task_kwargs=request.data)
            # 删除定时任务
            cron_obj.delete_job()

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
    # 操作描述信息
    get_description = "查询巡检任务配置列表"

    def retrieve(self, request, *args, **kwargs):
        data_dict = request.parser_context.get('kwargs')
        _r = InspectionReport.objects.filter(
            inst_id=data_dict.get('inst_id')).first()
        _h = InspectionHistory.objects.filter(
            id=data_dict.get('inst_id')).first()
        if not _r or not _h:
            return Response('巡检报告缺失，暂不可查看')

        ret = joint_json_data(_h.inspection_type, _r, _h)
        return Response(ret)


class InspectionSendEmailSettingView(GenericViewSet, ListModelMixin, CreateModelMixin):
    """
    读写巡检邮箱收件配置
    """
    get_description = "读取巡检邮箱设置"
    post_description = "更新巡检邮箱设置"

    serializer_class = Serializer

    def list(self, request, *args, **kwargs):
        # env_id = request.GET.get("env_id")
        env_id = 1  # 单环境暂为1
        email_setting = ModuleSendEmailSetting.get_email_settings(
            env_id, "inspection")  # TODO 暂写死为巡检
        if not email_setting:
            return Response(data={})
        return Response(
            data={
                "to_users": email_setting.to_users,
                "send_email": email_setting.send_email
            }
        )

    def create(self, request, *args, **kwargs):
        env_id = request.data.get("env_id")
        send_email = request.data.get("send_email", False)
        to_users = request.data.get("to_users")
        if not to_users and send_email:
            return Response(data={"code": 1, "message": "收件邮箱必填！"})
        if to_users:
            emails = to_users.split(",")
            for email in emails:
                try:
                    EmailValidator()(email)
                except Exception as e:
                    message = f"收件箱{email}格式错误！"
                    logger.error(f"{message} 错误信息：{str(e)}")
                    return Response(data={"code": 1, "message": message})
        try:
            ModuleSendEmailSetting.update_email_settings(
                env_id, "inspection", send_email, to_users)  # TODO 暂写死为巡检
        except Exception as e:
            logger.info(f"更新邮箱配置失败：{str(e)}，详情为：{traceback.format_exc()}")
            return Response(data={"code": 1, "message": "更新邮箱配置失败！"})
        return Response({})


class InspectionSendEmailAPIView(GenericViewSet, CreateModelMixin):
    """
    巡检邮件推送
    """
    post_description = "巡检邮件推送"
    serializer_class = Serializer

    def create(self, request, *args, **kwargs):
        inspection_id = request.data.get("id")
        inspection_module = request.data.get("module")
        if inspection_module not in ("host", "service", "deep"):
            return Response(data={"code": 1, "message": "请选择正确的巡检对象！"})
        to_users = request.data.get("to_users")
        if not to_users:
            return Response(data={"code": 1, "message": "请填入接收邮件邮箱！"})
        emails = to_users.split(",")
        for email in emails:
            try:
                EmailValidator()(email)
            except Exception as e:
                message = f"收件箱{email}格式错误！"
                logger.error(f"{message} 错误信息：{str(e)}")
                return Response(data={"code": 1, "message": message})
        state, result = send_report_email(
            inspection_module, inspection_id, emails)
        if not state:
            return Response(data={"code": 1, "message": result})
        return Response({})
