# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: lingyang guo

import datetime
import json
import logging
import os
import traceback

from django.conf import settings
from django.core.validators import EmailValidator
from rest_framework import status
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.serializers import Serializer
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

from backups.backups_serializers import BackupHistorySerializer
from backups.backups_utils import send_email as utils_send_email, rm_backend_file, transfer_week
from backups.tasks import backup_service_once
from db_models.models import BackupSetting, BackupHistory, Env, ModuleSendEmailSetting, Service
from utils.common.paginations import PageNumberPager
from utils.plugin.crontab_utils import CrontabUtils

logger = logging.getLogger("server")


class CanBackupInstancesView(GenericViewSet, ListModelMixin):
    """
    获取可备份实例列表
    """
    get_description = "读取可备份实例列表"
    serializer_class = Serializer

    def list(self, request, *args, **kwargs):
        env_id = request.GET.get("env_id", '1')  # 取不到则默认值为1
        try:
            Env.objects.get(id=int(env_id))
        except Exception as e:
            logger.error(f"id为{env_id}的环境不存在!详情：{e}")
            return Response(data={"code": 1, "message": f"id为{env_id}的环境不存在!"})
        can_backup_instance = Service.objects.filter(
            env_id=env_id,
            service__app_name__in=settings.BACKUP_SERVICE
        ).distinct().values_list("service_instance_name", flat=True)
        return Response(
            data=can_backup_instance
        )


