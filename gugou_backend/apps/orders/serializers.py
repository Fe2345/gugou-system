import logging

from rest_framework import serializers

from apps.common.id_generator import generate_order_id, generate_payment_id
from apps.market.models import Listing
from .models import Order, OrderStatusLog, PaymentRecord

logger = logging.getLogger("gugou")


def apply_shipping_address(order, address):
    order.shipping_address = address
    order.receiver_name = address.receiver_name
    order.receiver_phone = address.receiver_phone
    order.shipping_address_text = (
        f"{address.province.name}{address.city.name}{address.district.name}"
        f"{address.street}{address.detail}"
    )


def build_order_log_id(order, suffix):
    count = OrderStatusLog.objects.filter(order=order).count() + 1
    return f"L{order.order_id[-20:]}{suffix}{count:02d}"


class OrderCreateSerializer(serializers.Serializer):
    listing_id = serializers.CharField(max_length=25)
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate(self, attrs):
        from apps.credits.services import check_daily_order_limit, check_trading_permission

        user = self.context["request"].user

        allowed, msg = check_trading_permission(user)
        if not allowed:
            raise serializers.ValidationError({"credit": msg})

        allowed, msg = check_daily_order_limit(user)
        if not allowed:
            raise serializers.ValidationError({"credit": msg})

        try:
            listing = Listing.objects.get(listing_id=attrs["listing_id"])
        except Listing.DoesNotExist:
            raise serializers.ValidationError({"listing_id": "Listing does not exist"})

        if listing.status != Listing.Status.ACTIVE:
            raise serializers.ValidationError({"listing_id": "Listing is not available"})

        if attrs["quantity"] > listing.quantity:
            raise serializers.ValidationError({"quantity": "Quantity exceeds listing stock"})

        if listing.seller == user:
            raise serializers.ValidationError({"listing_id": "Cannot buy your own listing"})

        attrs["listing"] = listing
        return attrs

    def create(self, validated_data):
        from django.db import transaction
        from apps.assets.models import AssetFlow, UserAsset
        from apps.common.id_generator import generate_asset_flow_id

        user = self.context["request"].user
        listing = validated_data["listing"]
        quantity = validated_data["quantity"]
        amount = listing.price * quantity
        order_id = generate_order_id()

        with transaction.atomic():
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

            listing.quantity -= quantity
            if listing.quantity == 0:
                listing.status = Listing.Status.LOCKED
            listing.save()

            if listing.asset:
                asset = listing.asset
                asset.status = UserAsset.Status.SELLING
                asset.save()

                AssetFlow.objects.create(
                    flow_id=generate_asset_flow_id(),
                    asset=asset,
                    from_user=listing.seller,
                    to_user=None,
                    flow_type=AssetFlow.FlowType.LOCK,
                    related_order=order_id,
                    note=f"Order {order_id} created, asset locked",
                )

            OrderStatusLog.objects.create(
                log_id=f"L{order_id}",
                order=order,
                from_status="",
                to_status=Order.Status.PENDING_PAYMENT,
                operator=user,
                note="Order created",
            )

        logger.info("User %s created order %s", user.user_id, order_id)
        return order


class PaymentCreateSerializer(serializers.Serializer):
    pay_method = serializers.ChoiceField(
        choices=PaymentRecord.PayMethod.choices,
        default=PaymentRecord.PayMethod.SIMULATED,
    )

    def validate(self, attrs):
        order = self.instance
        if order.status != Order.Status.PENDING_PAYMENT:
            raise serializers.ValidationError("Order status does not allow payment")
        return attrs

    def update(self, instance, validated_data):
        return self.create(validated_data)

    def create(self, validated_data):
        order = self.instance
        user = self.context["request"].user
        payment_id = generate_payment_id(user.user_id)

        payment = PaymentRecord.objects.create(
            payment_id=payment_id,
            order=order,
            payer=user,
            amount=order.amount,
            pay_method=validated_data["pay_method"],
            status=PaymentRecord.Status.PENDING,
        )

        logger.info("User %s created payment %s", user.user_id, payment_id)
        return payment


class PaymentSuccessSerializer(serializers.Serializer):
    address_id = serializers.IntegerField()

    def validate_address_id(self, value):
        from apps.addresses.models import Address

        user = self.context["request"].user
        try:
            return Address.objects.select_related("province", "city", "district").get(id=value, user=user)
        except Address.DoesNotExist:
            raise serializers.ValidationError("Please select a valid shipping address")

    def validate(self, attrs):
        payment = self.instance
        if payment.status != PaymentRecord.Status.PENDING:
            raise serializers.ValidationError("Payment status does not allow success confirmation")
        if payment.order.status != Order.Status.PENDING_PAYMENT:
            raise serializers.ValidationError("Order status does not allow payment confirmation")
        return attrs

    def save(self):
        from django.db import transaction
        from django.utils import timezone

        payment = self.instance
        order = payment.order
        address = self.validated_data["address_id"]

        with transaction.atomic():
            payment.status = PaymentRecord.Status.SUCCESS
            payment.save(update_fields=["status", "updated_at"])

            old_status = order.status
            order.status = Order.Status.RECEIVING
            order.paid_at = timezone.now()
            apply_shipping_address(order, address)
            order.save()

            OrderStatusLog.objects.create(
                log_id=build_order_log_id(order, "P"),
                order=order,
                from_status=old_status,
                to_status=Order.Status.RECEIVING,
                operator=payment.payer,
                note="Payment succeeded, waiting for receipt",
            )

        logger.info("Order %s paid and waiting for receipt", order.order_id)
        return payment


