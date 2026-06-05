from django.conf import settings
from django.db import models

from apps.common.models import BaseModel


class Order(BaseModel):
    class Status(models.TextChoices):
        CREATED = "created", "Created"
        PENDING_PAYMENT = "pending_payment", "Pending payment"
        PAID = "paid", "Paid"
        RECEIVING = "receiving", "Receiving"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        CLOSED = "closed", "Closed"
        PENDING_RETURN = "pending_return", "Pending return"
        REFUNDED = "refunded", "Refunded"

    order_id = models.CharField("order id", max_length=25, primary_key=True)
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders_as_buyer",
        verbose_name="buyer",
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders_as_seller",
        verbose_name="seller",
    )
    listing = models.ForeignKey(
        "market.Listing",
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name="listing",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name="product",
    )
    quantity = models.PositiveIntegerField("quantity", default=1)
    amount = models.DecimalField("amount", max_digits=10, decimal_places=2)
    status = models.CharField("status", max_length=20, choices=Status.choices, default=Status.CREATED)
    paid_at = models.DateTimeField("paid at", null=True, blank=True)
    completed_at = models.DateTimeField("completed at", null=True, blank=True)
    shipping_address = models.ForeignKey(
        "addresses.Address",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="shipping address",
    )
    receiver_name = models.CharField("receiver name", max_length=30, blank=True, default="")
    receiver_phone = models.CharField("receiver phone", max_length=11, blank=True, default="")
    shipping_address_text = models.CharField("shipping address snapshot", max_length=300, blank=True, default="")

    class Meta:
        db_table = "order"
        verbose_name = "order"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.order_id}"


class PaymentRecord(BaseModel):
    class PayMethod(models.TextChoices):
        BALANCE = "balance", "Balance"
        ALIPAY = "alipay", "Alipay"
        WECHAT = "wechat", "Wechat"
        SIMULATED = "simulated", "Simulated"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    payment_id = models.CharField("payment id", max_length=50, primary_key=True)
    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="payments",
        verbose_name="order",
    )
    payer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="payments",
        verbose_name="payer",
    )
    amount = models.DecimalField("amount", max_digits=10, decimal_places=2)
    pay_method = models.CharField("pay method", max_length=20, choices=PayMethod.choices, default=PayMethod.SIMULATED)
    status = models.CharField("status", max_length=20, choices=Status.choices, default=Status.PENDING)
    third_trade_no = models.CharField("third trade no", max_length=100, blank=True, default="")

    class Meta:
        db_table = "payment_record"
        verbose_name = "payment record"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.payment_id}"


class OrderStatusLog(BaseModel):
    log_id = models.CharField("log id", max_length=30, primary_key=True)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="status_logs",
        verbose_name="order",
    )
    from_status = models.CharField("from status", max_length=20, blank=True, default="")
    to_status = models.CharField("to status", max_length=20)
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_status_logs",
        verbose_name="operator",
    )
    note = models.CharField("note", max_length=200, blank=True, default="")

    class Meta:
        db_table = "order_status_log"
        verbose_name = "order status log"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.log_id}"
