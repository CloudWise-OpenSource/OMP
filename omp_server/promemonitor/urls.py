"""
监控相关的路由
"""
from rest_framework.routers import DefaultRouter
from promemonitor.views import (
    MonitorUrlViewSet, AlertViewSet,
    MaintainViewSet, ReceiveAlertViewSet,
    MonitorAgentRestartView, GrafanaUrlViewSet, InstanceNameListView
)

router = DefaultRouter()
router.register(r'monitorurl', MonitorUrlViewSet)
router.register(r'alerts', AlertViewSet, basename='alerts')
router.register(r'restartMonitorAgent',
                MonitorAgentRestartView, basename="restartMonitorAgent")
router.register("global_maintain", MaintainViewSet, basename='global_maintain')
router.register(r'receive_alert', ReceiveAlertViewSet,
                basename='receive_alert')
router.register(r'grafanaurl', GrafanaUrlViewSet, basename="grafanaurl")
router.register(r'instanceNameList', InstanceNameListView,
                basename='instanceNameList')
urlpatterns = router.urls
