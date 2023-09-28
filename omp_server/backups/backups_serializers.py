# !/usr/bin/python3
# -*-coding:utf-8-*-
import logging
import os
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from utils.common.validators import ReValidator
from db_models.models import BackupHistory, BackupSetting, BackupCustom

logger = logging.getLogger("server")


class BackupHistoryIdsSerializer(ModelSerializer):
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="主机id列表",
        required=True,
        write_only=True,
        source="id",
        error_messages={"required": "必须包含[ids]字段"}
    )

    def validate(self, attrs):
        backup_obj = BackupHistory.objects.filter(id__in=attrs["id"])
        if len(backup_obj) != len(attrs["id"]):
            raise ValidationError(f"id不存在")
        attrs["id"] = backup_obj
        return attrs

    class Meta:
        model = BackupHistory
        fields = ("ids",)


class BackupHistorySerializer(ModelSerializer):
    class Meta:
        model = BackupHistory
        fields = "__all__"
        write_only_fields = ("id",)


class BackupCustomSerializer(ModelSerializer):
    notes = serializers.CharField(
        help_text="备注信息",
        required=False, default="",
        allow_null=True, allow_blank=True
    )

    def validate(self, attrs):
        backup_obj = BackupCustom.objects.filter(
            field_k=attrs["field_k"], field_v=attrs["field_v"]).count()
        if backup_obj != 0:
            raise ValidationError(f"自定义参数不可重复")
        return attrs

    class Meta:
        model = BackupCustom
        fields = "__all__"


class BackupCustomRepeatSerializer(ModelSerializer):
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        instance_ls = []
        for instance in obj.backupsetting_set.all():
            instance_ls.extend(instance.backup_instances)
        return ",".join(set(instance_ls))

    class Meta:
        model = BackupCustom
        fields = ("name",)


class BackupSettingSerializer(ModelSerializer):
    backup_instances = serializers.ListField(
        help_text="备份服务实例名称", required=True,
        error_messages={"required": "备份服务需必填"}
    )
    crontab_detail = serializers.DictField(
        help_text="定时任务详情", required=True,
        error_messages={"required": "请填写备份策略"})
    retain_day = serializers.IntegerField(help_text="文件保存天数", default=1)
    retain_path = serializers.CharField(
        help_text="文件保存路径", default="/data/omp/data/backup/",
        min_length=2,
        error_messages={
            "required": "必须包含[retain_path]字段",
            "min_length": "用户名长度需小于{min_length}"},
        validators=[
            ReValidator(regex=r"^/[-_/a-zA-Z0-9]+$"),
        ]
    )
    backup_custom = BackupCustomSerializer(many=True, required=False)

    def validate_retain_path(self, retain_path):  # NOQA
        try:
            folder = os.path.exists(retain_path)
            if not folder:
                os.makedirs(retain_path)
            file_path = os.path.join(retain_path, 'test.txt')
            create_file = open(file_path, "w")
            create_file.close()
        except Exception as e:
            logger.info(f"校验文件夹权限失败：{str(e)}")
            raise ValidationError(f"请确定程序对备份文件保存文件夹{retain_path}有读写权限！")
        return retain_path

    def validate_crontab_detail(self, crontab_detail):  # NOQA
        #
        # ToDo暂时不校验但有校验的必要
        return crontab_detail

    class Meta:
        model = BackupSetting
        fields = (
            "id", "backup_instances", "crontab_detail", "retain_day",
            "retain_path", "backup_custom", "is_on"
        )
