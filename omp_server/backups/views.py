# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: lingyang guo

import datetime
import json
import logging
import os

from django.conf import settings
from django.core.validators import EmailValidator
from rest_framework import status
from rest_framework.mixins import ListModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.serializers import Serializer
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

from backups.backups_utils import send_email as utils_send_email, rm_backend_file, transfer_week
from db_models.models import BackupSetting, BackupHistory, Env, ApplicationHub, ModuleSendEmailSetting
from utils.plugin.crontab_utils import CrontabUtils

logger = logging.getLogger("server")


class BackupSettingView(GenericViewSet, ListModelMixin, CreateModelMixin, UpdateModelMixin):
    """
    操作备份策略
    """

    get_description = "读取备份策略"
    post_description = "更新备份策略"

    serializer_class = Serializer

    def list(self, request, *args, **kwargs):
        env_id = request.GET.get("env_id")
        try:
            Env.objects.get(id=int(env_id))
        except Exception as e:
            logger.error(f"id为{env_id}的环境不存在!详情：{e}")
            return Response(data={"code": 1, "message": f"id为{env_id}的环境不存在!"})
        backup_setting = BackupSetting.objects.filter(env_id=env_id).first()
        can_backup_service = ApplicationHub.objects.filter(
            env_id=env_id,
            service_name__in=settings.BACKUP_SERVICE
        ).distinct().values_list("service_name", flat=True)
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
                    "can_backup_service": list(can_backup_service),
                    "backup_setting": {
                        "retain_path": settings.BACKUP_DEFAULT_PATH,
                        "to_users": to_users,
                        "send_email": send_email
                    }
                }
            )
        return Response(
            data={
                "can_backup_service": list(can_backup_service),
                "backup_setting": {
                    "backup_service": backup_setting.backup_service,
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

    def update(self, request, *args, **kwargs):
        request_data = json.loads(request.body)
        env_id = request_data.get("env_id")
        try:
            Env.objects.get(id=int(env_id))
        except Exception as e:
            logger.error(f"id为{env_id}的环境不存在!详情：{e}")
            return Response(data={"code": 1, "message": f"id为{env_id}的环境不存在!"})
        is_on = request_data.get("is_on", False)
        old_setting = BackupSetting.objects.filter(env_id=env_id).first()
        backup_services = request_data.get("backup_service")
        send_email = request_data.get("send_email", False)
        to_users = request_data.get("to_users", "")
        err_message = self.validate_email_send(send_email, to_users)
        if err_message:
            return Response(data={"code": 1, "message": f"{err_message}"})
        else:
            ModuleSendEmailSetting.update_email_settings(
                env_id, BackupSetting.__name__, send_email, to_users
            )
        # v1.5.0 修改
        backup_setting = BackupSetting.objects.filter(
            env_id=env_id
        ).first()
        # 关闭定时策略，删除定时任务
        if not is_on:
            if old_setting:
                try:
                    task_name = request.data.get('xxx')  # TODO 填充task_name
                    exe_cron_obj = CrontabUtils(task_name=task_name)
                    exe_cron_obj.delete_job()
                except Exception as e:
                    logger.info(f"删除定时任务失败！{str(e)}")
                if backup_setting:
                    backup_setting.is_on = False
                    backup_setting.backup_service = backup_services
                    backup_setting.save()
                else:
                    BackupSetting.objects.create(
                        env_id=env_id,
                        backup_service=backup_services,
                        crontab_detail={},
                        retain_day=7,
                        retain_path=settings.BACKUP_DEFAULT_PATH
                    )
            return Response({})
        retain_day = request_data.get("retain_day", 1)
        retain_path = request_data.get("retain_path", "")
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

        if not backup_services:
            return Response(data={"code": 1, "message": "备份服务需必填！"})
        can_backup_service = ApplicationHub.objects.filter(
            env_id=env_id,
            service_name__in=backup_services
        ).distinct().values_list("service_name", flat=True)
        diff_service = set(can_backup_service) - settings.BACKUP_SERVICE
        if diff_service:
            return Response(data={"code": 1, "message": f"服务{diff_service}在本环境下不支持备份"})
        crontab_detail = request_data.get("crontab_detail", "")
        if not crontab_detail:
            return Response(data={"code": 1, "message": "请填写备份策略！"})
        # omp-v-1.5修改，不改变邮箱设置
        backup_setting = BackupSetting.objects.filter(
            env_id=env_id
        ).first()
        if not backup_setting:
            backup_setting = BackupSetting.objects.create(
                env_id=env_id,
                backup_service=backup_services,
                is_on=is_on,
                crontab_detail=crontab_detail,
                retain_day=retain_day,
                retain_path=retain_path
            )
        else:
            backup_setting.backup_service = backup_services
            backup_setting.is_on = is_on
            backup_setting.crontab_detail = crontab_detail
            backup_setting.retain_day = retain_day
            backup_setting.retain_path = retain_path
            backup_setting.save()
        try:
            task_name = request.data.get('xxx')  # TODO 填充task_name
            exe_cron_obj = CrontabUtils(task_name=task_name)
            exe_cron_obj.delete_job()
        except Exception as e:
            logger.info(f"删除定时任务backup_service_{backup_setting}失败，详情：{e}")
        try:
            task_name = "backups_cron_task"
            task_func = "backups.tasks.backups_crontab"  # TODO 填充tasks
            cron_obj = CrontabUtils(task_name=task_name, task_func=task_func,
                                    task_kwargs=request.data)
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
                # 只是想在增加时加个判断及对应操作，增加还是执行父类的create
                return CreateModelMixin.create(self, request, *args, **kwargs)
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
        env_id = request_data.get("env_id")
        try:
            Env.objects.get(id=int(env_id))
        except Exception as e:
            logger.error(f"id为{env_id}的环境不存在!详情：{e}")
            return Response(data={"code": 1, "message": f"id为{env_id}的环境不存在!"})
        backup_services = request_data.get("backup_service")

        if not backup_services:
            return Response(data={"code": 1, "message": "请选择需要备份的服务！"})
        can_backup_service = ApplicationHub.objects.filter(
            env_id=env_id,
            service_name__in=backup_services
        ).distinct().values_list("service_name", flat=True)
        diff_service = set(can_backup_service) - settings.BACKUP_SERVICE
        if not can_backup_service or diff_service:
            return Response(data={"code": 1, "message": f"服务{diff_service}在本环境下不支持备份"})

        backup_setting = BackupSetting.objects.filter(
            env_id=env_id,
        ).first()
        if backup_setting:
            retain_path = backup_setting.retain_path
            expire_days = backup_setting.retain_day
        else:
            retain_path = settings.BACKUP_DEFAULT_PATH
            expire_days = 7

        date_str = datetime.date.today().strftime('%Y%m%d')
        history_count = BackupHistory.objects.filter(
            create_time__gte=datetime.date.today()
        ).count()
        expire_time = datetime.datetime.now() + datetime.timedelta(
            days=expire_days)
        try:
            BackupHistory.objects.create(
                backup_name=f"数据备份-{date_str}{history_count + 1}-{env_id}",
                content=backup_services,
                env_id=env_id,
                expire_time=expire_time,
                retain_path=retain_path,
                operation="手动执行"
            )
            # next_time = datetime.datetime.now() + datetime.timedelta(
            #     seconds=3)
            task_name = "backups_cron_task"
            task_func = "backups.tasks.backups_crontab"  # TODO 填充tasks
            cron_obj = CrontabUtils(task_name=task_name, task_func=task_func,
                                    task_kwargs=request.data)
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
                # 只是想在增加时加个判断及对应操作，增加还是执行父类的create
                return CreateModelMixin.create(self, request, *args, **kwargs)
            else:
                return Response(data='定时任务已存在，请勿重复操作',
                                status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"添加定时任务失败！{str(e)}")
            return Response(data={"code": 1, "message": "备份任务下发失败！请重试！"})


class BackupHistoryDeleteView(GenericViewSet, ListModelMixin, DestroyModelMixin):
    ordering = ("file_deleted", "-id")
    queryset = BackupHistory.objects.all().extra(
        select={"expire_time": "datetime(expire_time)"}
    )
    values_fields = (
        "id", "backup_name", "content", "result", "file_name",
        "file_size", "expire_time", "file_deleted", "message",
        "operation", "send_email_result", "email_fail_reason"
    )

    def list(self, request, *args, **kwargs):
        """
        获取备份历史记录
        """
        env_id = request.GET.get("env_id")
        try:
            Env.objects.get(id=int(env_id))
        except Exception as e:
            logger.error(f"id为{env_id}的环境不存在!详情：{e}")
            return Response(data={"code": 1, "message": f"id为{env_id}的环境不存在!"})
        return self.list(request, env_id=env_id)

    def destroy(self, request, *args, **kwargs):
        """
        删除备份文件，只删除文件
        """
        request_data = json.loads(request.body)
        env_id = request_data.get("env_id")
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
            return Response(data={"code": 1, "message": f"更新主机相关阈值过程中出错: {str(result)}!"})
        return Response({})
