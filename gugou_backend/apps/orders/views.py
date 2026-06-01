import logging

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.common.permissions import IsAuthenticated
from apps.common.response import error, flatten_errors, success, paginated
from .models import Order, PaymentRecord
from .serializers import (
    OrderCancelSerializer,
    OrderCompleteSerializer,
    OrderCreateSerializer,
    OrderDetailSerializer,
    OrderListSerializer,
    PaymentCreateSerializer,
    PaymentSuccessSerializer,
)

logger = logging.getLogger("gugou")


class OrderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors), code=400)
        order = serializer.save()
        data = OrderDetailSerializer(order).data
        return success(data=data, message="订单创建成功")


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return error(message="订单不存在", code=404)

        # 验证权限：只有买家和卖家可以查看
        if request.user not in (order.buyer, order.seller):
            return error(message="无权查看此订单", code=403)

        data = OrderDetailSerializer(order).data
        return success(data=data)


class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))
        role = request.query_params.get("role", "buyer")  # buyer 或 seller
        status_filter = request.query_params.get("status")

        # 根据角色筛选
        if role == "seller":
            queryset = Order.objects.filter(seller=request.user)
        else:
            queryset = Order.objects.filter(buyer=request.user)

        # 按状态筛选
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # 排序
        queryset = queryset.order_by("-created_at")

        # 分页
        from django.core.paginator import Paginator
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        serializer = OrderListSerializer(page_obj, many=True)
        data = paginated(page_obj, serializer, page_size)

        return success(data=data)


class PaymentCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return error(message="订单不存在", code=404)

        # 验证权限：只有买家可以支付
        if request.user != order.buyer:
            return error(message="无权支付此订单", code=403)

        serializer = PaymentCreateSerializer(order, data=request.data, context={"request": request})
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors), code=400)
        payment = serializer.save()
        return success(data={"payment_id": payment.payment_id}, message="支付创建成功")


class PaymentSuccessView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id, payment_id):
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return error(message="订单不存在", code=404)

        try:
            payment = PaymentRecord.objects.get(payment_id=payment_id, order=order)
        except PaymentRecord.DoesNotExist:
            return error(message="支付记录不存在", code=404)

        # 验证权限：只有买家可以确认支付成功
        if request.user != order.buyer:
            return error(message="无权操作此支付", code=403)

        serializer = PaymentSuccessSerializer(payment, data={})
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors), code=400)
        serializer.save()
        return success(message="支付成功")


class OrderCompleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return error(message="订单不存在", code=404)

        # 验证权限：只有买家可以确认完成
        if request.user != order.buyer:
            return error(message="无权操作此订单", code=403)

        serializer = OrderCompleteSerializer(order, data={})
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors), code=400)
        serializer.save()
        return success(message="订单已完成")


class OrderCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return error(message="订单不存在", code=404)

        # 验证权限：买家和卖家都可以取消
        if request.user not in (order.buyer, order.seller):
            return error(message="无权操作此订单", code=403)

        serializer = OrderCancelSerializer(order, data=request.data, context={"request": request})
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors), code=400)
        serializer.save()
        return success(message="订单已取消")
