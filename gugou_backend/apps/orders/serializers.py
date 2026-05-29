import logging
from decimal import Decimal

from rest_framework import serializers

from apps.common.id_generator import generate_order_id, generate_payment_id
from apps.market.models import Listing
from .models import Order, OrderStatusLog, PaymentRecord

logger = logging.getLogger("gugou")


class OrderCreateSerializer(serializers.Serializer):
    listing_id = serializers.CharField(max_length=25)
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate(self, attrs):
        from apps.credits.services import check_trading_permission, check_daily_order_limit

        user = self.context["request"].user

        # 检查信用分交易权限
        allowed, msg = check_trading_permission(user)
        if not allowed:
            raise serializers.ValidationError({"credit": msg})

        # 检查每日下单限制
        allowed, msg = check_daily_order_limit(user)
        if not allowed:
            raise serializers.ValidationError({"credit": msg})

        # 验证挂单存在
        try:
            listing = Listing.objects.get(listing_id=attrs["listing_id"])
        except Listing.DoesNotExist:
            raise serializers.ValidationError({"listing_id": "挂单不存在"})

        # 验证挂单状态
        if listing.status != Listing.Status.ACTIVE:
            raise serializers.ValidationError({"listing_id": "该挂单已不可购买"})

        # 验证购买数量
        if attrs["quantity"] > listing.quantity:
            raise serializers.ValidationError({"quantity": "购买数量超过挂单数量"})

        # 验证不能购买自己的挂单
        if listing.seller == user:
            raise serializers.ValidationError({"listing_id": "不能购买自己的挂单"})

        attrs["listing"] = listing
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        listing = validated_data["listing"]
        quantity = validated_data["quantity"]

        # 计算订单金额
        amount = listing.price * quantity

        # 生成订单编号
        order_id = generate_order_id()

        # 创建订单
        order = Order.objects.create(
            order_id=order_id,
            buyer=user,
            seller=listing.seller,
            listing=listing,
            product=listing.product,
            quantity=quantity,
            amount=amount,
            status=Order.Status.PENDING_PAYMENT,
        )

        # 锁定挂单
        listing.quantity -= quantity
        if listing.quantity == 0:
            listing.status = Listing.Status.LOCKED
        listing.save()

        # 记录状态变更日志
        OrderStatusLog.objects.create(
            log_id=f"LOG{order_id}",
            order=order,
            from_status="",
            to_status=Order.Status.PENDING_PAYMENT,
            operator=user,
            note="创建订单",
        )

        logger.info("用户 %s 创建订单 %s", user.user_id, order_id)
        return order


class PaymentCreateSerializer(serializers.Serializer):
    pay_method = serializers.ChoiceField(choices=PaymentRecord.PayMethod.choices, default=PaymentRecord.PayMethod.SIMULATED)

    def validate(self, attrs):
        order = self.instance
        if order.status != Order.Status.PENDING_PAYMENT:
            raise serializers.ValidationError("订单状态不允许支付")
        return attrs

    def update(self, instance, validated_data):
        return self.create(validated_data)

    def create(self, validated_data):
        order = self.instance
        user = self.context["request"].user

        # 生成支付流水号
        payment_id = generate_payment_id(user.user_id)

        # 创建支付记录
        payment = PaymentRecord.objects.create(
            payment_id=payment_id,
            order=order,
            payer=user,
            amount=order.amount,
            pay_method=validated_data["pay_method"],
            status=PaymentRecord.Status.PENDING,
        )

        logger.info("用户 %s 创建支付 %s", user.user_id, payment_id)
        return payment


class PaymentSuccessSerializer(serializers.Serializer):
    def validate(self, attrs):
        payment = self.instance
        if payment.status != PaymentRecord.Status.PENDING:
            raise serializers.ValidationError("支付状态不允许确认成功")
        return attrs

    def save(self):
        from apps.credits.services import create_credit_record
        from django.utils import timezone

        payment = self.instance
        order = payment.order

        # 更新支付状态
        payment.status = PaymentRecord.Status.SUCCESS
        payment.save()

        # 更新订单状态
        order.status = Order.Status.PAID
        order.paid_at = timezone.now()
        order.save()

        # 记录订单状态变更
        OrderStatusLog.objects.create(
            log_id=f"LOG{order.order_id}_PAID",
            order=order,
            from_status=Order.Status.PENDING_PAYMENT,
            to_status=Order.Status.PAID,
            operator=payment.payer,
            note="支付成功",
        )

        # 创建信用记录（买家获得信用）
        from apps.credits.services import CREDIT_ORDER_BUYER_COMPLETE
        create_credit_record(
            user=payment.payer,
            change_value=CREDIT_ORDER_BUYER_COMPLETE,
            reason=f"完成交易订单 {order.order_id}",
            related_order=order,
        )

        logger.info("订单 %s 支付成功", order.order_id)
        return payment


