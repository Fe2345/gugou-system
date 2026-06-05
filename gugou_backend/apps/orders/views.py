import logging

from django.db.models import Q
from rest_framework.views import APIView

from apps.common.permissions import IsAuthenticated, IsAdmin
from apps.common.response import error, flatten_errors, paginated, success
from .models import Order, PaymentRecord
from .serializers import (
    OrderCancelSerializer,
    OrderCompleteSerializer,
    OrderCreateSerializer,
    OrderDetailSerializer,
    OrderListSerializer,
    OrderReturnApproveSerializer,
    OrderReturnRejectSerializer,
    OrderReturnSerializer,
    OrderUpdateAddressSerializer,
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
        return success(data=OrderDetailSerializer(order).data, message="Order created")


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return error(message="Order does not exist", code=404)

        if request.user not in (order.buyer, order.seller):
            return error(message="No permission to view this order", code=403)

        return success(data=OrderDetailSerializer(order).data)


class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))
        role = request.query_params.get("role", "buyer")
        status_filter = request.query_params.get("status")
        keyword = request.query_params.get("keyword", "").strip()

        if request.user.role == "admin":
            queryset = Order.objects.all()
        elif role == "seller":
            queryset = Order.objects.filter(seller=request.user)
        else:
            queryset = Order.objects.filter(buyer=request.user)

        if keyword:
            queryset = queryset.filter(
                Q(order_id__icontains=keyword)
                | Q(buyer__nickname__icontains=keyword)
                | Q(product__name__icontains=keyword)
            )

        if status_filter:
            statuses = [item.strip() for item in status_filter.split(",") if item.strip()]
            queryset = queryset.filter(status__in=statuses)

        queryset = queryset.order_by("-created_at")

        from django.core.paginator import Paginator

        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        serializer = OrderListSerializer(page_obj, many=True)
        return success(data=paginated(page_obj, serializer, page_size))


class PaymentCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return error(message="Order does not exist", code=404)

        if request.user != order.buyer:
            return error(message="No permission to pay this order", code=403)

        serializer = PaymentCreateSerializer(order, data=request.data, context={"request": request})
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors), code=400)
        payment = serializer.save()
        return success(data={"payment_id": payment.payment_id}, message="Payment created")


class PaymentSuccessView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id, payment_id):
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return error(message="Order does not exist", code=404)

        try:
            payment = PaymentRecord.objects.get(payment_id=payment_id, order=order)
        except PaymentRecord.DoesNotExist:
            return error(message="Payment record does not exist", code=404)

        if request.user != order.buyer:
            return error(message="No permission to operate this payment", code=403)

        serializer = PaymentSuccessSerializer(payment, data=request.data, context={"request": request})
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors), code=400)

        try:
            serializer.save()
        except Exception as e:
            logger.exception("Payment confirmation failed: %s", str(e))
            return error(message=f"Operation failed: {str(e)}", code=500)

        return success(message="Payment succeeded, order is waiting for receipt")


class OrderCompleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return error(message="Order does not exist", code=404)

        if request.user != order.buyer:
            return error(message="No permission to operate this order", code=403)

        serializer = OrderCompleteSerializer(order, data={})
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors), code=400)

        try:
            serializer.save()
        except Exception as e:
            logger.exception("Order receipt confirmation failed: %s", str(e))
            return error(message=f"Operation failed: {str(e)}", code=500)

        return success(message="Order receipt confirmed")


class OrderAddressUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return error(message="Order does not exist", code=404)

        if request.user != order.buyer:
            return error(message="No permission to operate this order", code=403)

        serializer = OrderUpdateAddressSerializer(order, data=request.data, context={"request": request})
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors), code=400)

        serializer.save()
        return success(data=OrderDetailSerializer(order).data, message="Shipping address updated")


class OrderReturnView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return error(message="Order does not exist", code=404)

        if request.user != order.buyer:
            return error(message="No permission to operate this order", code=403)

        serializer = OrderReturnSerializer(order, data=request.data, context={"request": request})
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors), code=400)

        try:
            serializer.save()
        except Exception as e:
            logger.exception("Order return application failed: %s", str(e))
            return error(message=f"Operation failed: {str(e)}", code=500)

        return success(message="Return application submitted, awaiting admin review")


class OrderReturnApproveView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return error(message="Order does not exist", code=404)

        serializer = OrderReturnApproveSerializer(order, data={}, context={"request": request})
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors), code=400)

        try:
            serializer.save()
        except Exception as e:
            logger.exception("Order return approval failed: %s", str(e))
            return error(message=f"Operation failed: {str(e)}", code=500)

        return success(message="Return approved, order refunded")


class OrderReturnRejectView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return error(message="Order does not exist", code=404)

        serializer = OrderReturnRejectSerializer(order, data=request.data, context={"request": request})
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors), code=400)

        try:
            serializer.save()
        except Exception as e:
            logger.exception("Order return rejection failed: %s", str(e))
            return error(message=f"Operation failed: {str(e)}", code=500)

        return success(message="Return rejected")


class OrderCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return error(message="Order does not exist", code=404)

        if request.user not in (order.buyer, order.seller):
            return error(message="No permission to operate this order", code=403)

        serializer = OrderCancelSerializer(order, data=request.data, context={"request": request})
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors), code=400)

        try:
            serializer.save()
        except Exception as e:
            logger.exception("Order cancellation failed: %s", str(e))
            return error(message=f"Operation failed: {str(e)}", code=500)

        return success(message="Order cancelled")
