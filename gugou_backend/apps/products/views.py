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

    def _check_product_in_use(self, product):
        """检查商品是否被其他模块使用，返回 (是否在使用中, 提示信息)"""
        from apps.assets.models import UserAsset
        from apps.market.models import Listing
        from apps.orders.models import Order
        from apps.teams.models import TeamProject

        if UserAsset.objects.filter(product=product).exists():
            return True, "该商品已被用户持有为资产，无法操作"
        if Listing.objects.filter(product=product, status__in=["active", "locked"]).exists():
            return True, "该商品有活跃的市场挂单，无法操作"
        if Order.objects.filter(product=product).exclude(status="cancelled").exists():
            return True, "该商品有相关的订单，无法操作"
        if TeamProject.objects.filter(product=product).exists():
            return True, "该商品有相关的拼团项目，无法操作"
        return False, ""

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

        # inactive 状态可直接修改，active 状态需要检查是否在使用中
        if product.status == Product.Status.ACTIVE:
            in_use, msg = self._check_product_in_use(product)
            if in_use:
                return error(message=msg, code=400)
        elif product.status != Product.Status.INACTIVE:
            return error(message="当前商品状态不能修改", code=400)

        serializer = ProductUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors))

        data = dict(serializer.validated_data)
        data.pop("status", None)
        serializer.update(product, data)

        # active 状态的商品修改后变为 inactive（待审核）
        if product.status == Product.Status.ACTIVE:
            product.status = Product.Status.INACTIVE
            product.save()

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

        # inactive 状态可直接删除，active 状态需要检查是否在使用中
        if product.status == Product.Status.ACTIVE:
            in_use, msg = self._check_product_in_use(product)
            if in_use:
                return error(message=msg, code=400)
        elif product.status != Product.Status.INACTIVE:
            return error(message="当前商品状态不能删除", code=400)

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
