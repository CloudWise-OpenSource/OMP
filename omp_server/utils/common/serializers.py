"""
公共序列化器
"""

from rest_framework import serializers
from rest_framework.serializers import Serializer
from rest_framework.exceptions import ValidationError

from db_models.models import Host


class HostIdsSerializer(Serializer):
    """ 主机 id 列表序列化类 """

    host_ids = serializers.ListField(
        help_text="主机 ID 列表",
        required=True,
        error_messages={"required": "必须包含[host_ids]字段"},
        allow_empty=False)

    def validate_host_ids(self, host_ids):
        """ 校验主机 ID 列表中主机是否都存在 """
        exists_ids = Host.objects.filter(
            id__in=host_ids).values_list("id", flat=True)
        diff = set(host_ids) - set(exists_ids)
        if diff:
            raise ValidationError(
                f"主机列表中有不存在的ID ["
                f"{','.join(map(lambda x: str(x), diff))}"
                f"]")
        return host_ids
