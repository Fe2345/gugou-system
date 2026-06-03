from rest_framework.permissions import BasePermission


class IsAuthenticated(BasePermission):
    """仅允许已登录且未被停用/注销的用户访问。"""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        status = getattr(request.user, "status", None)
        if status in ("disabled", "deleted"):
            return False
        return True


class IsAdmin(BasePermission):
    """仅允许管理员 (role='admin') 访问。非管理员返回 403。"""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "admin"
        )


class HasTradingPermission(BasePermission):
    """检查用户信用分是否满足交易条件。信用分 < 40 禁止交易。"""

    message = "信用分过低，禁止交易"

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.role == "admin":
            return True
        from apps.credits.services import check_trading_permission
        allowed, _ = check_trading_permission(request.user)
        return allowed
