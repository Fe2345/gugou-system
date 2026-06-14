from datetime import datetime

from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
from rest_framework.views import APIView

from apps.common.id_generator import next_seq
from apps.common.permissions import IsAdmin
from apps.common.response import error, paginated, success
from apps.operations.models import AdminOperationLog

from .models import Product
from .serializers import AdminGoodsSerializer


def _log_operation(request, action, target_id, detail=""):
    log_id = f"AL{datetime.now().strftime('%Y%m%d%H%M%S')}{str(next_seq('admin_log')).zfill(4)}"
    AdminOperationLog.objects.create(
        op_log_id=log_id,
        admin=request.user,
        module="product",
        action=action,
        target_id=target_id,
        ip_address=request.META.get("REMOTE_ADDR"),
        detail=detail,
    )


class AdminGoodsListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        keyword = request.query_params.get("keyword", "").strip()
        status_filter = request.query_params.get("status", "").strip()
        category = request.query_params.get("category", "").strip()

        # 统计基于关键词和分类筛选（不含状态筛选）
        stats_base = Product.objects.all()
        if keyword:
            stats_base = stats_base.filter(
                Q(name__icontains=keyword)
                | Q(product_id__icontains=keyword)
                | Q(created_by__user_id__icontains=keyword)
            )
        if category:
            stats_base = stats_base.filter(category=category)

        stats_queryset = stats_base.values("status").annotate(count=Count("product_id"))
        stats_map = {item["status"]: item["count"] for item in stats_queryset}

        # 列表查询（含状态筛选）
        queryset = Product.objects.all().order_by("-created_at")

        if keyword:
            queryset = queryset.filter(
                Q(name__icontains=keyword)
                | Q(product_id__icontains=keyword)
                | Q(created_by__user_id__icontains=keyword)
            )

        if status_filter and status_filter != "all":
            queryset = queryset.filter(status=status_filter)

        if category:
            queryset = queryset.filter(category=category)

        queryset = queryset.annotate(
            stock=Sum("listings__quantity", filter=Q(listings__status="active"), default=0)
        )

        try:
            page = int(request.query_params.get("page", 1))
            page_size = int(request.query_params.get("page_size", 20))
        except (ValueError, TypeError):
            page, page_size = 1, 20

        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        serializer = AdminGoodsSerializer(page_obj, many=True)
        data = paginated(page_obj, serializer, page_size)
        data["stats"] = {
            "active": stats_map.get("active", 0),
            "inactive": stats_map.get("inactive", 0),
            "frozen": stats_map.get("frozen", 0),
            "total": sum(stats_map.values()),
        }

        return success(data=data)

    def post(self, request):
        return error(message="管理员不能添加商品，请由用户提交后审核", code=403)


class AdminGoodsApproveView(APIView):
    permission_classes = [IsAdmin]

    def put(self, request, product_id):
        try:
            product = Product.objects.get(product_id=product_id)
        except Product.DoesNotExist:
            return error(message="商品不存在", code=404)

        if product.status != Product.Status.INACTIVE:
            return error(message="只有待审核商品可以通过审核", code=400)

        product.status = Product.Status.ACTIVE
        product.save(update_fields=["status", "updated_at"])

        _log_operation(request, "approve", product_id, f"商品 {product.name} 审核通过并上架")
        return success(message="操作成功")


class AdminGoodsRejectView(APIView):
    permission_classes = [IsAdmin]

    def put(self, request, product_id):
        try:
            product = Product.objects.get(product_id=product_id)
        except Product.DoesNotExist:
            return error(message="商品不存在", code=404)

        if product.status != Product.Status.INACTIVE:
            return error(message="只有待审核商品可以驳回", code=400)

        product.status = Product.Status.FROZEN
        product.save(update_fields=["status", "updated_at"])

        _log_operation(request, "reject", product_id, f"商品 {product.name} 已驳回")
        return success(message="操作成功")


class AdminGoodsOfflineView(APIView):
    permission_classes = [IsAdmin]

    def put(self, request, product_id):
        try:
            product = Product.objects.get(product_id=product_id)
        except Product.DoesNotExist:
            return error(message="商品不存在", code=404)

        if product.status != Product.Status.ACTIVE:
            return error(message="只有已上架商品可以下架", code=400)

        product.status = Product.Status.INACTIVE
        product.save(update_fields=["status", "updated_at"])

        _log_operation(request, "offline", product_id, f"商品 {product.name} 已下架并回到待审核")
        return success(message="操作成功")


class AdminGoodsEditView(APIView):
    permission_classes = [IsAdmin]

    def put(self, request, product_id):
        return error(message="管理员不能修改商品信息", code=403)
