from rest_framework.routers import DefaultRouter

from tool.views import GetToolDetailView, ToolFormDetailAPIView

router = DefaultRouter()
router.register(r'result', GetToolDetailView, basename="result")
router.register(r'form', ToolFormDetailAPIView, basename="form")
urlpatterns = router.urls
