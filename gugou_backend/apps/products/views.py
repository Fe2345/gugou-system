from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from apps.common.response import success, error, flatten_errors
from .models import Product
from .serializers import ProductSerializer, ProductCreateSerializer, ProductUpdateSerializer


class ProductListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """获取商品列表，支持 keyword/category 筛选和分页"""
        queryset = Product.objects.all().order_by("-created_at")

        keyword = request.query_params.get("keyword", "").strip()
        if keyword:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(name__icontains=keyword) |
                Q(ip_name__icontains=keyword) |
                Q(character_name__icontains=keyword)
            )

        category = request.query_params.get("category", "").strip()
        if category:
            queryset = queryset.filter(category=category)

        # 分页
        try:
            page = int(request.query_params.get("page", 1))
            page_size = int(request.query_params.get("pageSize", 10))
        except (ValueError, TypeError):
            page, page_size = 1, 10

        total = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        items = queryset[start:end]

        serializer = ProductSerializer(items, many=True)
        return success(data={
            "list": serializer.data,
            "total": total,
            "page": page,
            "pageSize": page_size,
        })

    def post(self, request):
        """创建商品"""
        serializer = ProductCreateSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors))
        product = serializer.save()
        return success(data=ProductSerializer(product).data, message="创建成功")


class ProductDetailView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, product_id):
        try:
            return Product.objects.get(product_id=product_id)
        except Product.DoesNotExist:
            return None

    def get(self, request, product_id):
        """获取商品详情"""
        product = self.get_object(product_id)
        if not product:
            return error(message="商品不存在", code=404)
        return success(data=ProductSerializer(product).data)

    def put(self, request, product_id):
        """更新商品"""
        product = self.get_object(product_id)
        if not product:
            return error(message="商品不存在", code=404)

        serializer = ProductUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors))
        serializer.update(product, serializer.validated_data)
        return success(data=ProductSerializer(product).data, message="更新成功")

    def delete(self, request, product_id):
        """删除商品"""
        product = self.get_object(product_id)
        if not product:
            return error(message="商品不存在", code=404)
        product.delete()
        return success(message="删除成功")


class ProductCategoriesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """获取品类列表"""
        categories = [c.label for c in Product.Category]
        return success(data=categories)
