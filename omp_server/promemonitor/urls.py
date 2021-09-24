from rest_framework.routers import DefaultRouter
from promemonitor.views import MonitorUrlViewSet

"""
监控相关的路由
"""

router = DefaultRouter()
router.register(r'monitorurl', MonitorUrlViewSet)

urlpatterns = router.urls
