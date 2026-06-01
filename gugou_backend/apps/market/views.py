import logging

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.common.permissions import IsAuthenticated
from apps.common.response import error, flatten_errors, success, paginated
from .models import Listing
from .serializers import (
    ListingCancelSerializer,
    ListingCreateSerializer,
    ListingDetailSerializer,
    ListingListSerializer,
)

logger = logging.getLogger("gugou")


class ListingCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 检查信用分发布权限
        from apps.credits.services import check_listing_permission
        allowed, msg = check_listing_permission(request.user)
        if not allowed:
            return error(message=msg, code=403)

        serializer = ListingCreateSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors), code=400)
        listing = serializer.save()
        data = ListingDetailSerializer(listing).data
        return success(data=data, message="挂单创建成功")


class ListingCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, listing_id):
        try:
            listing = Listing.objects.get(listing_id=listing_id)
        except Listing.DoesNotExist:
            return error(message="挂单不存在", code=404)

        # 验证是否是挂单拥有者
        if listing.seller != request.user:
            return error(message="无权操作此挂单", code=403)

        serializer = ListingCancelSerializer(listing, data={})
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors), code=400)
        serializer.save()
        return success(message="挂单已取消")


class ListingListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # 获取查询参数
        status_filter = request.query_params.get("status", Listing.Status.ACTIVE)
        product_id = request.query_params.get("product_id")
        min_price = request.query_params.get("min_price")
        max_price = request.query_params.get("max_price")
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))

        # 构建查询
        queryset = Listing.objects.filter(status=status_filter)

        if product_id:
            queryset = queryset.filter(product_id=product_id)

        if min_price:
            queryset = queryset.filter(price__gte=min_price)

        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        # 排序
        queryset = queryset.order_by("-created_at")

        # 分页
        from django.core.paginator import Paginator
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        # 序列化
        serializer = ListingListSerializer(page_obj, many=True)
        data = paginated(page_obj, serializer, page_size)

        return success(data=data)


class ListingDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, listing_id):
        try:
            listing = Listing.objects.get(listing_id=listing_id)
        except Listing.DoesNotExist:
            return error(message="挂单不存在", code=404)

        data = ListingDetailSerializer(listing).data
        return success(data=data)


class MyListingListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))

        queryset = Listing.objects.filter(seller=request.user).order_by("-created_at")

        from django.core.paginator import Paginator
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        serializer = ListingListSerializer(page_obj, many=True)
        data = paginated(page_obj, serializer, page_size)

        return success(data=data)
