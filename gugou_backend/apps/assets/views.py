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

        op_type = serializer.validated_data["type"]
        status_map = {
            "list": UserAsset.Status.SELLING,
            "delist": UserAsset.Status.HOLDING,
            "sold": UserAsset.Status.SOLD,
        }
        asset.status = status_map[op_type]
        asset.save()
        return success(message="操作成功")
