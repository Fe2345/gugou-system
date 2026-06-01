import logging
from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone

from apps.common.id_generator import generate_credit_record_id
from .models import CreditRecord

logger = logging.getLogger("gugou")

# ==================== 信用分常量 ====================
INITIAL_SCORE = 100       # 初始信用分
MAX_SCORE = 100           # 满分上限
MIN_SCORE = 0             # 最低下限
RECOVERY_CAP = 80         # 月度恢复上限（恢复后不超过此分数）

# ==================== 信用等级阈值 ====================
LEVEL_EXCELLENT = 80      # 良好用户（无限制）
LEVEL_AVERAGE = 60        # 一般用户（部分限制）
LEVEL_POOR = 40           # 较差用户（严格限制）
# < 40: 极差用户（禁止所有交易）

# ==================== 加分规则 ====================
CREDIT_ORDER_BUYER_COMPLETE = 2       # 买家确认收货
CREDIT_ORDER_SELLER_COMPLETE = 2      # 卖家完成订单
CREDIT_EXCHANGE_COMPLETE = 2          # 换物完成（双方各）
CREDIT_TEAM_SUCCESS = 1               # 拼团成功参与
CREDIT_MONTHLY_RECOVERY = 2           # 月度恢复

# ==================== 扣分规则 ====================
CREDIT_ORDER_BUYER_CANCEL_PAID = -3        # 买家已付款后取消
CREDIT_ORDER_BUYER_TIMEOUT = -2            # 买家超时未付款
CREDIT_ORDER_SELLER_CANCEL_LOCKED = -3     # 卖家取消已锁定订单
CREDIT_EXCHANGE_CANCEL_AFTER_MATCH = -5    # 换物匹配后取消
CREDIT_TEAM_EXIT_AFTER_SUCCESS = -3        # 拼团成功后退出

# ==================== 每日限制 ====================
DAILY_ORDER_LIMIT_POOR = 1       # 较差用户每日下单上限
DAILY_ORDER_LIMIT_AVERAGE = 3    # 一般用户每日下单上限
MAX_LISTING_COUNT_AVERAGE = 5    # 一般用户最大发布商品数


def create_credit_record(user, change_value, reason, related_order=None):
    """创建信用变动记录并同步更新用户信用分。"""
    credit_record_id = generate_credit_record_id()

    credit_record = CreditRecord.objects.create(
        credit_record_id=credit_record_id,
        user=user,
        change_value=change_value,
        reason=reason,
        related_order=related_order,
    )

    new_score = user.credit_score + change_value
    new_score = max(MIN_SCORE, min(MAX_SCORE, new_score))
    user.credit_score = new_score
    user.save(update_fields=["credit_score"])

    # 信用分低于阈值时自动冻结账户
    if new_score < LEVEL_POOR and user.status == "normal":
        user.status = "frozen"
        user.save(update_fields=["status"])
        logger.warning("用户 %s 信用分过低(%d)，账户已自动冻结", user.user_id, new_score)

    logger.info(
        "用户 %s 信用变动: %s, 原因: %s, 当前信用分: %s",
        user.user_id,
        f"{change_value:+d}",
        reason,
        user.credit_score,
    )

    return credit_record


def get_credit_level(score):
    """返回信用等级标识。"""
    if score >= LEVEL_EXCELLENT:
        return "良好用户"
    elif score >= LEVEL_AVERAGE:
        return "一般用户"
    elif score >= LEVEL_POOR:
        return "较差用户"
    else:
        return "极差用户"


def get_trading_restrictions(score):
    """返回当前信用分对应的交易限制描述。"""
    if score >= LEVEL_EXCELLENT:
        return {"level": "良好用户", "can_trade": True, "restrictions": []}
    elif score >= LEVEL_AVERAGE:
        return {
            "level": "一般用户",
            "can_trade": True,
            "restrictions": [
                f"每日最多下单 {DAILY_ORDER_LIMIT_AVERAGE} 次",
                f"最多同时发布 {MAX_LISTING_COUNT_AVERAGE} 个商品",
            ],
        }
    elif score >= LEVEL_POOR:
        return {
            "level": "较差用户",
            "can_trade": True,
            "restrictions": [
                f"每日最多下单 {DAILY_ORDER_LIMIT_POOR} 次",
                "不能发布商品",
                "不能发起换物请求",
            ],
        }
    else:
        return {
            "level": "极差用户",
            "can_trade": False,
            "restrictions": ["信用分过低，禁止所有交易，请联系管理员"],
        }


