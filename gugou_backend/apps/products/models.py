from django.conf import settings
from django.db import models

from apps.common.models import BaseModel


class Product(BaseModel):
    class Category(models.TextChoices):
        FIGURE = "figure", "手办"
        BADGE = "badge", "徽章"
        POSTER = "poster", "海报"
        ACRYLIC = "acrylic", "亚克力"
        DOLL = "doll", "玩偶"
        CARD = "card", "卡片"
        OTHER = "other", "其他"

    class Status(models.TextChoices):
        ACTIVE = "active", "正常启用"
        INACTIVE = "inactive", "未启用"
        FROZEN = "frozen", "冻结"
        ARCHIVED = "archived", "已归档"

    product_id = models.CharField("商品编号", max_length=13, primary_key=True)
    name = models.CharField("商品名称", max_length=100)
    ip_name = models.CharField("IP 名称", max_length=50)
    character_name = models.CharField("角色名称", max_length=50, blank=True, default="")
    category = models.CharField("品类", max_length=20, choices=Category.choices)
    reference_price = models.DecimalField("参考价格", max_digits=10, decimal_places=2, default=0)
    main_image = models.ImageField("主图", upload_to="products/%Y/%m/", blank=True, default="")
    description = models.TextField("商品描述", blank=True, default="")
    status = models.CharField("商品状态", max_length=10, choices=Status.choices, default=Status.ACTIVE)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_products",
        verbose_name="创建人",
    )

    class Meta:
        db_table = "product"
        verbose_name = "商品"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.product_id} {self.name}"


class ProductImage(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images", verbose_name="商品")
    image_url = models.URLField("图片地址")
    sort_order = models.IntegerField("排序", default=0)

    class Meta:
        db_table = "product_image"
        verbose_name = "商品图片"
        verbose_name_plural = verbose_name
        ordering = ["sort_order"]
