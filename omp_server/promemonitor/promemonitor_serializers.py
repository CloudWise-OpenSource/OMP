from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, ListSerializer
from rest_framework.exceptions import ValidationError
#from rest_framework.serializers import ValidationError
from db_models.models import MonitorUrl


class MonitorUrlSerializer(ListSerializer):

    def to_internal_value(self, data):
        return data

    def validate(self, data):
        queryset = MonitorUrl.objects.all()
        Method=self.context["request"].method
        for i in data:
            if Method in ('PATCH', 'PUT', 'DELETE'):
                if not i.get("id"):
                    raise serializers.ValidationError(f"id是必须字段")
            monitor_url=i.get("monitor_url")
            if Method != 'GET':
                if not monitor_url:
                    raise serializers.ValidationError(f"monitor_url是必须字段")
                if len(monitor_url) > 128:
                    raise serializers.ValidationError(f"monitor_url字段超过128,detail:{monitor_url}")
                name=i.get("name")
                if name:
                    if queryset.filter(name=name).exists():
                        raise serializers.ValidationError(f"name字段已经存在,detail:{name}")
                    if len(name) > 32:
                        raise serializers.ValidationError(f"name字段长度超过32,detail:{name}")  
                else:
                    raise serializers.ValidationError("name字段不为空")
        return data

    def create(self, validated_data):
        monitor = [MonitorUrl(**item) for item in validated_data]
        return MonitorUrl.objects.bulk_create(monitor)


class MonitorUrlSerializer(ModelSerializer):
    """ 监控配置项序列化 """
    name = serializers.CharField(
        max_length=32, required=True,
        error_messages={"invalid": "监控名字重复"},
        help_text="监控名字")
    id = serializers.IntegerField(
        max_value=100, required=False,
        error_messages={"invalid": "id格式不正确"},
        help_text="id")
    monitor_url = serializers.CharField(
        required=True,
        error_messages={"invalid": "监控地址格式不正确"},
        help_text="监控地址")

    class Meta:
        model = MonitorUrl
        fields = "__all__"
        list_serializer_class = MonitorUrlSerializer

    def validate_name(self, name):
        """ 校验name是否重复 """
        queryset = MonitorUrl.objects.all()
        if self.instance is not None:
            queryset = queryset.exclude(id=self.instance.id)
        if queryset.filter(name=name).exists():
            raise ValidationError("name已经存在")
        return name
