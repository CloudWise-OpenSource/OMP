# !/usr/bin/python3
# -*-coding:utf-8-*-

import logging

from rest_framework.mixins import ListModelMixin, CreateModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from backups.backups_serializers import BackupHistorySerializer, \
    BackupHistoryIdsSerializer, BackupSettingSerializer, \
    BackupCustomSerializer, BackupCustomRepeatSerializer

from backups.backups_utils import rm_backend_file, \
    check_ing
from utils.plugin.crontab_utils import change_task
from backups.tasks import backup_service, pull_back_file
from db_models.models import BackupSetting, BackupHistory, Service, \
    BackupCustom
from utils.common.paginations import PageNumberPager
from utils.parse_config import BACKUP_SERVICE

logger = logging.getLogger("server")


class CanBackupInstancesView(GenericViewSet, ListModelMixin):
    """
    获取可备份实例列表
    """
    get_description = "读取可备份实例列表"

    def list(self, request, *args, **kwargs):
        # ToDo 找不出更合适的继承
        ser_data = Service.objects.filter(
            service__app_name__in=BACKUP_SERVICE
        ).filter(service_status=Service.SERVICE_STATUS_NORMAL).values_list("service_instance_name", flat=True)
        # back_instance = BackupSetting.objects.all().values_list("backup_instances", flat=True)
        # back_set = []
        # for instance in back_instance:
        #    back_set.extend(instance)
        # ser_data = list(set(ser_data) - set(back_set))
        return Response(data=list(ser_data))


class BackupSettingView(GenericViewSet, ListModelMixin,
                        CreateModelMixin, UpdateModelMixin,
                        DestroyModelMixin):
    """
    操作备份策略
    """

    get_description = "读取备份策略"
    post_description = "更新备份策略"
    serializer_class = BackupSettingSerializer
    queryset = BackupSetting.objects.all().order_by("-id")

    def create(self, request, *args, **kwargs):
        """
        更新备份策略
        """
        set_id = request.data.pop("id", 0)
        extend_field = request.data.pop("backup_custom", [])
        if set_id:
            # 任务策略制定后触发一次备份任务
            if check_ing(BackupSetting.objects.filter(id=set_id).first()):
                return Response(data={"code": 1, "message": f"当前策略存在正在备份的实例或id{set_id}不存在"})
            backup_service.delay(task_id=set_id)
            return Response("任务下发成功")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        # 多对多
        for field in extend_field:
            custom = BackupCustom.objects.filter(**field).first()
            obj.backup_custom.add(custom)
        code, msg = change_task(obj.id, request.data)
        return Response(msg)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        extend_field = request.data.pop("backup_custom", [])
        extend_con = [field["id"] for field in extend_field]
        instance.backup_custom.set(extend_con)
        instance.save()
        super(BackupSettingView, self).update(
            request, request, *args, **kwargs)
        code, msg = change_task(instance.id, request.data)
        return Response(msg)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        super(BackupSettingView, self).destroy(
            request, request, *args, **kwargs)
        code, msg = change_task(instance.id)
        return Response(msg)


class BackupHistoryView(GenericViewSet, ListModelMixin,
                        DestroyModelMixin, UpdateModelMixin
                        ):
    """
    备份记录相关视图
    """
    queryset = BackupHistory.objects.all().order_by("-create_time")
    pagination_class = PageNumberPager
    # 关闭权限、认证设置
    authentication_classes = ()
    permission_classes = ()

    delete_description = "删除备份记录文件"
    get_description = "获取备份历史记录"

    def get_serializer_class(self):
        if self.request is not None and self.request.method == "POST":
            return BackupHistoryIdsSerializer
        return BackupHistorySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.validated_data["id"]
        fail_files = rm_backend_file(instance)
        if fail_files:
            return Response(data={"code": 0, "message": f"删除{','.join(fail_files)}可能已不存在！"})
        return Response("删除记录成功")

    def update(self, request, *args, **kwargs):
        # 转换code意义，考虑是否把含义变更
        code = 0 if request.data.pop("result") != "0" else 1
        remote_path = request.data.get("remote_path", "")
        need_push = request.data.get("need_push", False)
        # 文件备份
        request.data["file_deleted"] = False if remote_path else True
        # 成功 且 存在要拉取的文件
        if code and remote_path and need_push:
            if remote_path.startswith("/") and remote_path.endswith(".tar.gz"):
                instance = self.get_object()
                pull_back_file.delay(
                    instance.id, remote_path, request.data["ip"])
            else:
                raise ValidationError(f"文件不合法{remote_path}")
            request.data["remote_path"] = ""
        else:
            request.data["retain_path"] = ""
            request.data["result"] = code
        return super(BackupHistoryView, self).update(
            request, request, *args, **kwargs)


class BackupCustomView(GenericViewSet, ListModelMixin,
                       CreateModelMixin, UpdateModelMixin,
                       DestroyModelMixin):
    """
    备份自定义字典视图
    """
    serializer_class = BackupCustomSerializer
    queryset = BackupCustom.objects.all()

    delete_description = "删除备份自定义字典"
    get_description = "获取备份自定义字典"
    put_description = "修改备份自定义字典"
    post_description = "创建备份自定义字典"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        BackupCustom.objects.create(**serializer.data)
        return Response("创建成功")


class BackupCustomRepeatView(GenericViewSet, ListModelMixin):
    """
        list:
        查询备份字典是否有多对多关联
    """

    serializer_class = BackupCustomRepeatSerializer

    get_description = "查询备份字典是否有多对多关联"

    def get_queryset(self):
        bk_id = self.request.query_params.get('id')
        if bk_id:
            return BackupCustom.objects.filter(id=bk_id)
        else:
            raise ValidationError("需要填写id")