class OrderCompleteSerializer(serializers.Serializer):
    def validate(self, attrs):
        order = self.instance
        if order.status != Order.Status.PAID:
            raise serializers.ValidationError("订单状态不允许确认完成")
        return attrs

    def save(self):
        from apps.credits.services import create_credit_record

        order = self.instance

        # 更新订单状态
        order.status = Order.Status.COMPLETED
        from django.utils import timezone
        order.completed_at = timezone.now()
        order.save()

        # 记录订单状态变更
        OrderStatusLog.objects.create(
            log_id=f"LOG{order.order_id}_COMPLETED",
            order=order,
            from_status=Order.Status.PAID,
            to_status=Order.Status.COMPLETED,
            operator=order.buyer,
            note="订单完成",
        )

        # 更新挂单状态（如果所有数量都售出）
        listing = order.listing
        if listing.quantity == 0:
            listing.status = Listing.Status.SOLD
            listing.save()

        # 卖家获得信用
        from apps.credits.services import CREDIT_ORDER_SELLER_COMPLETE
        create_credit_record(
            user=order.seller,
            change_value=CREDIT_ORDER_SELLER_COMPLETE,
            reason=f"完成交易订单 {order.order_id}",
            related_order=order,
        )

        logger.info("订单 %s 已完成", order.order_id)
        return order


class OrderCancelSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=200, required=False, allow_blank=True, default="")

    def validate(self, attrs):
        order = self.instance
        if order.status not in (Order.Status.CREATED, Order.Status.PENDING_PAYMENT):
            raise serializers.ValidationError("当前订单状态不允许取消")
        return attrs

    def save(self):
        from apps.credits.services import (
            create_credit_record,
            CREDIT_ORDER_BUYER_CANCEL_PAID,
            CREDIT_ORDER_SELLER_CANCEL_LOCKED,
        )

        order = self.instance
        reason = self.validated_data.get("reason", "")
        original_status = order.status
        operator = self.context["request"].user

        # 更新订单状态
        order.status = Order.Status.CANCELLED
        order.save()

        # 释放挂单
        listing = order.listing
        listing.quantity += order.quantity
        if listing.status == Listing.Status.LOCKED:
            listing.status = Listing.Status.ACTIVE
        listing.save()

        # 记录订单状态变更
        OrderStatusLog.objects.create(
            log_id=f"LOG{order.order_id}_CANCELLED",
            order=order,
            from_status=original_status,
            to_status=Order.Status.CANCELLED,
            operator=operator,
            note=reason or "用户取消订单",
        )

        # 信用分处理
        if original_status == Order.Status.PAID:
            # 买家已付款后取消，扣信用
            create_credit_record(
                user=order.buyer,
                change_value=CREDIT_ORDER_BUYER_CANCEL_PAID,
                reason=f"已付款后取消订单 {order.order_id}",
                related_order=order,
            )
        elif original_status == Order.Status.PENDING_PAYMENT and operator == order.seller:
            # 卖家取消已锁定的待付款订单
            create_credit_record(
                user=order.seller,
                change_value=CREDIT_ORDER_SELLER_CANCEL_LOCKED,
                reason=f"卖家取消已锁定订单 {order.order_id}",
                related_order=order,
            )

        logger.info("订单 %s 已取消", order.order_id)
        return order


class OrderListSerializer(serializers.ModelSerializer):
    buyer_id = serializers.CharField(source="buyer.user_id", read_only=True)
    buyer_name = serializers.CharField(source="buyer.nickname", read_only=True)
    seller_id = serializers.CharField(source="seller.user_id", read_only=True)
    seller_name = serializers.CharField(source="seller.nickname", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = Order
        fields = [
            "order_id", "buyer_id", "buyer_name", "seller_id", "seller_name",
            "product_id", "product_name", "quantity", "amount", "status",
            "paid_at", "completed_at", "created_at",
        ]


class OrderDetailSerializer(serializers.ModelSerializer):
    buyer_id = serializers.CharField(source="buyer.user_id", read_only=True)
    buyer_name = serializers.CharField(source="buyer.nickname", read_only=True)
    seller_id = serializers.CharField(source="seller.user_id", read_only=True)
    seller_name = serializers.CharField(source="seller.nickname", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    payments = serializers.SerializerMethodField()
    status_logs = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "order_id", "buyer_id", "buyer_name", "seller_id", "seller_name",
            "listing_id", "product_id", "product_name", "quantity", "amount",
            "status", "paid_at", "completed_at", "created_at", "updated_at",
            "payments", "status_logs",
        ]

    def get_payments(self, obj):
        payments = obj.payments.all().order_by("-created_at")
        return PaymentRecordSerializer(payments, many=True).data

    def get_status_logs(self, obj):
        logs = obj.status_logs.all().order_by("-created_at")
        return OrderStatusLogSerializer(logs, many=True).data


class PaymentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentRecord
        fields = [
            "payment_id", "amount", "pay_method", "status",
            "third_trade_no", "created_at",
        ]


class OrderStatusLogSerializer(serializers.ModelSerializer):
    operator_id = serializers.CharField(source="operator.user_id", read_only=True)
    operator_name = serializers.CharField(source="operator.nickname", read_only=True)

    class Meta:
        model = OrderStatusLog
        fields = [
            "log_id", "from_status", "to_status", "operator_id",
            "operator_name", "note", "created_at",
        ]
