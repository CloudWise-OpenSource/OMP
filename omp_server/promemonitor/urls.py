"""
监控相关的路由
"""
from rest_framework.routers import DefaultRouter
from promemonitor.views import MonitorUrlViewSet, AlertViewSet


router = DefaultRouter()
router.register(r'monitorurl', MonitorUrlViewSet)
router.register(r'alerts', AlertViewSet)

urlpatterns = router.urls
