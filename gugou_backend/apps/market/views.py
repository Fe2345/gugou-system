import logging
import os
import uuid

from django.conf import settings
from django.db.models import Q
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


class ImageUploadView(APIView):
    """图片上传接口"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        image_file = request.FILES.get('image')
        if not image_file:
            return error(message="请选择要上传的图片", code=400)

        # 验证文件类型
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if image_file.content_type not in allowed_types:
            return error(message="仅支持 JPG、PNG、GIF、WebP 格式的图片", code=400)

        # 验证文件大小 (限制5MB)
        if image_file.size > 5 * 1024 * 1024:
            return error(message="图片大小不能超过 5MB", code=400)

        # 生成唯一文件名
        ext = os.path.splitext(image_file.name)[1]
        filename = f"market/{uuid.uuid4().hex}{ext}"

        # 确保目录存在
        upload_dir = os.path.join(settings.MEDIA_ROOT, "market")
        os.makedirs(upload_dir, exist_ok=True)

        # 保存文件
        filepath = os.path.join(settings.MEDIA_ROOT, filename)
        with open(filepath, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)

        # 返回可访问的URL
        image_url = f"{settings.MEDIA_URL}{filename}"

        return success(data={"image_url": image_url}, message="图片上传成功")


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
        keyword = request.query_params.get("keyword", "").strip()
        status_filter = request.query_params.get("status", Listing.Status.ACTIVE)
        product_id = request.query_params.get("product_id")
        min_price = request.query_params.get("min_price")
        max_price = request.query_params.get("max_price")
        ip_name = request.query_params.get("ip_name")
        character_name = request.query_params.get("character_name")
        category = request.query_params.get("category")
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))

        # 构建查询
        queryset = Listing.objects.filter(status=status_filter)

        # 关键词搜索：商品名称、IP、角色
        if keyword:
            queryset = queryset.filter(
                Q(product__name__icontains=keyword)
                | Q(product__ip_name__icontains=keyword)
                | Q(product__character_name__icontains=keyword)
            )

        if product_id:
            queryset = queryset.filter(product_id=product_id)

        if min_price:
            queryset = queryset.filter(price__gte=min_price)

        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        # 通过关联的 Product 表筛选
        if ip_name:
            queryset = queryset.filter(product__ip_name__icontains=ip_name)

        if character_name:
            queryset = queryset.filter(product__character_name__icontains=character_name)

        if category:
            queryset = queryset.filter(product__category=category)

        # 排序
        sort = request.query_params.get("sort", "-created_at")
        if sort == "price_asc":
            queryset = queryset.order_by("price")
        elif sort == "price_desc":
            queryset = queryset.order_by("-price")
        elif sort == "time":
            queryset = queryset.order_by("-created_at")
        else:
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
        status_filter = request.query_params.get("status")

        queryset = Listing.objects.filter(seller=request.user)

        # 按状态筛选
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        queryset = queryset.order_by("-created_at")

        # 统计各状态数量
        from django.db.models import Count, Q
        stats = Listing.objects.filter(seller=request.user).aggregate(
            total=Count('listing_id'),
            active=Count('listing_id', filter=Q(status=Listing.Status.ACTIVE)),
            sold=Count('listing_id', filter=Q(status=Listing.Status.SOLD)),
            cancelled=Count('listing_id', filter=Q(status=Listing.Status.CANCELLED)),
        )

        from django.core.paginator import Paginator
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        serializer = ListingListSerializer(page_obj, many=True)
        data = paginated(page_obj, serializer, page_size)
        data['stats'] = stats

        return success(data=data)
