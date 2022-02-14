import logging
import traceback

from django.db import models, transaction
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView, GenericAPIView,\
    RetrieveUpdateAPIView
from rest_framework.response import Response

from db_models.mixins import UpgradeStateChoices, RollbackStateChoices
from db_models.models import UpgradeHistory, Service, ApplicationHub, Env, \
    UpgradeDetail, RollbackHistory, RollbackDetail
from utils.common.exceptions import GeneralError
from utils.common.paginations import PageNumberPager
from .filters import RollBackHistoryFilter
from .serializers import UpgradeHistorySerializer, ServiceSerializer, \
    UpgradeHistoryDetailSerializer,  ApplicationHubSerializer, \
    UpgradeTryAgainSerializer, RollbackHistorySerializer, \
    RollbackHistoryDetailSerializer, RollbackTryAgainSerializer, \
    RollbackListSerializer
from .tasks import upgrade_service, rollback_service

logger = logging.getLogger(__name__)


class UpgradeHistoryListAPIView(ListAPIView):
    # 升级历史记录
    pagination_class = PageNumberPager
    queryset = UpgradeHistory.objects.all()\
        .prefetch_related("upgradedetail_set")
    filter_backends = (OrderingFilter, )
    serializer_class = UpgradeHistorySerializer
    ordering_fields = ("-id", )
    get_description = "升级历史记录页"


class UpgradeHistoryDetailAPIView(RetrieveUpdateAPIView):
    # 升级历史记录详情
    queryset = UpgradeHistory.objects.all()\
        .prefetch_related("upgradedetail_set")
    serializer_class = UpgradeHistoryDetailSerializer
    lookup_url_kwarg = 'pk'
    get_description = "升级历史记录详情页"
    put_description = "升级重试"

    def update(self, request, *args, **kwargs):
        # put 升级重试
        instance = self.get_object()
        serializer = UpgradeTryAgainSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        upgrade_service.delay(instance.id)
        return Response()


class UpgradeChoiceAllVersionListAPIView(GenericAPIView):
    # 可升级服务列表（可选择升级的目标）
    queryset = Service.objects.filter(
        service_status__in=[0, 1, 2, 3, 4, 9]
    ).select_related("service")
    filter_backends = (SearchFilter, )
    search_fields = ("service__app_name",)
    get_description = "可升级服务列表"

    def get_service_info(self, services_data):
        """
        确定已安装服务最小版本，缩小查询范围及组装数据
        """
        service_min_app_ids, services_versions = {}, {}
        for service_data in services_data:
            app_name = service_data.get("app_name")
            app_id = service_data.get("app_id")
            min_app_id = service_min_app_ids.get(app_name, None)
            if app_name not in services_versions:
                services_versions[app_name] = [service_data]
            else:
                services_versions[app_name].append(service_data)
            if min_app_id is None or app_id < min_app_id:
                service_min_app_ids[app_name] = app_id
        return services_versions, service_min_app_ids

    def get(self, requests):
        queryset = self.filter_queryset(self.get_queryset())
        services_data = ServiceSerializer(queryset, many=True).data
        if not services_data:
            return Response({"results": []})
        services_v, min_app_ids = self.get_service_info(
            services_data)
        # 查询服务可能存在可升级的安装包
        apps = ApplicationHub.objects.filter(
            id__gt=min(min_app_ids.values()),
            app_name__in=services_v.keys()
        ).order_by("-id").exclude(id__in=min_app_ids.values())
        if not apps:
            return Response({"results": []})
        # 确定服务可升级的安装包
        apps_data = ApplicationHubSerializer(apps, many=True).data
        for app_data in apps_data:
            app_id = app_data.get("app_id")
            app_name = app_data.pop("app_name")
            if min_app_ids.get(app_name, float("inf")) >= app_id:
                apps_data.remove(app_data)
                continue
            for service_v in services_v.get(app_name):
                if service_v.get("app_id", float("inf")) >= app_id:
                    continue
                if "can_upgrade" not in service_v:
                    service_v["can_upgrade"] = [app_data]
                else:
                    service_v["can_upgrade"].append(app_data)
        # 格式化数据，排除不可升级服务
        results = []
        # {"a": [{""}, {}]}
        for app_name, services in services_v.items():
            if not services:
                services_v.pop(app_name)
            upgrade_services = []
            for service in services:
                if service.get("can_upgrade"):
                    upgrade_services.append(service)
            if upgrade_services:
                results.append(
                    {"app_name": app_name, "children": upgrade_services}
                )
        # results: [{"app_name": a, "service": [{"can_upgrade": []...}]
        return Response({"results": results})


