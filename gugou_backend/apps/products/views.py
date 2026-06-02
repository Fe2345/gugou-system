from django.db.models import ProtectedError, Q
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.common.response import error, flatten_errors, success

from .models import Product
from .serializers import ProductCreateSerializer, ProductSerializer, ProductUpdateSerializer


class ProductListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        mine = request.query_params.get("mine", "").lower() in ("1", "true", "yes")
        if mine:
            if not request.user or not request.user.is_authenticated:
                return error(message="请先登录", code=401)
            queryset = Product.objects.filter(created_by=request.user).order_by("-created_at")
        else:
            queryset = Product.objects.filter(status=Product.Status.ACTIVE).order_by("-created_at")

        keyword = request.query_params.get("keyword", "").strip()
        if keyword:
            queryset = queryset.filter(
                Q(name__icontains=keyword)
                | Q(ip_name__icontains=keyword)
                | Q(character_name__icontains=keyword)
            )

        category = request.query_params.get("category", "").strip()
        if category:
            queryset = queryset.filter(category=category)

        ip_name = request.query_params.get("ipName", "").strip()
        if ip_name:
            queryset = queryset.filter(ip_name__icontains=ip_name)

        character_name = request.query_params.get("characterName", "").strip()
        if character_name:
            queryset = queryset.filter(character_name__icontains=character_name)

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
        if not request.user or not request.user.is_authenticated:
            return error(message="请先登录", code=401)
        if getattr(request.user, "role", "") == "admin":
            return error(message="管理员不能添加商品，请由用户提交后审核", code=403)

        serializer = ProductCreateSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors))
        product = serializer.save()
        return success(data=ProductSerializer(product).data, message="提交成功，请等待管理员审核")


class ProductDetailView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, product_id):
        try:
            return Product.objects.get(product_id=product_id)
        except Product.DoesNotExist:
            return None

    def get(self, request, product_id):
        product = self.get_object(product_id)
        if not product:
            return error(message="商品不存在", code=404)

        is_owner = (
            request.user
            and request.user.is_authenticated
            and product.created_by_id == request.user.pk
        )
        is_admin = (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", "") == "admin"
        )
        if product.status != Product.Status.ACTIVE and not (is_owner or is_admin):
            return error(message="商品不存在", code=404)

        return success(data=ProductSerializer(product).data)

    def put(self, request, product_id):
        if not request.user or not request.user.is_authenticated:
            return error(message="请先登录", code=401)
        if getattr(request.user, "role", "") == "admin":
            return error(message="管理员不能修改商品信息", code=403)

        product = self.get_object(product_id)
        if not product:
            return error(message="商品不存在", code=404)
        if product.created_by_id != request.user.pk:
            return error(message="只能修改自己提交的商品", code=403)
        if product.status != Product.Status.INACTIVE:
            return error(message="商品已上架或已处理，不能修改", code=400)

        serializer = ProductUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors))

        data = dict(serializer.validated_data)
        data.pop("status", None)
        serializer.update(product, data)
        return success(data=ProductSerializer(product).data, message="更新成功")

    def delete(self, request, product_id):
        if not request.user or not request.user.is_authenticated:
            return error(message="请先登录", code=401)
        if getattr(request.user, "role", "") == "admin":
            return error(message="管理员不能删除用户商品", code=403)

        product = self.get_object(product_id)
        if not product:
            return error(message="商品不存在", code=404)
        if product.created_by_id != request.user.pk:
            return error(message="只能删除自己提交的商品", code=403)
        if product.status != Product.Status.INACTIVE:
            return error(message="只能删除待审核的商品", code=400)

        try:
            product.delete()
        except ProtectedError:
            return error(message="该商品已被资产、挂单或订单引用，无法删除", code=400)
        return success(message="删除成功")


class ProductCategoriesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        categories = [{"value": c.value, "label": c.label} for c in Product.Category]
        return success(data=categories)
