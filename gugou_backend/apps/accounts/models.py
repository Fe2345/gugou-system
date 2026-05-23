from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

from apps.common.models import BaseModel


class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError("手机号不能为空")
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("role", User.Role.ADMIN)
        extra_fields.setdefault("status", User.Status.NORMAL)
        return self.create_user(phone, password, **extra_fields)


class User(AbstractBaseUser, BaseModel):
    class Role(models.TextChoices):
        USER = "user", "普通用户"
        ADMIN = "admin", "管理员"

    class Status(models.TextChoices):
        NORMAL = "normal", "正常"
        FROZEN = "frozen", "冻结"
        DISABLED = "disabled", "停用"
        DELETED = "deleted", "已注销"

    user_id = models.CharField("用户编号", max_length=13, primary_key=True)
    phone = models.CharField("手机号", max_length=11, unique=True)
    nickname = models.CharField("昵称", max_length=50, blank=True, default="")
    role = models.CharField("角色", max_length=10, choices=Role.choices, default=Role.USER)
    is_active = models.BooleanField("是否活跃", default=True)
    credit_score = models.IntegerField("信用分", default=100)
    status = models.CharField("账户状态", max_length=10, choices=Status.choices, default=Status.NORMAL)

    objects = UserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "user"
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user_id} ({self.nickname or self.phone})"

    @property
    def is_staff(self):
        return self.role == self.Role.ADMIN

    @property
    def is_superuser(self):
        return self.role == self.Role.ADMIN

    def has_perm(self, perm, obj=None):
        return self.role == self.Role.ADMIN

    def has_module_perms(self, app_label):
        return self.role == self.Role.ADMIN


class UserProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", verbose_name="用户")
    avatar = models.URLField("头像", blank=True, default="")
    bio = models.CharField("简介", max_length=200, blank=True, default="")
    contact = models.CharField("联系方式", max_length=100, blank=True, default="")

    class Meta:
        db_table = "user_profile"
        verbose_name = "用户资料"
        verbose_name_plural = verbose_name
