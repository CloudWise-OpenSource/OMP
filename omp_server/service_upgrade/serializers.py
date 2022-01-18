from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from db_models.mixins import UpgradeStateChoices, RollbackStateChoices
from db_models.models import UpgradeHistory, UpgradeDetail, Service, \
    ApplicationHub, RollbackHistory, RollbackDetail
from utils.parse_config import BASIC_ORDER


class UpgradeHistorySerializer(serializers.ModelSerializer):
    service_count = serializers.SerializerMethodField()
    operator = serializers.CharField(source="operator.username")
    state_display = serializers.CharField(source="get_upgrade_state_display")
    can_rollback = serializers.BooleanField(source="can_roll_back")

    def get_service_count(self, obj):
        return obj.upgradedetail_set.all().count()

    class Meta:
        model = UpgradeHistory
        fields = ("id", "operator", "service_count", "upgrade_state",
                  "created", "can_rollback", "state_display")


class RollbackHistorySerializer(serializers.ModelSerializer):
    service_count = serializers.SerializerMethodField()
    operator = serializers.CharField(source="operator.username")
    state_display = serializers.CharField(source="get_rollback_state_display")

    def get_service_count(self, obj):
        return obj.rollbackdetail_set.all().count()

    class Meta:
        model = RollbackHistory
        fields = ("id", "operator", "service_count", "rollback_state",
                  "created", "state_display")


class UpgradeDetailSerializer(serializers.ModelSerializer):

    ip = serializers.CharField(source="service.ip")
    service_name = serializers.CharField(source="service.service.app_name")
    state_display = serializers.CharField(source="get_upgrade_state_display")
    instance_name = serializers.CharField(source="service.service_instance_name")

    class Meta:
        model = UpgradeDetail
        fields = ("id", "ip", "service_name", "upgrade_state", "message",
                  "state_display", "instance_name")


class RollbackDetailSerializer(serializers.ModelSerializer):

    ip = serializers.CharField(source="upgrade.service.ip")
    service_name = serializers.CharField(source="upgrade.target_app.app_name")
    state_display = serializers.CharField(source="get_rollback_state_display")
    instance_name = serializers.CharField(
        source="upgrade.service.service_instance_name")

    class Meta:
        model = RollbackDetail
        fields = ("id", "ip", "service_name", "rollback_state", "message",
                  "state_display", "instance_name")


class UpgradeHistoryDetailSerializer(serializers.ModelSerializer):
    operator = serializers.CharField(source="operator.username")
    upgrade_detail = serializers.SerializerMethodField()
    can_rollback = serializers.SerializerMethodField()
    success_count = serializers.SerializerMethodField()
    all_count = serializers.SerializerMethodField()

    def get_upgrade_details(self, obj, key):
        if hasattr(obj, key):
            return getattr(obj, key)
        details = obj.upgradedetail_set.all()
        upgrade_details = UpgradeDetailSerializer(details, many=True).data
        # 合并服务
        upgrade_result = {}
        success_count = all_count = 0
        for detail in upgrade_details:
            all_count += 1
            if detail.get("upgrade_state") ==\
                    UpgradeStateChoices.UPGRADE_SUCCESS:
                success_count += 1
            if detail.get("service_name") not in upgrade_result:
                upgrade_result[detail.get("service_name")] = [detail]
            else:
                upgrade_result[detail.get("service_name")].append(detail)
        setattr(obj, "success_count", success_count)
        setattr(obj, "all_count", all_count)
        setattr(obj, "upgrade_result", upgrade_result)
        return getattr(obj, key)

    def get_upgrade_detail(self, obj):
        result = self.get_upgrade_details(obj, "upgrade_result")
        # 获取服务顺序
        service_index = {}
        sum_index = 0
        for index, services in BASIC_ORDER.items():
            for sub_index, service in enumerate(services, sum_index):
                service_index[service] = sub_index
                sum_index += 1
        # 升级记录排序
        results = sorted(
            result.items(),
            key=lambda x: service_index.get(x[0], sum_index+1)
        )
        # 调整返回数据结构
        return [
            {
                "service_name": service_tmp[0],
                "upgrade_details": service_tmp[1]
            } for service_tmp in results
        ]

    def get_can_rollback(self, obj):
        return obj.can_roll_back

    def get_success_count(self, obj):
        return self.get_upgrade_details(obj, "success_count")

    def get_all_count(self, obj):
        return self.get_upgrade_details(obj, "all_count")

    class Meta:
        model = UpgradeHistory
        fields = ("id", "operator", "upgrade_detail", "upgrade_state",
                  "created", "can_rollback", "success_count",
                  "all_count")


