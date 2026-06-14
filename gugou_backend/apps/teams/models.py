from django.conf import settings
from django.db import models

from apps.common.models import BaseModel


class TeamProject(BaseModel):
    class Status(models.TextChoices):
        RECRUITING = "recruiting", "招募中"
        SUCCESS = "success", "拼团成功"
        FAILED = "failed", "拼团失败"
        CANCELLED = "cancelled", "已取消"

    team_id = models.CharField("拼团编号", max_length=25, primary_key=True)
    product_name = models.CharField("拼团商品名称", max_length=100, default="")
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="team_projects",
        verbose_name="发起用户",
    )
    target_count = models.PositiveIntegerField("目标人数")
    current_count = models.PositiveIntegerField("当前人数", default=0)
    team_price = models.DecimalField("团购价格", max_digits=10, decimal_places=2)
    deadline = models.DateTimeField("截止时间")
    status = models.CharField("拼团状态", max_length=20, choices=Status.choices, default=Status.RECRUITING)

    class Meta:
        db_table = "team_project"
        verbose_name = "拼团项目"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.team_id}"


class TeamParticipant(BaseModel):
    class Status(models.TextChoices):
        JOINED = "joined", "已参与"
        CANCELLED = "cancelled", "已取消"
        REFUNDED = "refunded", "已退款"

    participant_id = models.CharField("参与记录编号", max_length=30, primary_key=True)
    team = models.ForeignKey(
        TeamProject,
        on_delete=models.CASCADE,
        related_name="participants",
        verbose_name="关联拼团",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="team_participations",
        verbose_name="参与用户",
    )
    status = models.CharField("参与状态", max_length=20, choices=Status.choices, default=Status.JOINED)
    joined_at = models.DateTimeField("参与时间", auto_now_add=True)
    selected_item = models.ForeignKey(
        "TeamItem",
        on_delete=models.SET_NULL,
        related_name="selected_by_participants",
        verbose_name="选中小商品",
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "team_participant"
        verbose_name = "拼团参与记录"
        verbose_name_plural = verbose_name
        constraints = [
            models.UniqueConstraint(fields=["team", "user"], name="unique_team_user"),
        ]

    def __str__(self):
        return f"{self.participant_id}"


class TeamItem(BaseModel):
    """拼团内的小商品选项，每个选项只能被一个参与者选择"""

    item_id = models.CharField("选项编号", max_length=30, primary_key=True)
    team = models.ForeignKey(
        TeamProject,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="关联拼团",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="team_items",
        verbose_name="关联商品",
        null=True,
        blank=True,
    )
    name = models.CharField("选项名称", max_length=100)
    selected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="selected_team_items",
        verbose_name="选中用户",
    )
    selected_at = models.DateTimeField("选中时间", null=True, blank=True)
    sort_order = models.IntegerField("排序", default=0)

    class Meta:
        db_table = "team_item"
        verbose_name = "拼团小商品选项"
        verbose_name_plural = verbose_name
        ordering = ["sort_order"]

    def __str__(self):
        return f"{self.item_id} {self.name}"
