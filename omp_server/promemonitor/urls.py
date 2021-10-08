"""
监控相关的路由
"""
from rest_framework.routers import DefaultRouter
from promemonitor.views import MonitorUrlViewSet, AlertViewSet, MaintainViewSet, ReceiveAlert

from django.urls import path


router = DefaultRouter()
router.register(r'monitorurl', MonitorUrlViewSet)
router.register(r'alerts', AlertViewSet)
router.register("global_maintain", MaintainViewSet, basename='global_maintain')
router.urls.append(path('receive_alert', ReceiveAlert.as_view()))
urlpatterns = router.urls
