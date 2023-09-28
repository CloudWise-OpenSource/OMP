"""
公共序列化器
"""

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from db_models import models
from db_models.models import Host, UploadFileHistory


class HostIdsSerializer(serializers.Serializer):
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


class UploadFileSerializer(serializers.Serializer):
    file = serializers.FileField(
        help_text="上传的文件",
        required=True,
        error_messages={"required": "必须包含[file]字段"}
    )
    storage_klass = serializers.CharField(
        help_text="存储方式", required=False, default="location")
    module = serializers.CharField(
        help_text="需要上传文件的model", required=False, default="")
    module_id = serializers.IntegerField(
        help_text="需要上传文件的model id", required=False, default=0)
    file_name = serializers.CharField(
        help_text="保存后文件名", required=False, default="")
    file_url = serializers.CharField(
        help_text="保存后文件访问路径", required=False, default="")
    union_id = serializers.CharField(
        help_text="文件union_id", required=False, default="")

    def validate(self, attrs):
        module = attrs.get("module")
        module_id = attrs.get("module_id")
        if module:
            _obj = getattr(models, module).objects.filter(id=module_id).first()
            if not _obj:
                raise ValidationError({
                    "module": "请确定指定上传文件的module"
                })
            setattr(self, "module_obj", _obj)
        if attrs.get("storage_klass", "location") \
                not in UploadFileHistory.STORAGE_KLASS:
            raise ValidationError({
                "storage_klass":
                    f"文件存储方式目前只支持{UploadFileHistory.STORAGE_KLASS}"
            })
        return attrs

    def create(self, validated_data):
        user = self.context.get("request").user
        file = validated_data.get("file")
        if hasattr(self, "module_obj"):
            module_obj = self.module_obj
        else:
            module_obj = None
        obj = getattr(
            UploadFileHistory,
            validated_data.get("storage_klass", "location")
        )(file, module_obj, user)
        validated_data.update(
            {
                "file_name": obj.file_name,
                "union_id": obj.union_id,
                "file_url": obj.file_url
            }
        )
        return validated_data


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # 正常地实例化父类
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # 删除fields参数中未指定的任何字段
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