def check_trading_permission(user):
    """检查用户是否有交易权限。返回 (allowed, message)。"""
    if user.role == "admin":
        return True, ""

    score = user.credit_score

    if score < LEVEL_POOR:
        return False, "信用分过低，禁止所有交易，请联系管理员"

    if user.status != "normal":
        return False, "账户状态异常，请联系管理员"

    return True, ""


def check_daily_order_limit(user):
    """检查用户今日下单次数是否超限。返回 (allowed, message)。"""
    if user.role == "admin":
        return True, ""

    score = user.credit_score

    if score < LEVEL_POOR:
        return False, "信用分过低，禁止下单"

    if score < LEVEL_AVERAGE:
        limit = DAILY_ORDER_LIMIT_POOR
    elif score < LEVEL_EXCELLENT:
        limit = DAILY_ORDER_LIMIT_AVERAGE
    else:
        return True, ""

    from apps.orders.models import Order
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_count = Order.objects.filter(
        buyer=user,
        created_at__gte=today_start,
    ).exclude(
        status=Order.Status.CANCELLED,
    ).count()

    if today_count >= limit:
        return False, f"信用等级限制：每日最多下单 {limit} 次"

    return True, ""


def check_listing_permission(user):
    """检查用户是否有发布商品权限。返回 (allowed, message)。"""
    if user.role == "admin":
        return True, ""

    score = user.credit_score

    if score < LEVEL_POOR:
        return False, "信用分过低，禁止发布商品"
    if score < LEVEL_AVERAGE:
        return False, "信用分不足，不能发布商品（需60分以上）"

    if score < LEVEL_EXCELLENT:
        from apps.market.models import Listing
        active_count = Listing.objects.filter(
            seller=user,
            status__in=[Listing.Status.ACTIVE, Listing.Status.LOCKED],
        ).count()
        if active_count >= MAX_LISTING_COUNT_AVERAGE:
            return False, f"信用等级限制：最多同时发布 {MAX_LISTING_COUNT_AVERAGE} 个商品"

    return True, ""


def check_exchange_permission(user):
    """检查用户是否有发起换物权限。返回 (allowed, message)。"""
    if user.role == "admin":
        return True, ""

    score = user.credit_score

    if score < LEVEL_POOR:
        return False, "信用分过低，禁止换物交易"
    if score < LEVEL_AVERAGE:
        return False, "信用分不足，不能发起换物（需60分以上）"

    return True, ""


def check_team_permission(user):
    """检查用户是否有参与拼团权限。返回 (allowed, message)。"""
    if user.role == "admin":
        return True, ""

    score = user.credit_score

    if score < LEVEL_POOR:
        return False, "信用分过低，禁止参与拼团"

    return True, ""


def monthly_credit_recovery():
    """月度信用恢复：信用分 < 80 的用户自动 +2 分（上限80分）。"""
    from apps.accounts.models import User

    users = User.objects.filter(
        credit_score__lt=RECOVERY_CAP,
        status="normal",
        role="user",
    )

    count = 0
    for user in users:
        old_score = user.credit_score
        if old_score >= RECOVERY_CAP:
            continue

        recovery = min(CREDIT_MONTHLY_RECOVERY, RECOVERY_CAP - old_score)
        if recovery <= 0:
            continue

        create_credit_record(
            user=user,
            change_value=recovery,
            reason="月度信用恢复",
        )

        # 如果恢复后信用分 >= 40 且账户是冻结状态，自动解冻
        if user.credit_score >= LEVEL_POOR and user.status == "frozen":
            user.status = "normal"
            user.save(update_fields=["status"])
            logger.info("用户 %s 信用分恢复至 %d，账户已自动解冻", user.user_id, user.credit_score)

        count += 1

    logger.info("月度信用恢复完成，影响 %d 名用户", count)
    return count
