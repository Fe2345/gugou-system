from django.urls import path

from .admin_views import AdminPriceHistoryView, AdminPriceRecordListView

urlpatterns = [
    path("", AdminPriceRecordListView.as_view(), name="admin-price-record-list"),
    path("history/", AdminPriceHistoryView.as_view(), name="admin-price-history"),
]
