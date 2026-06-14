import logging

from django.utils import timezone

from apps.common.id_generator import generate_credit_record_id
from .models import CreditRecord

logger = logging.getLogger("gugou")

# Credit score constants
INITIAL_SCORE = 100
MAX_SCORE = 100
MIN_SCORE = 0
RECOVERY_CAP = 80

# Credit levels
LEVEL_EXCELLENT = 80
LEVEL_AVERAGE = 60
LEVEL_POOR = 40

# Positive rules
CREDIT_ORDER_BUYER_COMPLETE = 2
CREDIT_ORDER_SELLER_COMPLETE = 2
CREDIT_EXCHANGE_COMPLETE = 2
CREDIT_TEAM_SUCCESS = 1
CREDIT_MONTHLY_RECOVERY = 2

# Negative rules
CREDIT_ORDER_BUYER_CANCEL_PAID = -3
CREDIT_ORDER_BUYER_RETURN = -2
CREDIT_ORDER_BUYER_TIMEOUT = -2
CREDIT_ORDER_SELLER_CANCEL_LOCKED = -3
CREDIT_EXCHANGE_CANCEL_AFTER_MATCH = -5
CREDIT_TEAM_EXIT_AFTER_SUCCESS = -3

# Daily limits
DAILY_ORDER_LIMIT_POOR = 1
DAILY_ORDER_LIMIT_AVERAGE = 3
MAX_LISTING_COUNT_AVERAGE = 5


def create_credit_record(user, change_value, reason, related_order=None):
    """Create a credit record and update the user's credit score."""
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

    if new_score < LEVEL_POOR and user.status == "normal":
        user.status = "frozen"
        user.save(update_fields=["status"])
        logger.warning("User %s credit score is too low (%d), account frozen", user.user_id, new_score)

    logger.info(
        "User %s credit changed: %s, reason: %s, current score: %s",
        user.user_id,
        f"{change_value:+d}",
        reason,
        user.credit_score,
    )

    return credit_record


def get_credit_level(score):
    """Return the credit level name."""
    if score >= LEVEL_EXCELLENT:
        return "excellent"
    if score >= LEVEL_AVERAGE:
        return "average"
    if score >= LEVEL_POOR:
        return "poor"
    return "blocked"


def get_trading_restrictions(score):
    """Return trading restrictions for the current credit score."""
    if score >= LEVEL_EXCELLENT:
        return {"level": "excellent", "can_trade": True, "restrictions": []}
    if score >= LEVEL_AVERAGE:
        return {
            "level": "average",
            "can_trade": True,
            "restrictions": [
                f"Daily order limit: {DAILY_ORDER_LIMIT_AVERAGE}",
                f"Active listing limit: {MAX_LISTING_COUNT_AVERAGE}",
            ],
        }
    if score >= LEVEL_POOR:
        return {
            "level": "poor",
            "can_trade": True,
            "restrictions": [
                f"Daily order limit: {DAILY_ORDER_LIMIT_POOR}",
                "Cannot publish products",
                "Cannot start exchange requests",
            ],
        }
    return {
        "level": "blocked",
        "can_trade": False,
        "restrictions": ["Credit score is too low. Trading is disabled."],
    }


def check_trading_permission(user):
    """Check whether the user can trade. Returns (allowed, message)."""
    if user.role == "admin":
        return True, ""

    score = user.credit_score

    if score < LEVEL_POOR:
        return False, "Credit score is too low. Trading is disabled."

    if user.status != "normal":
        return False, "Account status is abnormal. Please contact an administrator."

    return True, ""


def check_daily_order_limit(user):
    """Check whether today's order count exceeds the credit-based limit."""
    if user.role == "admin":
        return True, ""

    score = user.credit_score

    if score < LEVEL_POOR:
        return False, "Credit score is too low. Orders are disabled."

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
        return False, f"Credit level limit: maximum {limit} orders per day."

    return True, ""


def check_listing_permission(user):
    """Check whether the user can publish listings. Returns (allowed, message)."""
    if user.role == "admin":
        return True, ""

    score = user.credit_score

    if score < LEVEL_POOR:
        return False, "Credit score is too low. Publishing products is disabled."
    if score < LEVEL_AVERAGE:
        return False, "Credit score is not enough to publish products. At least 60 is required."

    if score < LEVEL_EXCELLENT:
        from apps.market.models import Listing

        active_count = Listing.objects.filter(
            seller=user,
            status__in=[Listing.Status.ACTIVE, Listing.Status.LOCKED],
        ).count()
        if active_count >= MAX_LISTING_COUNT_AVERAGE:
            return False, f"Credit level limit: maximum {MAX_LISTING_COUNT_AVERAGE} active listings."

    return True, ""


def check_exchange_permission(user):
    """Check whether the user can start exchange requests. Returns (allowed, message)."""
    if user.role == "admin":
        return True, ""

    score = user.credit_score

    if score < LEVEL_POOR:
        return False, "Credit score is too low. Exchange is disabled."
    if score < LEVEL_AVERAGE:
        return False, "Credit score is not enough to start exchanges. At least 60 is required."

    return True, ""


def check_team_permission(user):
    """Check whether the user can join team purchases. Returns (allowed, message)."""
    if user.role == "admin":
        return True, ""

    score = user.credit_score

    if score < LEVEL_POOR:
        return False, "Credit score is too low. Team purchases are disabled."

    return True, ""


def monthly_credit_recovery():
    """Monthly recovery: users below 80 recover +2 points, capped at 80."""
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
            reason="Monthly credit recovery",
        )

        if user.credit_score >= LEVEL_POOR and user.status == "frozen":
            user.status = "normal"
            user.save(update_fields=["status"])
            logger.info("User %s recovered to %d, account unfrozen", user.user_id, user.credit_score)

        count += 1

    logger.info("Monthly credit recovery completed, affected users: %d", count)
    return count
