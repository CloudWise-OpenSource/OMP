# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author:' Lingyang.guo'
# CreateDate: 14:26
import json

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from db_models.models.custom_metric import CustomScript


class CustomScriptSerializer(ModelSerializer):

    bound_hosts_num = serializers.SerializerMethodField()

    class Meta:
        model = CustomScript
        fields = "__all__"

    def get_bound_hosts_num(self, obj):  # NOQA
        bound_hosts = obj.bound_hosts
        if isinstance(bound_hosts, str):
            bound_hosts_num = len(json.loads(bound_hosts))
        else:
            bound_hosts_num = len(bound_hosts)
        return bound_hosts_num
