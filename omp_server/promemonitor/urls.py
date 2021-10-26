"""
监控相关的路由
"""
from rest_framework.routers import DefaultRouter
from promemonitor.views import (
    MonitorUrlViewSet, ListAlertViewSet, UpdateAlertViewSet,
    MaintainViewSet, ReceiveAlertViewSet,
    MonitorAgentRestartView, GrafanaUrlViewSet, InstanceNameListView, InstrumentPanelView
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
urlpatterns = router.urls