class RollbackHistoryDetailSerializer(serializers.ModelSerializer):
    operator = serializers.CharField(source="operator.username")
    rollback_detail = serializers.SerializerMethodField()
    success_count = serializers.SerializerMethodField()
    all_count = serializers.SerializerMethodField()

    def get_rollback_details(self, obj, key):
        if hasattr(obj, key):
            return getattr(obj, key)
        details = obj.rollbackdetail_set.all()
        rollback_details = RollbackDetailSerializer(details, many=True).data
        # 合并服务
        rollback_result = {}
        success_count = all_count = 0
        for detail in rollback_details:
            all_count += 1
            if detail.get("rollback_state") ==\
                    RollbackStateChoices.ROLLBACK_SUCCESS:
                success_count += 1
            if detail.get("service_name") not in rollback_result:
                rollback_result[detail.get("service_name")] = [detail]
            else:
                rollback_result[detail.get("service_name")].append(detail)
        setattr(obj, "success_count", success_count)
        setattr(obj, "all_count", all_count)
        setattr(obj, "rollback_result", rollback_result)
        return getattr(obj, key)

    def get_rollback_detail(self, obj):
        result = self.get_rollback_details(obj, "rollback_result")
        # 获取服务顺序
        service_index = {}
        sum_index = 0
        for index, services in BASIC_ORDER.items():
            for sub_index, service in enumerate(services, sum_index):
                service_index[service] = sub_index
                sum_index += 1
        # 升级记录排序
        results = sorted(
            result.items(),
            key=lambda x: service_index.get(x[0], sum_index+1)
        )
        # 调整返回数据结构
        return [
            {
                "service_name": service_tmp[0],
                "rollback_details": service_tmp[1]
            } for service_tmp in results
        ]

    def get_success_count(self, obj):
        return self.get_rollback_details(obj, "success_count")

    def get_all_count(self, obj):
        return self.get_rollback_details(obj, "all_count")

    class Meta:
        model = RollbackHistory
        fields = ("id", "operator", "rollback_detail", "rollback_state",
                  "created",  "success_count",  "all_count")


class UpgradeTryAgainSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = UpgradeHistory
        fields = ("id", )

    def validate(self, attrs):
        if self.instance.upgrade_state != UpgradeStateChoices.UPGRADE_FAIL:
            raise ValidationError("该升级记录不支持重新再次升级!")
        histories = UpgradeHistory.objects.filter(
            upgrade_state__in=[
                UpgradeStateChoices.UPGRADE_WAIT,
                UpgradeStateChoices.UPGRADE_ING
            ]
        )
        if histories.exists():
            raise ValidationError("存在正在升级的服务，请稍后重试!")
        if UpgradeHistory.objects.filter(id__gt=self.instance.id).exists():
            raise ValidationError("历史记录不可再次升级!")
        return True


class RollbackTryAgainSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = RollbackHistory
        fields = ("id", )

    def validate(self, attrs):
        if self.instance.rollback_state != RollbackStateChoices.ROLLBACK_FAIL:
            raise ValidationError("该回滚记录不支持重新再次回滚!")
        if RollbackHistory.objects.filter(id__gt=self.instance.id).exists():
            raise ValidationError("历史记录不可再次回滚!")
        return True


class ApplicationHubSerializer(serializers.ModelSerializer):
    app_id = serializers.IntegerField(source="id")

    class Meta:
        model = ApplicationHub
        fields = ("app_id", "app_name", "app_version")


class ServiceSerializer(serializers.ModelSerializer):
    service_id = serializers.IntegerField(source="id")
    instance_name = serializers.CharField(source="service_instance_name")
    app_name = serializers.CharField(source="service.app_name")
    app_id = serializers.IntegerField(source="service.id")
    version = serializers.CharField(source="service.app_version")

    class Meta:
        model = Service
        fields = ("service_id", "ip", "instance_name", "app_name", "version",
                  "app_id")


class RollbackListSerializer(serializers.ModelSerializer):

    before_rollback_v = serializers.CharField(source="target_app.app_version")
    after_rollback_v = serializers.CharField(source="current_app.app_version")
    app_name = serializers.CharField(source="target_app.app_name")
    ip = serializers.CharField(source="service.ip")
    instance_name = serializers.CharField(source="service.service_instance_name")

    class Meta:
        model = UpgradeDetail
        fields = ("id", "ip", "service_id", "app_name", "before_rollback_v",
                  "after_rollback_v", "instance_name")
