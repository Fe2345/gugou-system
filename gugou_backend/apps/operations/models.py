from django.conf import settings
from django.db import models

from apps.common.models import BaseModel


class SystemLog(BaseModel):
    log_id = models.CharField("日志编号", max_length=30, primary_key=True)
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="system_logs",
        verbose_name="操作用户",
    )
    module = models.CharField("操作模块", max_length=50)
    action = models.CharField("操作类型", max_length=50)
    target_id = models.CharField("操作对象编号", max_length=50, blank=True, default="")
    ip_address = models.GenericIPAddressField("操作 IP", blank=True, null=True)
    detail = models.TextField("操作详情", blank=True, default="")

    class Meta:
        db_table = "system_log"
        verbose_name = "系统日志"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.log_id}"


class AdminOperationLog(BaseModel):
    op_log_id = models.CharField("日志编号", max_length=30, primary_key=True)
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="admin_operation_logs",
        verbose_name="管理员",
    )
    module = models.CharField("操作模块", max_length=50)
    action = models.CharField("操作类型", max_length=50)
    target_id = models.CharField("操作对象编号", max_length=50, blank=True, default="")
    ip_address = models.GenericIPAddressField("操作 IP", blank=True, null=True)
    detail = models.TextField("操作详情", blank=True, default="")

    class Meta:
        db_table = "admin_operation_log"
        verbose_name = "管理员操作日志"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.op_log_id}"
