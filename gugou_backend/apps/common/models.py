from django.db import models


class BaseModel(models.Model):
    """Abstract base model with created_at / updated_at timestamps."""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        abstract = True
