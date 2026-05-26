from django.conf import settings
from django.db import models

from apps.common.models import BaseModel


class Division(models.Model):
    """省/市/区 行政区划"""
    code = models.CharField(max_length=6, primary_key=True)
    name = models.CharField(max_length=50)
    level = models.SmallIntegerField()  # 1=省 2=市 3=区
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True,
        related_name="children",
    )

    class Meta:
        db_table = "division"
        verbose_name = "行政区划"
        verbose_name_plural = verbose_name
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} {self.name}"


class Address(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="addresses", verbose_name="用户",
    )
    receiver_name = models.CharField("收货人", max_length=30)
    receiver_phone = models.CharField("手机号", max_length=11)
    province = models.ForeignKey(
        Division, on_delete=models.PROTECT, related_name="+",
        verbose_name="省",
    )
    city = models.ForeignKey(
        Division, on_delete=models.PROTECT, related_name="+",
        verbose_name="市",
    )
    district = models.ForeignKey(
        Division, on_delete=models.PROTECT, related_name="+",
        verbose_name="区",
    )
    street = models.CharField("街道/镇", max_length=100)
    detail = models.CharField("详细地址", max_length=200)
    is_default = models.BooleanField("默认地址", default=False)

    class Meta:
        db_table = "user_address"
        verbose_name = "收货地址"
        verbose_name_plural = verbose_name
        ordering = ["-is_default", "-updated_at"]

    def __str__(self):
        return f"{self.receiver_name} {self.receiver_phone} {self.detail}"

    def set_default(self):
        """设为默认地址，取消其他默认。"""
        from django.db import transaction
        with transaction.atomic():
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
            self.is_default = True
            self.save(update_fields=["is_default"])

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
