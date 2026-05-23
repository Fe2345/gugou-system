from django.db import models

from apps.common.models import BaseModel


class PriceRecord(BaseModel):
    class Source(models.TextChoices):
        ORDER = "order", "平台成交订单"
        MANUAL = "manual", "管理员录入"
        SYSTEM = "system", "系统统计生成"

    price_record_id = models.CharField("价格记录编号", max_length=30, primary_key=True)
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="price_records",
        verbose_name="商品",
    )
    price = models.DecimalField("成交价格或统计价格", max_digits=10, decimal_places=2)
    source = models.CharField("来源", max_length=10, choices=Source.choices, default=Source.ORDER)
    recorded_at = models.DateTimeField("统计时间")

    class Meta:
        db_table = "price_record"
        verbose_name = "商品价格记录"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.price_record_id} {self.price}"
