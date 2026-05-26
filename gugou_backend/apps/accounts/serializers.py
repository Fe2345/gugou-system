import logging

from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from apps.common.id_generator import generate_user_id
from .models import User, UserProfile

logger = logging.getLogger("gugou")


class RegisterSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=11)
    password = serializers.CharField(min_length=6, write_only=True)

    def validate_phone(self, value):
        import re
        if not re.match(r"^1[3-9]\d{9}$", value):
            raise serializers.ValidationError("请输入有效的 11 位手机号")
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("该手机号已注册")
        return value

    def create(self, validated_data):
        user = User(
            user_id=generate_user_id(),
            phone=validated_data["phone"],
        )
        user.set_password(validated_data["password"])
        user.save()
        UserProfile.objects.create(user=user)
        logger.info("新用户注册: %s", user.user_id)
        return user


class LoginSerializer(serializers.Serializer):
    account = serializers.CharField(max_length=11)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        account = attrs["account"]
        password = attrs["password"]

        user = authenticate(request=self.context.get("request"), username=account, password=password)
        if user is None:
            logger.warning("登录失败: account=%s", account)
            raise serializers.ValidationError("账号或密码错误")

        if user.status in (User.Status.FROZEN, User.Status.DISABLED, User.Status.DELETED):
            logger.warning("登录被拒: %s status=%s", user.user_id, user.status)
            raise serializers.ValidationError("账户已被冻结或停用，请联系管理员")

        token, _ = Token.objects.get_or_create(user=user)
        logger.info("用户登录: %s", user.user_id)
        attrs["token"] = token.key
        attrs["user"] = user
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=11)
    password = serializers.CharField(min_length=6, write_only=True)

    def validate_phone(self, value):
        import re
        if not re.match(r"^1[3-9]\d{9}$", value):
            raise serializers.ValidationError("请输入有效的 11 位手机号")
        return value

    def save(self):
        try:
            user = User.objects.get(phone=self.validated_data["phone"])
        except User.DoesNotExist:
            raise serializers.ValidationError({"phone": "未找到该手机号"})
        user.set_password(self.validated_data["password"])
        user.save()
        logger.info("密码重置: %s", user.user_id)


class UserSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="user_id", read_only=True)
    role = serializers.CharField(read_only=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    creditScore = serializers.IntegerField(source="credit_score", read_only=True)
    status = serializers.CharField(read_only=True)
    avatar = serializers.SerializerMethodField()
    bio = serializers.SerializerMethodField()
    contact = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "phone", "nickname", "avatar", "role", "createdAt", "creditScore", "status", "bio", "contact"]

    def get_avatar(self, obj):
        profile = getattr(obj, "profile", None)
        return profile.avatar if profile else ""

    def get_bio(self, obj):
        profile = getattr(obj, "profile", None)
        return profile.bio if profile else ""

    def get_contact(self, obj):
        profile = getattr(obj, "profile", None)
        return profile.contact if profile else ""


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(min_length=6, write_only=True)

    def validate_old_password(self, value):
        user = self.context["user"]
        if not user.check_password(value):
            raise serializers.ValidationError("当前密码不正确")
        return value

    def save(self):
        user = self.context["user"]
        user.set_password(self.validated_data["new_password"])
        user.save()


class ChangePhoneSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=11)

    def validate_phone(self, value):
        import re
        if not re.match(r"^1[3-9]\d{9}$", value):
            raise serializers.ValidationError("请输入有效的 11 位手机号")
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("该手机号已被其他账号使用")
        return value

    def save(self):
        user = self.context["user"]
        user.phone = self.validated_data["phone"]
        user.save(update_fields=["phone"])


class LoginRecordSerializer(serializers.Serializer):
    ip = serializers.CharField(source="ip_address", read_only=True)
    ua = serializers.CharField(source="user_agent", read_only=True)
    time = serializers.DateTimeField(source="created_at", read_only=True)


class UserUpdateSerializer(serializers.Serializer):
    nickname = serializers.CharField(max_length=50, required=False, allow_blank=True)
    avatar = serializers.URLField(required=False, allow_blank=True)
    bio = serializers.CharField(max_length=200, required=False, allow_blank=True, allow_null=True)
    contact = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True)

    def update(self, user, validated_data):
        if "nickname" in validated_data:
            user.nickname = validated_data["nickname"]
        user.save()

        profile, _ = UserProfile.objects.get_or_create(user=user)
        if "avatar" in validated_data:
            profile.avatar = validated_data["avatar"]
        if "bio" in validated_data:
            profile.bio = validated_data["bio"]
        if "contact" in validated_data:
            profile.contact = validated_data["contact"]
        profile.save()
        return user
