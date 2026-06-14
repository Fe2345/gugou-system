from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from apps.common.response import success, error, flatten_errors
from .models import UserAsset
from .serializers import AssetSerializer, AssetCreateSerializer, AssetUpdateSerializer, AssetOperateSerializer


class AssetListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """获取资产列表，支持 keyword/status/category/sortBy 筛选"""
        queryset = UserAsset.objects.select_related("product").order_by("-created_at")
        if request.user and request.user.is_authenticated:
            queryset = queryset.filter(owner=request.user)

        keyword = request.query_params.get("keyword", "").strip()
        if keyword:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(product__name__icontains=keyword) |
                Q(product__ip_name__icontains=keyword) |
                Q(product__character_name__icontains=keyword)
            )

        status = request.query_params.get("status", "").strip()
        if status and status != "all":
            queryset = queryset.filter(status=status)

        category = request.query_params.get("category", "").strip()
        if category:
            queryset = queryset.filter(product__category=category)

        sort_by = request.query_params.get("sortBy", "").strip()
        if sort_by == "value":
            queryset = queryset.order_by("-current_value")
        elif sort_by == "change":
            from django.db.models import F
            queryset = queryset.order_by(F("current_value") - F("acquire_price"))

        serializer = AssetSerializer(queryset, many=True)
        assets = serializer.data

        # 计算资产概览
        total_count = sum(a["quantity"] for a in assets)
        category_count = len(set(a["category"] for a in assets))
        total_cost = sum(float(a["acquirePrice"]) * a["quantity"] for a in assets)
        total_value = sum(float(a["currentValue"]) * a["quantity"] for a in assets)
        value_change = total_value - total_cost

        return success(data={
            "list": assets,
            "summary": {
                "totalCount": total_count,
                "categoryCount": category_count,
                "totalCost": total_cost,
                "totalValue": total_value,
                "valueChange": value_change,
            }
        })

    def post(self, request):
        """创建资产"""
        if not request.user or not request.user.is_authenticated:
            return error(message="请先登录", code=401)
        serializer = AssetCreateSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors))
        asset = serializer.save()
        return success(data=AssetSerializer(asset).data, message="创建成功")


class AssetDetailView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, asset_id):
        try:
            return UserAsset.objects.select_related("product").get(asset_id=asset_id)
        except UserAsset.DoesNotExist:
            return None

    def get(self, request, asset_id):
        """获取资产详情"""
        asset = self.get_object(asset_id)
        if not asset:
            return error(message="资产不存在", code=404)
        return success(data=AssetSerializer(asset).data)

    def put(self, request, asset_id):
        """更新资产"""
        asset = self.get_object(asset_id)
        if not asset:
            return error(message="资产不存在", code=404)

        serializer = AssetUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors))
        serializer.update(asset, serializer.validated_data)
        return success(data=AssetSerializer(asset).data, message="更新成功")

    def delete(self, request, asset_id):
        """删除资产"""
        asset = self.get_object(asset_id)
        if not asset:
            return error(message="资产不存在", code=404)

        # 检查是否有活跃的换物请求引用此资产
        from apps.exchanges.models import ExchangeRequest, ExchangeMatch
        active_exchanges = ExchangeRequest.objects.filter(
            offered_asset=asset,
            status__in=["active", "matched"]
        ).exists()
        if active_exchanges:
            return error(message="该资产正在换物中，无法删除", code=400)

        active_matches = ExchangeMatch.objects.filter(
            applicant_asset=asset,
            status__in=["pending", "accepted"]
        ).exists()
        if active_matches:
            return error(message="该资产正在换物匹配中，无法删除", code=400)

        # 检查是否有活跃的挂单
        from apps.market.models import Listing
        active_listings = Listing.objects.filter(
            asset=asset,
            status="active"
        ).exists()
        if active_listings:
            return error(message="该资产正在市场挂单中，无法删除", code=400)

        asset.delete()
        return success(message="删除成功")


class AssetOperateView(APIView):
    """资产操作：上架、下架、卖出"""
    permission_classes = [AllowAny]

    def post(self, request, asset_id):
        serializer = AssetOperateSerializer(data={**request.data, "assetId": asset_id})
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors))

        try:
            asset = UserAsset.objects.get(asset_id=asset_id)
        except UserAsset.DoesNotExist:
            return error(message="资产不存在", code=404)

        # 检查资产是否已被订单锁定
        from apps.market.models import Listing
        from apps.orders.models import Order

        # 检查是否有活跃的挂单关联此资产
        active_listing = Listing.objects.filter(
            asset=asset,
            status__in=[Listing.Status.ACTIVE, Listing.Status.LOCKED]
        ).first()

        if active_listing:
            # 检查是否有未完成的订单
            active_order = Order.objects.filter(
                listing=active_listing,
                status__in=[Order.Status.PENDING_PAYMENT, Order.Status.PAID]
            ).exists()

            if active_order:
                return error(message="该资产已被订单锁定，无法进行操作", code=400)

        op_type = serializer.validated_data["type"]
        status_map = {
            "list": UserAsset.Status.SELLING,
            "delist": UserAsset.Status.HOLDING,
            "sold": UserAsset.Status.SOLD,
        }

        # 验证操作合法性
        if op_type == "list" and asset.status != UserAsset.Status.HOLDING:
            return error(message="只有持有中的资产才能上架", code=400)
        elif op_type == "delist" and asset.status != UserAsset.Status.SELLING:
            return error(message="只有出售中的资产才能下架", code=400)
        elif op_type == "sold" and asset.status != UserAsset.Status.SELLING:
            return error(message="只有出售中的资产才能标记为已售出", code=400)

        asset.status = status_map[op_type]
        asset.save()
        return success(message="操作成功")
