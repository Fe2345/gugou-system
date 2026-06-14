from django.urls import path

from .admin_views import (
    AdminDashboardStatsView,
    AdminUserDisableView,
    AdminUserEnableView,
    AdminUserListView,
)

urlpatterns = [
    path("", AdminUserListView.as_view(), name="admin-users-list"),
    path("<str:user_id>/disable/", AdminUserDisableView.as_view(), name="admin-users-disable"),
    path("<str:user_id>/enable/", AdminUserEnableView.as_view(), name="admin-users-enable"),
]
