from django.urls import path

from service_upgrade.views import UpgradeChoiceMaxVersionListAPIView, \
    UpgradeHistoryListAPIView, UpgradeHistoryDetailAPIView, DoUpgradeAPIView, \
    RollbackHistoryListAPIView, RollbackHistoryDetailAPIView, \
    RollbackChoiceListAPIView, DoRollbackAPIView

upgrade_urlpatterns = [
    path('history', UpgradeHistoryListAPIView.as_view(), name="history"),
    path(
        'history/<int:pk>',
        UpgradeHistoryDetailAPIView.as_view(),
        name="detail"),
    path(
        'can-upgrade',
        UpgradeChoiceMaxVersionListAPIView.as_view(),
        name="can-upgrade"),
    path('do-upgrade', DoUpgradeAPIView.as_view(), name="do-upgrade")
]

rollback_urlpatterns = [
    path('history', RollbackHistoryListAPIView.as_view(), name="history"),
    path(
        'history/<int:pk>',
        RollbackHistoryDetailAPIView.as_view(),
        name="detail"),
    path(
        'can-rollback',
        RollbackChoiceListAPIView.as_view(),
        name="can-rollback"),
    path('do-rollback', DoRollbackAPIView.as_view(), name="do-rollback")
]
