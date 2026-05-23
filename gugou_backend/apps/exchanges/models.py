from django.conf import settings
from django.db import models

from apps.common.models import BaseModel


class ExchangeRequest(BaseModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "发布中"
        MATCHED = "matched", "已匹配"
        COMPLETED = "completed", "已完成"
        CANCELLED = "cancelled", "已取消"
        EXPIRED = "expired", "已过期"

    exchange_id = models.CharField("换物请求编号", max_length=25, primary_key=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="exchange_requests",
        verbose_name="发起用户",
    )
    offered_asset = models.ForeignKey(
        "assets.UserAsset",
        on_delete=models.PROTECT,
        related_name="exchange_requests",
        verbose_name="发起方资产",
    )
    target_condition = models.TextField("目标条件", blank=True, default="")
    price_difference_note = models.TextField("补差说明", blank=True, default="")
    status = models.CharField("请求状态", max_length=20, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        db_table = "exchange_request"
        verbose_name = "换物请求"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.exchange_id}"


class ExchangeMatch(BaseModel):
    class Status(models.TextChoices):
        PENDING = "pending", "待确认"
        ACCEPTED = "accepted", "已接受"
        REJECTED = "rejected", "已拒绝"
        EXPIRED = "expired", "已过期"

    match_id = models.CharField("匹配编号", max_length=30, primary_key=True)
    request = models.ForeignKey(
        ExchangeRequest,
        on_delete=models.CASCADE,
        related_name="matches",
        verbose_name="关联换物请求",
    )
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="exchange_matches",
        verbose_name="申请用户",
    )
    applicant_asset = models.ForeignKey(
        "assets.UserAsset",
        on_delete=models.PROTECT,
        related_name="exchange_matches",
        verbose_name="申请方资产",
    )
    status = models.CharField("匹配状态", max_length=20, choices=Status.choices, default=Status.PENDING)

    class Meta:
        db_table = "exchange_match"
        verbose_name = "换物匹配记录"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.match_id}"


class ExchangeStatusLog(BaseModel):
    log_id = models.CharField("日志编号", max_length=30, primary_key=True)
    exchange = models.ForeignKey(
        ExchangeRequest,
        on_delete=models.CASCADE,
        related_name="status_logs",
        verbose_name="关联换物请求",
    )
    from_status = models.CharField("变更前状态", max_length=20, blank=True, default="")
    to_status = models.CharField("变更后状态", max_length=20)
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="exchange_status_logs",
        verbose_name="操作人",
    )
    note = models.CharField("备注", max_length=200, blank=True, default="")

    class Meta:
        db_table = "exchange_status_log"
        verbose_name = "换物状态变更记录"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.log_id}"
