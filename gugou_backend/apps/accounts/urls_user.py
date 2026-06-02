from django.urls import path

from .views import (
    ChangePasswordView,
    ChangePhoneView,
    DeleteAccountView,
    LoginRecordsView,
    UserInfoView,
)

urlpatterns = [
    path("info/", UserInfoView.as_view(), name="user-info"),
    path("change-password/", ChangePasswordView.as_view(), name="user-change-password"),
    path("change-phone/", ChangePhoneView.as_view(), name="user-change-phone"),
    path("login-records/", LoginRecordsView.as_view(), name="user-login-records"),
    path("delete-account/", DeleteAccountView.as_view(), name="user-delete-account"),
]
