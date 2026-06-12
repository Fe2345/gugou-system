from django.urls import path

from .admin_views import AdminDashboardStatsView

urlpatterns = [
    path("", AdminDashboardStatsView.as_view(), name="admin-dashboard-stats"),
]
