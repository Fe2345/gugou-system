from rest_framework.permissions import BasePermission


class IsAuthenticated(BasePermission):
    """仅允许已登录用户访问。未登录返回 401。"""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsAdmin(BasePermission):
    """仅允许管理员 (role='admin') 访问。非管理员返回 403。"""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "admin"
        )
