from django.conf import settings
from django.db import models

from apps.common.models import BaseModel


class CreditRecord(BaseModel):
    credit_record_id = models.CharField("信用记录编号", max_length=30, primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="credit_records",
        verbose_name="关联用户",
    )
    change_value = models.IntegerField("信用变动值")
    reason = models.CharField("变动原因", max_length=200)
    related_order = models.ForeignKey(
        "orders.Order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="credit_records",
        verbose_name="关联订单",
    )

    class Meta:
        db_table = "credit_record"
        verbose_name = "信用变动记录"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.credit_record_id} {self.change_value:+d}"
