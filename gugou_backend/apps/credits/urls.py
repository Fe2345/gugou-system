from django.urls import path

from .views import CreditRecordListView, CreditSummaryView

urlpatterns = [
    path("", CreditRecordListView.as_view(), name="credit-list"),
    path("summary/", CreditSummaryView.as_view(), name="credit-summary"),
]
