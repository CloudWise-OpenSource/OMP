from rest_framework.routers import DefaultRouter

from tool.views import GetToolDetailView

router = DefaultRouter()
router.register(r'result', GetToolDetailView, basename="services")
