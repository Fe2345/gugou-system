import logging
import os
import uuid

from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
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


class DeleteAccountView(APIView):
    """注销账户：将用户标记为 deleted 并吊销所有 token"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.status == "deleted":
            return error(message="账户已注销", code=400)

        user.status = "deleted"
        user.token_revoked_at = timezone.now()
        user.save(update_fields=["status", "token_revoked_at", "updated_at"])
        logger.info("用户注销: %s", user.user_id)
        return success(message="账户已注销")


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


class AvatarUploadView(APIView):
    """头像上传接口"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        image_file = request.FILES.get('avatar')
        if not image_file:
            return error(message="请选择要上传的头像", code=400)

        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if image_file.content_type not in allowed_types:
            return error(message="仅支持 JPG、PNG、GIF、WebP 格式的图片", code=400)

        if image_file.size > 2 * 1024 * 1024:
            return error(message="头像大小不能超过 2MB", code=400)

        ext = os.path.splitext(image_file.name)[1]
        filename = f"avatars/{uuid.uuid4().hex}{ext}"

        upload_dir = os.path.join(settings.MEDIA_ROOT, "avatars")
        os.makedirs(upload_dir, exist_ok=True)

        filepath = os.path.join(settings.MEDIA_ROOT, filename)
        with open(filepath, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)

        image_url = f"{settings.MEDIA_URL}{filename}"

        from apps.accounts.models import UserProfile
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.avatar = image_url
        profile.save(update_fields=["avatar", "updated_at"])

        return success(data={"avatar": image_url}, message="头像上传成功")
