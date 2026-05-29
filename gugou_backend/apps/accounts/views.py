import logging

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from apps.common.permissions import IsAuthenticated
from apps.common.response import error, flatten_errors, success
from .models import LoginRecord
from .serializers import (
    ChangePasswordSerializer,
    ChangePhoneSerializer,
    LoginRecordSerializer,
    LoginSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    UserSerializer,
    UserUpdateSerializer,
)

logger = logging.getLogger("gugou")


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors), code=400)
        user = serializer.save()
        return success(message="注册成功")


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors), code=400)
        data = serializer.validated_data
        user = data["user"]
        LoginRecord.objects.create(
            user=user,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )
        user_data = UserSerializer(user).data
        return success(data={
            "access": data["access"],
            "refresh": data["refresh"],
            "user": user_data,
        })


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # JWT is stateless — logout is client-side. The server just acknowledges.
        logger.info("用户登出: %s", request.user.user_id)
        return success(message="已退出登录")


class TokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return error(message="请提供刷新令牌", code=400)

        try:
            refresh = RefreshToken(refresh_token)
            data = {"access": str(refresh.access_token)}
            if settings.SIMPLE_JWT.get("ROTATE_REFRESH_TOKENS", False):
                data["refresh"] = str(refresh)
            return success(data=data)
        except TokenError:
            return error(message="刷新令牌无效或已过期", code=401)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors), code=400)
        serializer.save()
        return success(message="密码修改成功，请使用新密码登录")


class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = UserSerializer(request.user).data
        return success(data=data)

    def put(self, request):
        serializer = UserUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors), code=400)
        serializer.update(request.user, serializer.validated_data)
        data = UserSerializer(request.user).data
        return success(data=data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"user": request.user}
        )
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors), code=400)
        serializer.save()
        logger.info("密码修改: %s", request.user.user_id)
        return success(message="密码修改成功，请使用新密码重新登录")


class ChangePhoneView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = ChangePhoneSerializer(
            data=request.data, context={"user": request.user}
        )
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors), code=400)
        serializer.save()
        logger.info("手机号变更: %s", request.user.user_id)
        data = UserSerializer(request.user).data
        return success(data=data, message="手机号修改成功")


class LoginRecordsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        records = (
            LoginRecord.objects
            .filter(user=request.user)
            .order_by("-created_at")[:20]
        )
        data = LoginRecordSerializer(records, many=True).data
        return success(data=data)