class BackupSettingView(GenericViewSet, ListModelMixin, CreateModelMixin):
    """
    操作备份策略
    """

    get_description = "读取备份策略"
    post_description = "更新备份策略"

    serializer_class = Serializer

    def list(self, request, *args, **kwargs):
        """
        读取备份策略
        """
        env_id = request.GET.get("env_id", '1')  # 取不到则默认值为1
        try:
            Env.objects.get(id=int(env_id))
        except Exception as e:
            logger.error(f"id为{env_id}的环境不存在!详情：{e}")
            return Response(data={"code": 1, "message": f"id为{env_id}的环境不存在!"})
        backup_setting = BackupSetting.objects.filter(env_id=env_id).first()
        can_backup_instance = Service.objects.filter(
            env_id=env_id,
            service__app_name__in=settings.BACKUP_SERVICE
        ).distinct().values_list("service_instance_name", flat=True)
        email_setting = ModuleSendEmailSetting.get_email_settings(
            env_id, BackupSetting.__name__)
        if email_setting:
            to_users = email_setting.to_users
            send_email = email_setting.send_email
        else:
            to_users = ""
            send_email = False
        if not backup_setting:
            return Response(
                data={
                    "can_backup_instance": list(can_backup_instance),
                    "backup_setting": {
                        "backup_instances": [],
                        "is_on": False,
                        # "crontab_detail": None,
                        "retain_day": 7,
                        "retain_path": settings.BACKUP_DEFAULT_PATH,
                        "env_id": env_id,
                        "to_users": to_users,
                        "send_email": send_email
                    }
                }
            )
        return Response(
            data={
                "can_backup_instance": list(can_backup_instance),
                "backup_setting": {
                    "backup_instances": backup_setting.backup_instances,
                    "is_on": backup_setting.is_on,
                    "crontab_detail": backup_setting.crontab_detail,
                    "retain_day": backup_setting.retain_day,
                    "retain_path": backup_setting.retain_path,
                    "env_id": backup_setting.env_id,
                    "to_users": to_users,
                    "send_email": send_email
                }
            }
        )

    @staticmethod
    def validate_email_send(send_email, to_users):
        if not to_users and send_email:
            return "收件邮箱必填！"
        if to_users:
            emails = to_users.split(",")
            for email in emails:
                try:
                    EmailValidator()(email)
                except Exception as e:
                    message = f"收件箱{email}格式错误！"
                    logger.error(f"{message} 错误信息：{str(e)}")
                    return message
        return ""

    def create(self, request, *args, **kwargs):
        """
        更新备份策略
        """
        request_data = json.loads(request.body)
        env_id = request_data.get("env_id", "1")
        try:
            Env.objects.get(id=int(env_id))
        except Exception as e:
            logger.error(f"id为{env_id}的环境不存在!详情：{e}")
            return Response(data={"code": 1, "message": f"id为{env_id}的环境不存在!"})
        is_on = request_data.get("is_on", False)
        backup_instances = request_data.get("backup_instances")
        retain_day = request_data.get("retain_day", 30)
        retain_path = request_data.get("retain_path", "")
        crontab_detail = request_data.get("crontab_detail", "")
        send_email = request_data.get("send_email", False)
        to_users = request_data.get("to_users", "")
        err_message = self.validate_email_send(send_email, to_users)
        if err_message:
            return Response(data={"code": 1, "message": f"{err_message}"})
        else:
            ModuleSendEmailSetting.update_email_settings(
                env_id, BackupSetting.__name__, send_email, to_users
            )
        backup_setting = BackupSetting.objects.filter(env_id=env_id).first()
        if not retain_path:
            return Response(data={"code": 1, "message": "请确定备份文件保存路径！"})
        try:
            folder = os.path.exists(retain_path)
            if not folder:
                os.makedirs(retain_path)
            file_path = os.path.join(retain_path, 'test.txt')
            create_file = open(file_path, "w")
            create_file.close()
        except Exception as e:
            logger.info(f"校验文件夹权限失败：{str(e)}")
            return Response(data={"code": 1, "message": "请确定程序对备份文件保存文件夹有读写权限！"})
        if not crontab_detail:
            return Response(data={"code": 1, "message": "请填写备份策略！"})
        # 关闭定时策略，删除定时任务
        if not is_on:
            if backup_setting:
                try:
                    task_name = "backups_cron_task"
                    exe_cron_obj = CrontabUtils(task_name=task_name)
                    exe_cron_obj.delete_job()
                except Exception as e:
                    logger.info(f"删除定时任务失败！{str(e)}")
                backup_setting.env_id = env_id
                backup_setting.is_on = False
                backup_setting.backup_instances = backup_instances
                backup_setting.retain_path = retain_path
                backup_setting.crontab_detail = crontab_detail
                backup_setting.retain_day = retain_day
                backup_setting.save()
            else:
                BackupSetting.objects.create(
                    is_on=False,
                    env_id=env_id,
                    backup_instances=backup_instances,
                    crontab_detail=crontab_detail,
                    retain_day=retain_day,
                    retain_path=retain_path
                )
            return Response({})

        if not backup_instances:
            return Response(data={"code": 1, "message": "备份服务需必填！"})
        can_backup_instance = Service.objects.filter(
            env_id=env_id,
            service__app_name__in=settings.BACKUP_SERVICE
        ).distinct().values_list("service_instance_name", flat=True)
        diff_service = set(backup_instances) - set(can_backup_instance)
        if diff_service:
            return Response(data={"code": 1, "message": f"服务{diff_service}在本环境下不支持备份"})

        if not backup_setting:
            backup_setting = BackupSetting.objects.create(
                env_id=env_id,
                backup_instances=backup_instances,
                is_on=is_on,
                crontab_detail=crontab_detail,
                retain_day=retain_day,
                retain_path=retain_path
            )
        else:
            backup_setting.env_id = env_id
            backup_setting.backup_instances = backup_instances
            backup_setting.is_on = is_on
            backup_setting.crontab_detail = crontab_detail
            backup_setting.retain_day = retain_day
            backup_setting.retain_path = retain_path
            backup_setting.save()
        try:
            task_name = "backups_cron_task"
            exe_cron_obj = CrontabUtils(task_name=task_name)
            exe_cron_obj.delete_job()
        except Exception as e:
            logger.info(f"删除定时任务backup_service_{backup_setting}失败，详情：{e}")
        try:
            task_name = "backups_cron_task"
            task_func = "backups.tasks.backup_service"
            cron_obj = CrontabUtils(task_name=task_name, task_func=task_func,
                                    task_kwargs={"backup_setting_id": backup_setting.id})
            cron_args = {
                'minute': request.data.get('crontab_detail').get('minute'),
                'hour': request.data.get('crontab_detail').get('hour'),
                'day_of_month': request.data.get('crontab_detail').get('day'),
                'month_of_year':
                    request.data.get('crontab_detail').get('month'),
                'day_of_week': transfer_week(request)
            }
            is_success, job_name = cron_obj.create_crontab_job(**cron_args)
            if is_success:
                return Response({})
            else:
                return Response(data='定时任务已存在，请勿重复操作',
                                status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"添加定时任务失败：{str(e)}")
            return Response(data={"code": 1, "message": "添加定时任务失败，请重试！"})


