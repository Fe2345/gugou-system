from datetime import timedelta

from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.utils import timezone
from rest_framework.views import APIView

from apps.common.permissions import IsAdmin
from apps.common.response import error, paginated, success

from .models import User
from .serializers import AdminUserSerializer


class AdminDashboardStatsView(APIView):
    """管理员仪表盘统计数据"""
    permission_classes = [IsAdmin]

    def get(self, request):
        from apps.orders.models import Order
        from apps.products.models import Product

        now = timezone.now()
        week_ago = now - timedelta(days=7)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        user_count = User.objects.exclude(status=User.Status.DELETED).count()
        product_count = Product.objects.exclude(status="archived").count()
        order_count = Order.objects.count()

        # 待审核事项：待审核的商品 + 待处理的订单
        pending_goods = Product.objects.filter(status="inactive").count()
        pending_orders = Order.objects.filter(
            status__in=["created", "pending_payment", "paid"]
        ).count()
        pending_count = pending_goods + pending_orders

        new_users_week = User.objects.filter(
            created_at__gte=week_ago
        ).exclude(status=User.Status.DELETED).count()

        orders_today = Order.objects.filter(
            created_at__gte=today_start
        ).count()

        return success(data={
            "user_count": user_count,
            "product_count": product_count,
            "order_count": order_count,
            "pending_count": pending_count,
            "new_users_week": new_users_week,
            "orders_today": orders_today,
        })


class AdminUserListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        keyword = request.query_params.get("keyword", "").strip()
        status_filter = request.query_params.get("status", "").strip()
        credit_level = request.query_params.get("creditLevel", "").strip()

        queryset = User.objects.all().order_by("-created_at")

        if keyword:
            queryset = queryset.filter(
                Q(user_id__icontains=keyword)
                | Q(nickname__icontains=keyword)
                | Q(phone__icontains=keyword)
            )

        if status_filter and status_filter != "all":
            # frontend sends Chinese labels, map to backend values
            status_map = {"正常": User.Status.NORMAL, "冻结": User.Status.FROZEN,
                          "停用": User.Status.DISABLED, "active": User.Status.NORMAL}
            status_filter = status_map.get(status_filter, status_filter)
            queryset = queryset.filter(status=status_filter)

        if credit_level:
            if credit_level == "高":
                queryset = queryset.filter(credit_score__gte=90)
            elif credit_level == "中":
                queryset = queryset.filter(credit_score__gte=70, credit_score__lt=90)
            elif credit_level == "低":
                queryset = queryset.filter(credit_score__lt=70)

        queryset = queryset.annotate(
            total_assets=Sum("assets__current_value", default=0)
        )

        try:
            page = int(request.query_params.get("page", 1))
            page_size = int(request.query_params.get("page_size", 20))
        except (ValueError, TypeError):
            page, page_size = 1, 20

        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        serializer = AdminUserSerializer(page_obj, many=True)
        return success(data=paginated(page_obj, serializer, page_size))


class AdminUserDisableView(APIView):
    """管理员停用用户（同时吊销所有 token）"""
    permission_classes = [IsAdmin]

    def put(self, request, user_id):
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return error(message="用户不存在", code=404)

        if user.status == User.Status.DISABLED:
            return error(message="用户已被停用", code=400)
        if user.status == User.Status.DELETED:
            return error(message="用户已注销，无法操作", code=400)

        user.status = User.Status.DISABLED
        user.token_revoked_at = timezone.now()
        user.save(update_fields=["status", "token_revoked_at", "updated_at"])
        return success(message="已停用，该用户所有 token 已失效")


class AdminUserEnableView(APIView):
    """管理员启用用户（恢复为正常状态）"""
    permission_classes = [IsAdmin]

    def put(self, request, user_id):
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return error(message="用户不存在", code=404)

        if user.status == User.Status.NORMAL:
            return error(message="该用户已是正常状态", code=400)
        if user.status == User.Status.DELETED:
            return error(message="用户已注销，无法操作", code=400)

        user.status = User.Status.NORMAL
        user.token_revoked_at = None
        user.save(update_fields=["status", "token_revoked_at", "updated_at"])
        return success(message="已恢复为正常状态")
