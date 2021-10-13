# -*- coding:utf-8 -*-
# Project: app_store_serializers
# Author:Times.niu@yunzhihui.com
# Create time: 2021/10/13 10:14 上午

import logging
import os
from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from db_models.models import UploadPackageHistory
from rest_framework.serializers import Serializer
from utils.exceptions import OperateError


class UploadPackageSerializer(Serializer):
    """上传安装包序列化类"""

    uuid = serializers.UUIDField(
        help_text="上传安装包uuid",
        required=True,
        error_messages={"required": "必须包含[uuid]字段"}
    )
    operation_user = serializers.CharField(
        help_text="操作用户",
        required=True,
        error_messages={"required": "必须包含[operation_user]字段"}
    )
    file = serializers.FileField(
        help_text="上传的文件",
        required=True,
        error_messages={"required": "必须包含[file]字段"}
    )

    def validate(self, attrs):
        file = attrs.get("file")
        file_name = file.name
        file_size = file.size
        if not file_name.endswith('.tar') and not file_name.endswith('tar.gz'):
            raise ValidationError({
                "file_name": "上传文件名仅支持.tar或.tar.gz"
            })
        # 文件大小超过4G不支持
        if file_size > 4294967296:
            raise ValidationError({
                "file_size": "上传文件大小超过4G"
            })
        return attrs

    def create(self, validated_data):
        request_file = validated_data.get("file")
        if not request_file:
            raise OperateError(f"上传文件为空")
        destination_dir = os.path.join(settings.PROJECT_DIR, 'package_hub/back_end_verified')
        with open(os.path.join(destination_dir, request_file.name), 'wb+') as f:
            for chunk in request_file.chunks():
                try:
                    f.write(chunk)
                except Exception as e:
                    raise OperateError(f"文件写入过程失败")
        return validated_data
