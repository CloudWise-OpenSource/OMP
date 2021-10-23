from rest_framework.routers import DefaultRouter

from services.views import (
    ServiceListView
)

router = DefaultRouter()
router.register("services", ServiceListView, basename="services")
