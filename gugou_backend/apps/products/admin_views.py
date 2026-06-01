from datetime import datetime

from django.core.paginator import Paginator
from django.db.models import Q, Sum
from rest_framework.views import APIView

from apps.common.id_generator import next_seq
from apps.common.permissions import IsAdmin
from apps.common.response import error, paginated, success
from apps.operations.models import AdminOperationLog

from .models import Product
from .serializers import AdminGoodsSerializer, ProductUpdateSerializer


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

        # 全量统计（基于筛选后的完整数据，不受分页影响）
        from django.db.models import Count, Case, When, Value, CharField
        stats_queryset = queryset.values("status").annotate(count=Count("product_id"))
        stats_map = {item["status"]: item["count"] for item in stats_queryset}

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


class AdminGoodsApproveView(APIView):
    permission_classes = [IsAdmin]

    def put(self, request, product_id):
        try:
            product = Product.objects.get(product_id=product_id)
        except Product.DoesNotExist:
            return error(message="商品不存在", code=404)

        if product.status not in (Product.Status.INACTIVE, Product.Status.FROZEN):
            return error(message="当前状态不允许此操作", code=400)

        product.status = Product.Status.ACTIVE
        product.save(update_fields=["status", "updated_at"])

        _log_operation(request, "approve", product_id, f"商品 {product.name} 已启用")
        return success(message="操作成功")


class AdminGoodsRejectView(APIView):
    permission_classes = [IsAdmin]

    def put(self, request, product_id):
        try:
            product = Product.objects.get(product_id=product_id)
        except Product.DoesNotExist:
            return error(message="商品不存在", code=404)

        if product.status != Product.Status.INACTIVE:
            return error(message="当前状态不允许此操作", code=400)

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
            return error(message="当前状态不允许此操作", code=400)

        product.status = Product.Status.INACTIVE
        product.save(update_fields=["status", "updated_at"])

        _log_operation(request, "offline", product_id, f"商品 {product.name} 已下架")
        return success(message="操作成功")


class AdminGoodsEditView(APIView):
    permission_classes = [IsAdmin]

    def put(self, request, product_id):
        try:
            product = Product.objects.get(product_id=product_id)
        except Product.DoesNotExist:
            return error(message="商品不存在", code=404)

        serializer = ProductUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            from apps.common.response import flatten_errors
            return error(message=flatten_errors(serializer.errors))
        serializer.update(product, serializer.validated_data)

        _log_operation(request, "edit", product_id, f"管理员编辑了商品 {product.name}")
        return success(data=AdminGoodsSerializer(product).data, message="编辑成功")
