from rest_framework.routers import DefaultRouter

from services.views import (
    ServiceListView, ServiceDetailView,
    ServiceActionView, ServiceDeleteView
)

router = DefaultRouter()
router.register("services", ServiceListView, basename="services")
router.register("services", ServiceDetailView, basename="services")
router.register("action", ServiceActionView, basename="action")
router.register("delete", ServiceDeleteView, basename="delete")
