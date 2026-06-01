from django.urls import path

from .views import AdminCreditAdjustView, CreditRecordListView, CreditSummaryView

urlpatterns = [
    path("", CreditRecordListView.as_view(), name="credit-list"),
    path("summary/", CreditSummaryView.as_view(), name="credit-summary"),
    path("admin/adjust/", AdminCreditAdjustView.as_view(), name="credit-admin-adjust"),
]
