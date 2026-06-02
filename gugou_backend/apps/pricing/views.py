from datetime import timedelta

from django.utils import timezone
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.common.response import success, error
from apps.pricing.models import PriceRecord
from apps.products.models import Product


def _build_price_item(product, days):
    """为单个商品构建价格分析数据"""
    now = timezone.now()
    start = now - timedelta(days=days)
    records = PriceRecord.objects.filter(
        product=product, recorded_at__gte=start
    ).order_by("recorded_at")

    if not records.exists():
        return None

    prices = [float(r.price) for r in records]
    current_price = prices[-1]
    avg_price = round(sum(prices) / len(prices), 2)
    max_price = max(prices)
    min_price = min(prices)
    first_price = prices[0]
    change_percent = round((current_price - first_price) / first_price * 100, 2) if first_price else 0

    # 按天聚合趋势
    trend_map = {}
    for r in records:
        day_key = r.recorded_at.strftime("%m-%d")
        trend_map.setdefault(day_key, []).append(float(r.price))
    trend = [{"date": k, "price": round(sum(v) / len(v), 2)} for k, v in trend_map.items()]

    # 最近交易记录（最多10条）
    recent = records.order_by("-recorded_at")[:10]
    transactions = [
        {
            "date": r.recorded_at.strftime("%Y-%m-%d %H:%M"),
            "name": product.name,
            "price": float(r.price),
            "condition": "全新",
            "method": r.get_source_display(),
        }
        for r in recent
    ]

    return {
        "id": product.product_id,
        "name": product.name,
        "ipName": product.ip_name,
        "characterName": product.character_name,
        "category": product.category,
        "currentPrice": current_price,
        "avgPrice": avg_price,
        "maxPrice": max_price,
        "minPrice": min_price,
        "changePercent": change_percent,
        "trend": trend,
        "transactions": transactions,
    }


class PriceQueryView(APIView):
    """价格查询：按关键词搜索商品并返回价格分析"""
    permission_classes = [AllowAny]

    def get(self, request):
        keyword = request.query_params.get("keyword", "").strip()
        range_str = request.query_params.get("range", "30d").strip()

        days_map = {"7d": 7, "30d": 30, "90d": 90}
        days = days_map.get(range_str, 30)

        if not keyword:
            return error(message="请输入搜索关键词")

        from django.db.models import Q
        products = Product.objects.filter(
            Q(name__icontains=keyword) |
            Q(ip_name__icontains=keyword) |
            Q(character_name__icontains=keyword)
        )

        if not products.exists():
            return success(data=None)

        product = products.first()
        item = _build_price_item(product, days)
        if not item:
            return success(data=None)

        return success(data=item)


class PriceHotView(APIView):
    """热门价格：返回有价格记录的热门商品"""
    permission_classes = [AllowAny]

    def get(self, request):
        product_ids = list(
            PriceRecord.objects.values_list("product_id", flat=True)
            .distinct()[:8]
        )
        products = Product.objects.filter(product_id__in=product_ids)

        items = []
        for product in products:
            item = _build_price_item(product, 30)
            if item:
                items.append(item)

        return success(data=items)
