from django.conf import settings
from django.db import models

from apps.common.models import BaseModel


class Listing(BaseModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "上架中"
        LOCKED = "locked", "已被订单锁定"
        SOLD = "sold", "已售出"
        CANCELLED = "cancelled", "已取消"
        REMOVED = "removed", "管理员下架"

    listing_id = models.CharField("挂单编号", max_length=25, primary_key=True)
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="listings",
        verbose_name="卖家",
    )
    asset = models.ForeignKey(
        "assets.UserAsset",
        on_delete=models.PROTECT,
        related_name="listings",
        verbose_name="出售资产",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="listings",
        verbose_name="商品",
    )
    price = models.DecimalField("出售价格", max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField("出售数量", default=1)
    description = models.TextField("描述", blank=True, default="")
    status = models.CharField("挂单状态", max_length=20, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        db_table = "listing"
        verbose_name = "出售挂单"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.listing_id}"


class ListingImage(BaseModel):
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="挂单",
    )
    image_url = models.URLField("图片地址")
    sort_order = models.IntegerField("排序", default=0)

    class Meta:
        db_table = "listing_image"
        verbose_name = "挂单图片"
        verbose_name_plural = verbose_name
        ordering = ["sort_order"]