class UpgradeChoiceMaxVersionListAPIView(UpgradeChoiceAllVersionListAPIView):
    # 可升级服务列表（只展示可供升级的最高版本）
    get_description = "可升级服务列表"

    def get_service_max_app(self, apps):
        max_apps = {}
        for app in apps:
            app_info = max_apps.get(app["app_name"], {})
            if app_info.get("app_id", float("-inf")) <= app["app_id"]:
                max_apps[app["app_name"]] = app
        return max_apps

    def get(self, requests):
        queryset = self.filter_queryset(self.get_queryset())
        services_data = ServiceSerializer(queryset, many=True).data
        if not services_data:
            return Response({"results": []})
        services_v, min_app_ids = self.get_service_info(
            services_data)
        # 查询服务可能存在可升级的安装包
        apps = ApplicationHub.objects.filter(
            id__gt=min(min_app_ids.values()),
            app_name__in=services_v.keys()
        ).order_by("-id").exclude(id__in=min_app_ids.values())
        if not apps:
            return Response({"results": []})
        # 确定服务可升级的安装包
        apps_data = ApplicationHubSerializer(apps, many=True).data
        max_apps_dict = self.get_service_max_app(apps_data)
        results = []
        for app_name, max_app in max_apps_dict.items():
            services = services_v.get(app_name)
            upgrade_services = []
            for service_v in services:
                if service_v.get("app_id", float("inf")) >= max_app["app_id"]:
                    continue
                service_v["can_upgrade"] = [max_app]
                upgrade_services.append(service_v)
            if upgrade_services:
                results.append(
                    {
                        "app_name": app_name,
                        "children": upgrade_services,
                        "can_upgrade": max_app
                    }
                )
        return Response({"results": results})


class DoUpgradeAPIView(GenericAPIView):
    post_description = "升级服务"

    def valid_can_upgrade(self, data):
        # todo：校验升级依赖
        # 校验信息
        services = list(
            Service.objects.filter(
                id__in=data.keys(),
                service_status__in=[0, 1, 2, 3, 4]
            ).annotate(
                app_name=models.F("service__app_name"),
                current_app_id=models.F("service_id")
            ).values("id", "app_name", "ip", "current_app_id")
        )
        if not services:
            raise GeneralError("请选择需要升级的服务！")
        apps = ApplicationHub.objects.filter(
            id__in=data.values(),
            is_release=True
        ).values("id", "app_name", "app_version")
        app_dict = {}
        for app in apps:
            app_dict[app.get("app_name")] = {"target_app_id": app.get("id")}
        for service in services:
            app_name = service.get("app_name")
            if app_dict.get(app_name, {}).get("target_app_id", float("-inf"))\
                    <= service["current_app_id"]:
                raise GeneralError(f"服务{app_name}升级版本小于或等于当前版本！")
            service.update(app_dict.get(app_name))
        return services

    def post(self, requests):
        if UpgradeHistory.objects.filter(
            upgrade_state__in=[
                UpgradeStateChoices.UPGRADE_WAIT,
                UpgradeStateChoices.UPGRADE_ING,
            ]
        ).exists():
            raise GeneralError("存在正在升级的服务，请稍后！")
        if RollbackHistory.objects.filter(
            rollback_state__in=[
                RollbackStateChoices.ROLLBACK_WAIT,
                RollbackStateChoices.ROLLBACK_ING,
            ]
        ).exists():
            raise GeneralError("存在正在回滚的服务，请稍后！")
        if UpgradeDetail.objects.filter(
                upgrade_state=UpgradeStateChoices.UPGRADE_FAIL
        ).exclude(has_rollback=True).exists():
            raise GeneralError("存在升级失败的服务，请继续升级或回滚！")
        choices = requests.data.get("choices", [])
        if not choices:
            raise GeneralError("请选择需要升级的服务！")
        try:
            data = {}
            for choice in choices:
                if choice.get("service_id") in data:
                    raise KeyError(f'{choice.get("service_id")}重复！')
                data[choice.get("service_id")] = choice.get("app_id")
        except Exception as e:
            logger.error(
                f"解析升级数据错误：{str(e)}, 详情为：\n{traceback.format_exc()}")
            raise GeneralError("解析升级数据错误！")
        services = self.valid_can_upgrade(data)
        with transaction.atomic():
            history = UpgradeHistory.objects.create(
                env=Env.objects.first(),
                operator=requests.user
            )
            details = []
            for service in services:
                service_id = service.pop("id")
                app_name = service.pop("app_name")
                ip = service.pop("ip")
                details.append(
                    UpgradeDetail(
                        history=history,
                        service_id=service_id,
                        union_server=f"{ip}-{app_name}",
                        **service,
                    )
                )
            UpgradeDetail.objects.bulk_create(details)
        upgrade_service.delay(history.id)
        # todo: update data.json && ???
        return Response({"history": history.id})


