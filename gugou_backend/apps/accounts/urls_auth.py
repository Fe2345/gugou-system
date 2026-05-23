from django.urls import path

from .views import LoginView, LogoutView, RegisterView, ResetPasswordView

urlpatterns = [
    path("login/", LoginView.as_view(), name="auth-login"),
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("reset-password/", ResetPasswordView.as_view(), name="auth-reset-password"),
]
