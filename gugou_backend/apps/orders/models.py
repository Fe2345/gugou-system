from django.conf import settings
from django.db import models

from apps.common.models import BaseModel


class Order(BaseModel):
    class Status(models.TextChoices):
        CREATED = "created", "已创建"
        PENDING_PAYMENT = "pending_payment", "待支付"
        PAID = "paid", "已支付"
        COMPLETED = "completed", "已完成"
        CANCELLED = "cancelled", "已取消"
        CLOSED = "closed", "已关闭"
        REFUNDED = "refunded", "已退款"

    order_id = models.CharField("订单编号", max_length=25, primary_key=True)
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders_as_buyer",
        verbose_name="买家",
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders_as_seller",
        verbose_name="卖家",
    )
    listing = models.ForeignKey(
        "market.Listing",
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name="关联挂单",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name="商品",
    )
    quantity = models.PositiveIntegerField("数量", default=1)
    amount = models.DecimalField("订单金额", max_digits=10, decimal_places=2)
    status = models.CharField("订单状态", max_length=20, choices=Status.choices, default=Status.CREATED)
    paid_at = models.DateTimeField("支付时间", null=True, blank=True)
    completed_at = models.DateTimeField("完成时间", null=True, blank=True)

    class Meta:
        db_table = "order"
        verbose_name = "订单"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.order_id}"


class PaymentRecord(BaseModel):
    class PayMethod(models.TextChoices):
        BALANCE = "balance", "余额支付"
        ALIPAY = "alipay", "支付宝"
        WECHAT = "wechat", "微信支付"
        SIMULATED = "simulated", "模拟支付"

    class Status(models.TextChoices):
        PENDING = "pending", "待支付"
        SUCCESS = "success", "支付成功"
        FAILED = "failed", "支付失败"
        REFUNDED = "refunded", "已退款"

    payment_id = models.CharField("支付流水编号", max_length=50, primary_key=True)
    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="payments",
        verbose_name="关联订单",
    )
    payer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="payments",
        verbose_name="支付用户",
    )
    amount = models.DecimalField("支付金额", max_digits=10, decimal_places=2)
    pay_method = models.CharField("支付方式", max_length=20, choices=PayMethod.choices, default=PayMethod.SIMULATED)
    status = models.CharField("支付状态", max_length=20, choices=Status.choices, default=Status.PENDING)
    third_trade_no = models.CharField("第三方交易流水号", max_length=100, blank=True, default="")

    class Meta:
        db_table = "payment_record"
        verbose_name = "支付记录"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.payment_id}"


class OrderStatusLog(BaseModel):
    log_id = models.CharField("日志编号", max_length=30, primary_key=True)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="status_logs",
        verbose_name="关联订单",
    )
    from_status = models.CharField("变更前状态", max_length=20, blank=True, default="")
    to_status = models.CharField("变更后状态", max_length=20)
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_status_logs",
        verbose_name="操作人",
    )
    note = models.CharField("备注", max_length=200, blank=True, default="")

    class Meta:
        db_table = "order_status_log"
        verbose_name = "订单状态变更记录"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.log_id}"
