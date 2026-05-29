import logging

from apps.common.id_generator import generate_credit_record_id
from .models import CreditRecord

logger = logging.getLogger("gugou")


def create_credit_record(user, change_value, reason, related_order=None):
    """
    创建信用变动记录

    Args:
        user: 用户对象
        change_value: 信用变动值（正数为增加，负数为减少）
        reason: 变动原因
        related_order: 关联订单（可选）

    Returns:
        CreditRecord: 创建的信用记录
    """
    # 生成信用记录编号
    credit_record_id = generate_credit_record_id()

    # 创建信用记录
    credit_record = CreditRecord.objects.create(
        credit_record_id=credit_record_id,
        user=user,
        change_value=change_value,
        reason=reason,
        related_order=related_order,
    )

    # 同步更新用户信用分
    user.credit_score = max(0, user.credit_score + change_value)
    user.save(update_fields=["credit_score"])

    logger.info(
        "用户 %s 信用变动: %s, 原因: %s, 当前信用分: %s",
        user.user_id,
        f"{change_value:+d}",
        reason,
        user.credit_score,
    )

    return credit_record
