from django.conf import settings
from django.db import models

from apps.common.models import BaseModel


class UserAsset(BaseModel):
    class Status(models.TextChoices):
        HOLDING = "holding", "持有中"
        SELLING = "selling", "出售中"
        EXCHANGING = "exchanging", "换物中"
        LOCKED = "locked", "交易锁定"
        SOLD = "sold", "已售出"
        EXCHANGED = "exchanged", "已换出"
        INVALID = "invalid", "已失效"

    asset_id = models.CharField("资产编号", max_length=25, primary_key=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assets",
        verbose_name="所属用户",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="assets",
        verbose_name="关联商品",
    )
    quantity = models.PositiveIntegerField("持有数量", default=1)
    acquire_price = models.DecimalField("入手价格", max_digits=10, decimal_places=2, default=0)
    acquired_at = models.DateTimeField("入手时间", null=True, blank=True)
    current_value = models.DecimalField("当前估值", max_digits=10, decimal_places=2, default=0)
    status = models.CharField("持有状态", max_length=20, choices=Status.choices, default=Status.HOLDING)
    source = models.CharField("来源", max_length=50, blank=True, default="")

    class Meta:
        db_table = "user_asset"
        verbose_name = "用户资产"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.asset_id}"


class AssetFlow(BaseModel):
    class FlowType(models.TextChoices):
        ACQUIRE = "acquire", "获取"
        TRANSFER = "transfer", "转让"
        SELL = "sell", "售出"
        EXCHANGE_OUT = "exchange_out", "换出"
        EXCHANGE_IN = "exchange_in", "换入"
        LOCK = "lock", "锁定"
        UNLOCK = "unlock", "解锁"
        INVALIDATE = "invalidate", "失效"

    flow_id = models.CharField("流水编号", max_length=30, primary_key=True)
    asset = models.ForeignKey(
        UserAsset,
        on_delete=models.CASCADE,
        related_name="flows",
        verbose_name="关联资产",
    )
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="asset_flows_out",
        verbose_name="来源用户",
        null=True,
        blank=True,
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="asset_flows_in",
        verbose_name="目标用户",
        null=True,
        blank=True,
    )
    flow_type = models.CharField("流转类型", max_length=20, choices=FlowType.choices)
    related_order = models.CharField("关联订单", max_length=25, blank=True, default="")
    related_exchange = models.CharField("关联换物", max_length=25, blank=True, default="")
    note = models.CharField("备注", max_length=200, blank=True, default="")

    class Meta:
        db_table = "asset_flow"
        verbose_name = "资产流转记录"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.flow_id} {self.flow_type}"
