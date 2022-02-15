from rest_framework.routers import DefaultRouter

from utils.common.views import UploadFileAPIView

router = DefaultRouter()
router.register(r'upload_file', UploadFileAPIView, basename="upload_file")
urlpatterns = router.urls