class OrderUpdateAddressSerializer(serializers.Serializer):
    address_id = serializers.IntegerField()

    def validate_address_id(self, value):
        from apps.addresses.models import Address

        user = self.context["request"].user
        try:
            return Address.objects.select_related("province", "city", "district").get(id=value, user=user)
        except Address.DoesNotExist:
            raise serializers.ValidationError("Please select a valid shipping address")

    def validate(self, attrs):
        order = self.instance
        if order.status != Order.Status.RECEIVING:
            raise serializers.ValidationError("Only receiving orders can update shipping address")
        return attrs

    def save(self):
        from django.db import transaction

        order = self.instance
        address = self.validated_data["address_id"]

        with transaction.atomic():
            apply_shipping_address(order, address)
            order.save()
            OrderStatusLog.objects.create(
                log_id=build_order_log_id(order, "A"),
                order=order,
                from_status=order.status,
                to_status=order.status,
                operator=self.context["request"].user,
                note="Shipping address updated",
            )
        return order


class OrderCompleteSerializer(serializers.Serializer):
    def validate(self, attrs):
        order = self.instance
        if order.status != Order.Status.RECEIVING:
            raise serializers.ValidationError("Only receiving orders can be completed")
        return attrs

    def save(self):
        from django.db import transaction
        from django.utils import timezone
        from apps.assets.models import AssetFlow, UserAsset
        from apps.common.id_generator import generate_asset_flow_id, generate_price_record_id
        from apps.credits.services import (
            CREDIT_ORDER_BUYER_COMPLETE,
            CREDIT_ORDER_SELLER_COMPLETE,
            create_credit_record,
        )
        from apps.pricing.models import PriceRecord

        order = self.instance

        with transaction.atomic():
            order.status = Order.Status.COMPLETED
            order.completed_at = timezone.now()
            order.save(update_fields=["status", "completed_at", "updated_at"])

            OrderStatusLog.objects.create(
                log_id=build_order_log_id(order, "C"),
                order=order,
                from_status=Order.Status.RECEIVING,
                to_status=Order.Status.COMPLETED,
                operator=order.buyer,
                note="Buyer confirmed receipt, order completed",
            )

            unit_price = order.amount / order.quantity if order.quantity > 0 else order.amount
            PriceRecord.objects.create(
                price_record_id=generate_price_record_id(),
                product=order.product,
                price=unit_price,
                source=PriceRecord.Source.ORDER,
                recorded_at=order.completed_at,
            )

            listing = order.listing
            if listing.quantity == 0:
                listing.status = Listing.Status.SOLD
                listing.save()

            if listing.asset:
                asset = listing.asset
                asset.status = UserAsset.Status.SOLD
                asset.save()

                AssetFlow.objects.create(
                    flow_id=generate_asset_flow_id(),
                    asset=asset,
                    from_user=order.seller,
                    to_user=order.buyer,
                    flow_type=AssetFlow.FlowType.SELL,
                    related_order=order.order_id,
                    note=f"Order {order.order_id} completed, asset sold",
                )

            create_credit_record(
                user=order.buyer,
                change_value=CREDIT_ORDER_BUYER_COMPLETE,
                reason=f"Confirmed receipt for order {order.order_id}",
                related_order=order,
            )
            create_credit_record(
                user=order.seller,
                change_value=CREDIT_ORDER_SELLER_COMPLETE,
                reason=f"Completed order {order.order_id}",
                related_order=order,
            )

        logger.info("Order %s completed", order.order_id)
        return order


class OrderReturnSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=200, required=False, allow_blank=True, default="")

    def validate(self, attrs):
        order = self.instance
        if order.status != Order.Status.RECEIVING:
            raise serializers.ValidationError("Only receiving orders can be returned")
        return attrs

    def save(self):
        from django.db import transaction
        from apps.assets.models import AssetFlow, UserAsset
        from apps.common.id_generator import generate_asset_flow_id
        from apps.credits.services import CREDIT_ORDER_BUYER_RETURN, create_credit_record

        order = self.instance
        reason = self.validated_data.get("reason", "")
        operator = self.context["request"].user

        with transaction.atomic():
            order.status = Order.Status.REFUNDED
            order.save(update_fields=["status", "updated_at"])

            PaymentRecord.objects.filter(order=order, status=PaymentRecord.Status.SUCCESS).update(
                status=PaymentRecord.Status.REFUNDED
            )

            listing = order.listing
            listing.quantity += order.quantity
            if listing.status in [Listing.Status.LOCKED, Listing.Status.SOLD]:
                listing.status = Listing.Status.ACTIVE
            listing.save()

            if listing.asset and listing.asset.status == UserAsset.Status.SELLING:
                asset = listing.asset
                asset.status = UserAsset.Status.HOLDING
                asset.save()

                AssetFlow.objects.create(
                    flow_id=generate_asset_flow_id(),
                    asset=asset,
                    from_user=None,
                    to_user=order.seller,
                    flow_type=AssetFlow.FlowType.UNLOCK,
                    related_order=order.order_id,
                    note=f"Order {order.order_id} returned, asset unlocked",
                )

            OrderStatusLog.objects.create(
                log_id=build_order_log_id(order, "R"),
                order=order,
                from_status=Order.Status.RECEIVING,
                to_status=Order.Status.REFUNDED,
                operator=operator,
                note=reason or "Buyer returned goods",
            )

            create_credit_record(
                user=order.buyer,
                change_value=CREDIT_ORDER_BUYER_RETURN,
                reason=f"Returned order {order.order_id}",
                related_order=order,
            )

        logger.info("Order %s returned", order.order_id)
        return order


class OrderCancelSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=200, required=False, allow_blank=True, default="")

    def validate(self, attrs):
        order = self.instance
        if order.status not in (Order.Status.CREATED, Order.Status.PENDING_PAYMENT):
            raise serializers.ValidationError("Current order status does not allow cancellation")
        return attrs

    def save(self):
        from django.db import transaction
        from apps.assets.models import AssetFlow, UserAsset
        from apps.common.id_generator import generate_asset_flow_id
        from apps.credits.services import CREDIT_ORDER_SELLER_CANCEL_LOCKED, create_credit_record

        order = self.instance
        reason = self.validated_data.get("reason", "")
        original_status = order.status
        operator = self.context["request"].user

        with transaction.atomic():
            order.status = Order.Status.CANCELLED
            order.save(update_fields=["status", "updated_at"])

            listing = order.listing
            listing.quantity += order.quantity
            if listing.status == Listing.Status.LOCKED:
                listing.status = Listing.Status.ACTIVE
            listing.save()

            if listing.asset and listing.asset.status == UserAsset.Status.SELLING:
                asset = listing.asset
                asset.status = UserAsset.Status.HOLDING
                asset.save()

                AssetFlow.objects.create(
                    flow_id=generate_asset_flow_id(),
                    asset=asset,
                    from_user=None,
                    to_user=order.seller,
                    flow_type=AssetFlow.FlowType.UNLOCK,
                    related_order=order.order_id,
                    note=f"Order {order.order_id} cancelled, asset unlocked",
                )

            OrderStatusLog.objects.create(
                log_id=build_order_log_id(order, "X"),
                order=order,
                from_status=original_status,
                to_status=Order.Status.CANCELLED,
                operator=operator,
                note=reason or "Order cancelled",
            )

            if original_status == Order.Status.PENDING_PAYMENT and operator == order.seller:
                create_credit_record(
                    user=order.seller,
                    change_value=CREDIT_ORDER_SELLER_CANCEL_LOCKED,
                    reason=f"Seller cancelled locked order {order.order_id}",
                    related_order=order,
                )

        logger.info("Order %s cancelled", order.order_id)
        return order


class OrderListSerializer(serializers.ModelSerializer):
    buyer_id = serializers.CharField(source="buyer.user_id", read_only=True)
    buyer_name = serializers.CharField(source="buyer.nickname", read_only=True)
    seller_id = serializers.CharField(source="seller.user_id", read_only=True)
    seller_name = serializers.CharField(source="seller.nickname", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    shipping_address_id = serializers.IntegerField(source="shipping_address.id", read_only=True, default=None)

    class Meta:
        model = Order
        fields = [
            "order_id", "buyer_id", "buyer_name", "seller_id", "seller_name",
            "product_id", "product_name", "quantity", "amount", "status",
            "paid_at", "completed_at", "created_at", "shipping_address_id",
            "receiver_name", "receiver_phone", "shipping_address_text",
        ]


class OrderDetailSerializer(serializers.ModelSerializer):
    buyer_id = serializers.CharField(source="buyer.user_id", read_only=True)
    buyer_name = serializers.CharField(source="buyer.nickname", read_only=True)
    seller_id = serializers.CharField(source="seller.user_id", read_only=True)
    seller_name = serializers.CharField(source="seller.nickname", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    shipping_address_id = serializers.IntegerField(source="shipping_address.id", read_only=True, default=None)
    payments = serializers.SerializerMethodField()
    status_logs = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "order_id", "buyer_id", "buyer_name", "seller_id", "seller_name",
            "listing_id", "product_id", "product_name", "quantity", "amount",
            "status", "paid_at", "completed_at", "created_at", "updated_at",
            "shipping_address_id", "receiver_name", "receiver_phone",
            "shipping_address_text", "payments", "status_logs",
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
