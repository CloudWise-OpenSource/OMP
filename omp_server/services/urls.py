from rest_framework.routers import DefaultRouter

from services.views import (
    ServiceListView, ServiceDetailView
)

router = DefaultRouter()
router.register("services", ServiceListView, basename="services")
router.register("services", ServiceDetailView, basename="services")
