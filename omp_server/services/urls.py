from rest_framework.routers import DefaultRouter

from services.views import (
    ServiceListView, ServiceDetailView,
    ServiceActionView, ServiceDeleteView,
    ServiceStatusView
)
from services.self_heal_view import (
    SelfHealingSettingView, ListSelfHealingHistoryView,
    UpdateSelfHealingHistoryView
)

router = DefaultRouter()
router.register("services", ServiceListView, basename="services")
router.register("services", ServiceDetailView, basename="services")
router.register("action", ServiceActionView, basename="action")
router.register("delete", ServiceDeleteView, basename="delete")
router.register("SelfHealingSetting", SelfHealingSettingView,
                basename="SelfHealingSetting")
router.register("ListSelfHealingHistory",
                ListSelfHealingHistoryView, basename="ListSelfHealingHistory")
router.register("UpdateSelfHealingHistory",
                UpdateSelfHealingHistoryView, basename="UpdateSelfHealingHistory")
router.register("serviceStatus", ServiceStatusView, basename="serviceStatus")