class RollbackHistoryListAPIView(ListAPIView):
    pagination_class = PageNumberPager
    queryset = RollbackHistory.objects.all()\
        .prefetch_related("rollbackdetail_set")
    filter_backends = (OrderingFilter, )
    serializer_class = RollbackHistorySerializer
    ordering_fields = ("-id", )
    get_description = "回滚历史记录页"


class RollbackHistoryDetailAPIView(RetrieveUpdateAPIView):
    queryset = RollbackHistory.objects.all()\
        .prefetch_related("rollbackdetail_set")
    serializer_class = RollbackHistoryDetailSerializer
    lookup_url_kwarg = 'pk'
    get_description = "回滚历史记录详情页"
    put_description = "回滚重试"

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = RollbackTryAgainSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        rollback_service.delay(instance.id)
        return Response()


class RollbackChoiceListAPIView(GenericAPIView):
    queryset = UpgradeDetail.objects.filter(
        upgrade_state__in=[
            UpgradeStateChoices.UPGRADE_SUCCESS,
            UpgradeStateChoices.UPGRADE_FAIL
        ]
    ).exclude(has_rollback=True).exclude(service__isnull=True)
    filter_backends = (SearchFilter, RollBackHistoryFilter)
    search_fields = ("target_app__app_name", )
    get_description = "可回滚服务列表页"

    def get(self, requests):
        queryset = self.filter_queryset(self.get_queryset())
        upgrades_data = RollbackListSerializer(queryset, many=True).data
        service_id_max_d, service_name_max_d = {}, {}
        for upgrade_data in upgrades_data:
            service_id = upgrade_data.get("service_id")
            detail_id = upgrade_data.get("id")
            app_name = upgrade_data.get("app_name")
            service_max_data = service_id_max_d.get(service_id, {})
            if service_max_data.get("id", float("-inf")) > detail_id:
                continue
            service_id_max_d[service_id] = upgrade_data
            if app_name not in service_name_max_d:
                service_name_max_d[app_name] = {service_id: upgrade_data}
            else:
                service_name_max_d[app_name].update({service_id: upgrade_data})
        response_data = [
            {"app_name": app_name, "children": list(max_info.values())}
            for app_name, max_info in service_name_max_d.items()
        ]
        return Response(data={"results": response_data})


class DoRollbackAPIView(GenericAPIView):
    get_description = "回滚服务"

    def post(self, requests):
        if UpgradeHistory.objects.filter(
            upgrade_state__in=[
                UpgradeStateChoices.UPGRADE_WAIT,
                UpgradeStateChoices.UPGRADE_ING,
            ]
        ).exists():
            raise GeneralError("存在正在升级的服务，请稍后！")
        if RollbackHistory.objects.filter(
            rollback_state__in=[
                RollbackStateChoices.ROLLBACK_WAIT,
                RollbackStateChoices.ROLLBACK_ING,
            ]
        ).exists():
            raise GeneralError("存在正在回滚的服务，请稍后！")
        choices = requests.data.get("choices", [])
        if not choices:
            raise GeneralError("请选择需要回滚的记录！")
        upgrade_details = UpgradeDetail.objects.filter(
            id__in=choices,
            upgrade_state__in=[
                UpgradeStateChoices.UPGRADE_SUCCESS,
                UpgradeStateChoices.UPGRADE_FAIL
            ]
        ).values("id", "current_app_id", "union_server")
        if upgrade_details.count() != len(choices):
            raise GeneralError("提交信息校验失败，请刷新重试！")
        # 校验同一个服务是否回滚至同一版本
        union_app = {}
        for detail in upgrade_details:
            rollback_app_id = detail.get("current_app_id")
            union_server = detail.get("union_server")
            if not union_server:
                raise GeneralError(f"实例{union_server}不在平台纳管范围！")
            if not union_app.get(union_server):
                union_app[union_server] = rollback_app_id
                continue
            if union_app.get(union_server) != rollback_app_id:
                raise GeneralError(f"实例{union_server}将回滚的服务版本不一致！")
        with transaction.atomic():
            history = RollbackHistory.objects.create(
                env=Env.objects.first(),
                operator=requests.user
            )
            RollbackDetail.objects.bulk_create(
                [
                    RollbackDetail(
                        history=history,
                        upgrade_id=upgrade_detail.get("id")
                    )
                    for upgrade_detail in upgrade_details
                ]
            )
        rollback_service.delay(history.id)
        # todo: rollback data.json && 升级、回滚过程中禁止取消维护模式
        return Response({"history": history.id})
