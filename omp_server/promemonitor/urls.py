"""
监控相关的路由
"""
from rest_framework.routers import DefaultRouter

from promemonitor.custom_script_views import CustomScriptViewSet, CustomScriptJobInfoView
from promemonitor.views import (
    MonitorUrlViewSet, ListAlertViewSet, UpdateAlertViewSet,
    MaintainViewSet, ReceiveAlertViewSet,
    MonitorAgentRestartView, GrafanaUrlViewSet, InstanceNameListView,
    InstrumentPanelView, GetSendEmailConfig, UpdateSendEmailConfig,
    GetSendAlertSettingView, UpdateSendAlertSettingView, HostThresholdView,
    ServiceThresholdView, CustomThresholdView, BuiltinsRuleView, QuotaView, PromSqlTestView, BatchUpdateRuleView
)

router = DefaultRouter()
router.register(r'monitorurl', MonitorUrlViewSet)
router.register(r'listAlert', ListAlertViewSet, basename='listAlert')
router.register(r'updateAlert', UpdateAlertViewSet, basename='updateAlert')
router.register(r'restartMonitorAgent',
                MonitorAgentRestartView, basename="restartMonitorAgent")
router.register("globalMaintain", MaintainViewSet, basename='globalMaintain')
router.register(r'receiveAlert', ReceiveAlertViewSet,
                basename='receiveAlert')
router.register(r'grafanaurl', GrafanaUrlViewSet, basename="grafanaurl")
router.register(r'instanceNameList', InstanceNameListView,
                basename='instanceNameList')
router.register(r"instrumentPanel", InstrumentPanelView,
                basename="instrumentPanel")
router.register(r'getSendEmailConfig', GetSendEmailConfig,
                basename='getSendEmailConfig')
router.register(r'updateSendEmailConfig', UpdateSendEmailConfig,
                basename='updateSendEmailConfig')
router.register(r'getSendAlertSetting', GetSendAlertSettingView,
                basename='getSendAlertSetting')
router.register(r'updateSendAlertSetting',
                UpdateSendAlertSettingView, basename='updateSendAlertSetting')
router.register(r'hostThreshold', HostThresholdView, basename='hostThreshold')
router.register(r'serviceThreshold', ServiceThresholdView,
                basename='serviceThreshold')
router.register(r'customThreshold', CustomThresholdView,
                basename='customThreshold')
router.register(r'customScript', CustomScriptViewSet, basename='customScript')
router.register(r'customScriptJobInfo', CustomScriptJobInfoView,
                basename='customScriptJobInfo')
router.register(r'builtinRule', BuiltinsRuleView, basename="builtinRule")
router.register(r'quota', QuotaView, basename="quota")
router.register(r'testPromSql', PromSqlTestView, basename="testPromSql")
router.register(r'batchUpdateRule', BatchUpdateRuleView,
                basename="batchUpdateRule")

urlpatterns = router.urls