class BackupOnceView(GenericViewSet, CreateModelMixin):
    """
    单次备份
    """
    post_description = "单次备份"

    serializer_class = Serializer

    def create(self, request, *args, **kwargs):
        request_data = json.loads(request.body)
        env_id = request_data.get("env_id", "1")
        try:
            Env.objects.get(id=int(env_id))
        except Exception as e:
            logger.error(f"id为{env_id}的环境不存在!详情：{e}")
            return Response(data={"code": 1, "message": f"id为{env_id}的环境不存在!"})
        backup_instances = request_data.get("backup_instances")

        if not backup_instances:
            return Response(data={"code": 1, "message": "请选择需要备份的服务！"})
        can_backup_instance = Service.objects.filter(
            env_id=env_id,
            service__app_name__in=settings.BACKUP_SERVICE
        ).distinct().values_list("service_instance_name", flat=True)
        diff_service = set(backup_instances) - set(can_backup_instance)
        if diff_service:
            return Response(data={"code": 1, "message": f"服务{diff_service}在本环境下不支持备份"})

        backup_setting = BackupSetting.objects.filter(
            env_id=env_id,
        ).first()
        if backup_setting:
            retain_path = backup_setting.retain_path
            expire_days = backup_setting.retain_day
        else:
            retain_path = settings.BACKUP_DEFAULT_PATH
            expire_days = 30

        date_str = datetime.date.today().strftime('%Y%m%d')
        history_count = BackupHistory.objects.filter(
            create_time__gte=datetime.date.today()
        ).count()
        expire_time = datetime.datetime.now() + datetime.timedelta(
            days=expire_days)
        try:
            history = BackupHistory.objects.create(
                backup_name=f"数据备份-{date_str}{history_count + 1}-{env_id}",
                content=backup_instances,
                env_id=env_id,
                expire_time=expire_time,
                retain_path=retain_path,
                operation="手动执行",
                file_name=f"数据备份-{date_str}{history_count + 1}-{env_id}.tar.gz"
            )
            backup_service_once.delay(history.id)
            return Response({})

        except Exception as e:
            logger.error(f"备份任务下发失败！{str(e)}详情:{traceback.format_exc(e)}")
            return Response(data={"code": 1, "message": "备份任务下发失败！"})


class BackupHistoryView(GenericViewSet, ListModelMixin, CreateModelMixin):
    """
    备份记录相关视图
    """
    serializer_class = BackupHistorySerializer
    # queryset = BackupHistory.objects.all().extra(
    #     select={"expire_time": "datetime(expire_time)"}
    # ).order_by("-create_time")   # 分页，过滤，排序
    pagination_class = PageNumberPager

    # values_fields = (
    #     "id", "backup_name", "content", "result", "file_name",
    #     "file_size", "expire_time", "file_deleted", "message",
    #     "operation", "send_email_result", "email_fail_reason"
    # )

    def list(self, request, *args, **kwargs):
        """
        获取备份历史记录
        """
        env_id = request.GET.get("env_id", "1")
        try:
            Env.objects.get(id=int(env_id))
        except Exception as e:
            logger.error(f"id为{env_id}的环境不存在!详情：{e}")
            return Response(data={"code": 1, "message": f"id为{env_id}的环境不存在!"})
        queryset = BackupHistory.objects.all().order_by("-create_time")  # 分页，过滤，排序

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        删除备份文件，只删除文件
        """
        request_data = json.loads(request.body)
        env_id = request_data.get("env_id", "1")
        try:
            Env.objects.get(id=int(env_id))
        except Exception as e:
            logger.error(f"id为{env_id}的环境不存在!详情：{e}")
            return Response(data={"code": 1, "message": f"id为{env_id}的环境不存在!"})

        ids = request_data.get("ids")
        if not ids or not isinstance(ids, list):
            return Response(data={"code": 1, "message": "请选择需要删除的历史记录！"})
        fail_files = rm_backend_file(ids=ids)
        if fail_files:
            return Response(data={"code": 1, "message": f"删除{','.join(fail_files)}失败！"})
        return Response({})


class BackupSendEmailView(GenericViewSet, CreateModelMixin):
    """
    发送备份结果邮件
    """

    post_description = "发送备份结果邮件"

    serializer_class = Serializer

    def create(self, request, *args, **kwargs):
        request_data = json.loads(request.body)
        history_id = request_data.get("id")
        try:
            history = BackupHistory.objects.get(id=history_id)
        except Exception as e:
            logger.error(f"未找到对应备份记录：{str(e)}")
            return Response(data={"code": 1, "message": "请选择正确的备份记录！"})
        if history.file_deleted:
            return Response(data={"code": 1, "message": "备份文件已被删除！"})
        to_users = request_data.get("to_users")
        if not to_users:
            return Response(data={"code": 1, "message": "请填入接收邮件邮箱！"})
        emails = to_users.split(",")
        for email in emails:
            try:
                EmailValidator()(email)
            except Exception as e:
                message = f"收件箱{email}格式错误！"
                logger.error(f"{message} 错误信息：{str(e)}")
                return Response(data={"code": 1, "message": f"{message}"})
        result = utils_send_email(history.id, emails)
        if result:
            return Response(data={"code": 1, "message": f"发送备份邮件过程中出错: {str(result)}!"})
        return Response({})
