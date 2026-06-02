from datetime import datetime, timedelta

from django.db.models import Q
from django.utils import timezone
from rest_framework.views import APIView

from apps.common.id_generator import generate_price_record_id
from apps.common.permissions import IsAdmin
from apps.common.response import error, success
from apps.pricing.models import PriceRecord
from apps.products.models import Product


def _parse_date(value, end_of_day=False):
    if not value:
        return None
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return None
    if end_of_day:
        parsed = parsed.replace(hour=23, minute=59, second=59)
    return timezone.make_aware(parsed, timezone.get_current_timezone())


def _serialize_record(record):
    return {
        "id": record.price_record_id,
        "productId": record.product_id,
        "name": record.product.name,
        "price": float(record.price),
        "period": record.source,
        "change": 0,
        "time": record.recorded_at.strftime("%Y-%m-%d %H:%M"),
    }


class AdminPriceRecordListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        keyword = request.query_params.get("keyword", "").strip()
        product_id = request.query_params.get("productId", "").strip()
        start_date = _parse_date(request.query_params.get("startDate", "").strip())
        end_date = _parse_date(request.query_params.get("endDate", "").strip(), end_of_day=True)

        queryset = PriceRecord.objects.select_related("product").order_by("-recorded_at")
        if keyword:
            queryset = queryset.filter(
                Q(price_record_id__icontains=keyword)
                | Q(product__name__icontains=keyword)
                | Q(product__ip_name__icontains=keyword)
                | Q(product__character_name__icontains=keyword)
            )
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        if start_date:
            queryset = queryset.filter(recorded_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(recorded_at__lte=end_date)

        records = list(queryset[:200])
        data = [_serialize_record(record) for record in records]

        previous = None
        for item in reversed(data):
            if previous and previous["price"]:
                item["change"] = round((item["price"] - previous["price"]) / previous["price"] * 100, 2)
            previous = item

        return success(data=data)

    def post(self, request):
        product_id = request.data.get("productId") or request.data.get("product_id")
        product_name = (request.data.get("name") or "").strip()
        price = request.data.get("price")
        recorded_at = request.data.get("recordedAt") or request.data.get("recorded_at")

        if not price:
            return error(message="请填写价格")

        product = None
        if product_id:
            product = Product.objects.filter(product_id=product_id).first()
        if not product and product_name:
            product = Product.objects.filter(name=product_name).first()
        if not product:
            return error(message="商品不存在，请先在商品管理中添加商品", code=404)

        record_time = timezone.now()
        if recorded_at:
            parsed = _parse_date(recorded_at)
            if parsed:
                record_time = parsed

        record = PriceRecord.objects.create(
            price_record_id=generate_price_record_id(),
            product=product,
            price=price,
            source=PriceRecord.Source.MANUAL,
            recorded_at=record_time,
        )
        return success(data=_serialize_record(record), message="创建成功")


class AdminPriceHistoryView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        product_id = request.query_params.get("productId", "").strip()
        start_date = _parse_date(request.query_params.get("startDate", "").strip())
        end_date = _parse_date(request.query_params.get("endDate", "").strip(), end_of_day=True)
        range_value = request.query_params.get("range", "").strip()

        if not product_id:
            return error(message="请选择商品")

        queryset = PriceRecord.objects.filter(product_id=product_id).order_by("recorded_at")
        if range_value and not start_date:
            days_map = {"7d": 7, "30d": 30, "90d": 90, "180d": 180, "1y": 365}
            days = days_map.get(range_value)
            if days:
                queryset = queryset.filter(recorded_at__gte=timezone.now() - timedelta(days=days))
        if start_date:
            queryset = queryset.filter(recorded_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(recorded_at__lte=end_date)

        records = list(queryset)
        points = [
            {
                "date": record.recorded_at.strftime("%Y-%m-%d"),
                "time": record.recorded_at.strftime("%Y-%m-%d %H:%M"),
                "price": float(record.price),
            }
            for record in records
        ]

        return success(data={
            "productId": product_id,
            "points": points,
        })
