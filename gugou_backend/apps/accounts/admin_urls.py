from django.urls import path

from .admin_views import AdminUserFreezeView, AdminUserListView, AdminUserUnfreezeView

urlpatterns = [
    path("", AdminUserListView.as_view(), name="admin-users-list"),
    path("<str:user_id>/freeze/", AdminUserFreezeView.as_view(), name="admin-users-freeze"),
    path("<str:user_id>/unfreeze/", AdminUserUnfreezeView.as_view(), name="admin-users-unfreeze"),
]
