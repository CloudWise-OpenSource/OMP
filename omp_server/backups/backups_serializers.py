# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: lingyang guo
from rest_framework.serializers import ModelSerializer

from db_models.models import BackupHistory


class BackupHistorySerializer(ModelSerializer):
    class Meta:
        model = BackupHistory
        fields = "__all__"
        write_only_fields = ("id",)
