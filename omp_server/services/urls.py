from django.urls import path
from rest_framework.routers import DefaultRouter

from services.views import (
    ServiceListView, ServiceDetailView,
    ServiceActionView, ServiceDeleteView,
    ServiceStatusView, ServiceDataJsonView,
    AppListView, AppConfCheckView,
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
                UpdateSelfHealingHistoryView,
                basename="UpdateSelfHealingHistory")
router.register("serviceStatus", ServiceStatusView, basename="serviceStatus")

# Accept_manager
router.register("appList", AppListView, basename="appList")
router.register("appConfCheck", AppConfCheckView, basename="appConfCheck")

urlpatterns = [
    path('data_json', ServiceDataJsonView.as_view(), name="serviceDataJson")
]

urlpatterns += router.urls
