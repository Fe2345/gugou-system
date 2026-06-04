import logging
from decimal import Decimal

from rest_framework import serializers

from .models import Listing, ListingImage

logger = logging.getLogger("gugou")


class ListingImageSerializer(serializers.Serializer):
    image_url = serializers.CharField(max_length=500)
    sort_order = serializers.IntegerField(required=False, default=0)


class ListingCreateSerializer(serializers.Serializer):
    product_id = serializers.CharField(max_length=25)
    asset_id = serializers.CharField(max_length=25)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("0.01"))
    quantity = serializers.IntegerField(min_value=1, default=1)
    description = serializers.CharField(max_length=500, required=False, allow_blank=True, default="")
    images = ListingImageSerializer(many=True, required=False, default=[])

    def validate(self, attrs):
        from apps.products.models import Product
        from apps.assets.models import UserAsset

        # 验证商品存在
        try:
            product = Product.objects.get(product_id=attrs["product_id"])
        except Product.DoesNotExist:
            raise serializers.ValidationError({"product_id": "商品不存在"})
        if product.status != Product.Status.ACTIVE:
            raise serializers.ValidationError({"product_id": "商品尚未上架，不能发布到交易市场"})

        # 验证资产存在且属于当前用户
        try:
            asset = UserAsset.objects.get(asset_id=attrs["asset_id"])
        except UserAsset.DoesNotExist:
            raise serializers.ValidationError({"asset_id": "资产不存在"})

        # 验证资产归属
        user = self.context["request"].user
        if asset.owner != user:
            raise serializers.ValidationError({"asset_id": "只能使用自己的资产"})

        if asset.product_id != product.product_id:
            raise serializers.ValidationError({"asset_id": "所选资产与商品不匹配"})

        # 验证资产数量足够
        if asset.quantity < attrs["quantity"]:
            raise serializers.ValidationError({"quantity": "资产数量不足"})

        attrs["product"] = product
        attrs["asset"] = asset
        return attrs

    def create(self, validated_data):
        from apps.common.id_generator import generate_exchange_id

        user = self.context["request"].user
        images_data = validated_data.pop("images", [])

        # 生成挂单编号
        listing_id = f"L{generate_exchange_id()[1:]}"

        # 创建挂单
        listing = Listing.objects.create(
            listing_id=listing_id,
            seller=user,
            asset=validated_data["asset"],
            product=validated_data["product"],
            price=validated_data["price"],
            quantity=validated_data["quantity"],
            description=validated_data.get("description", ""),
        )

        # 创建图片
        for img_data in images_data:
            ListingImage.objects.create(
                listing=listing,
                image_url=img_data["image_url"],
                sort_order=img_data.get("sort_order", 0),
            )

        # 锁定资产
        from apps.assets.models import UserAsset
        asset = validated_data["asset"]
        asset.quantity -= validated_data["quantity"]
        if asset.quantity == 0:
            asset.status = UserAsset.Status.SELLING
        asset.save()

        logger.info("用户 %s 创建挂单 %s", user.user_id, listing_id)
        return listing


class ListingListSerializer(serializers.ModelSerializer):
    seller_id = serializers.CharField(source="seller.user_id", read_only=True)
    seller_name = serializers.CharField(source="seller.nickname", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_image = serializers.ImageField(source="product.main_image", read_only=True)
    images = ListingImageSerializer(many=True, read_only=True)

    class Meta:
        model = Listing
        fields = [
            "listing_id", "seller_id", "seller_name", "product_id", "product_name",
            "product_image", "price", "quantity", "description", "status", "images", "created_at",
        ]


class ListingDetailSerializer(serializers.ModelSerializer):
    seller_id = serializers.CharField(source="seller.user_id", read_only=True)
    seller_name = serializers.CharField(source="seller.nickname", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_image = serializers.ImageField(source="product.main_image", read_only=True)
    images = ListingImageSerializer(many=True, read_only=True)

    class Meta:
        model = Listing
        fields = [
            "listing_id", "seller_id", "seller_name", "product_id", "product_name",
            "product_image", "asset_id", "price", "quantity", "description", "status", "images",
            "created_at", "updated_at",
        ]


class ListingCancelSerializer(serializers.Serializer):
    def validate(self, attrs):
        listing = self.instance
        if listing.status != Listing.Status.ACTIVE:
            raise serializers.ValidationError("只能取消上架中的挂单")
        return attrs

    def save(self):
        from apps.assets.models import UserAsset

        listing = self.instance
        listing.status = Listing.Status.CANCELLED
        listing.save()

        # 释放资产
        asset = listing.asset
        asset.quantity += listing.quantity
        asset.status = UserAsset.Status.HOLDING
        asset.save()

        logger.info("用户取消挂单 %s", listing.listing_id)
        return listing
