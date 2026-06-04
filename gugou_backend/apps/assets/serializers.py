from rest_framework import serializers

from apps.common.id_generator import generate_asset_id
from .models import UserAsset


class AssetSerializer(serializers.ModelSerializer):
    """资产输出序列化器，snake_case -> camelCase"""
    id = serializers.CharField(source="asset_id", read_only=True)
    productId = serializers.CharField(source="product.product_id", read_only=True)
    productName = serializers.CharField(source="product.name", read_only=True)
    ipName = serializers.CharField(source="product.ip_name", read_only=True)
    characterName = serializers.CharField(source="product.character_name", read_only=True)
    category = serializers.CharField(source="product.category", read_only=True)
    mainImage = serializers.ImageField(source="product.main_image", read_only=True)
    acquirePrice = serializers.DecimalField(source="acquire_price", max_digits=10, decimal_places=2, read_only=True)
    currentValue = serializers.DecimalField(source="current_value", max_digits=10, decimal_places=2, read_only=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = UserAsset
        fields = ["id", "productId", "productName", "ipName", "characterName",
                  "category", "mainImage", "quantity", "acquirePrice",
                  "currentValue", "status", "description", "createdAt", "updatedAt"]


class AssetCreateSerializer(serializers.Serializer):
    """资产创建序列化器"""
    productId = serializers.CharField(max_length=25, required=False, default="", allow_blank=True)
    productName = serializers.CharField(max_length=100, required=False, default="")
    ipName = serializers.CharField(max_length=50, required=False, default="", allow_blank=True)
    characterName = serializers.CharField(max_length=50, required=False, default="", allow_blank=True)
    category = serializers.CharField(max_length=20, required=False, default="other", allow_blank=True)
    quantity = serializers.IntegerField(min_value=1, default=1)
    acquirePrice = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = serializers.CharField(required=False, default="", allow_blank=True)

    def validate(self, data):
        # 品类合法性校验
        from apps.products.models import Product
        category = data.get("category", "")
        if category and category not in Product.Category.values:
            raise serializers.ValidationError({"category": f"无效的品类：{category}"})

        # 未选择已有商品时，IP/角色/品类必须填写
        if not data.get("productId"):
            for field, label in [("ipName", "IP名称"), ("characterName", "角色名称"), ("category", "品类")]:
                if not data.get(field, "").strip():
                    raise serializers.ValidationError({field: f"{label}不能为空"})
        return data

    def create(self, validated_data):
        from apps.products.models import Product
        from apps.common.id_generator import generate_product_id

        product_id = validated_data.get("productId")
        if product_id:
            product = Product.objects.get(product_id=product_id)
        else:
            product = Product.objects.create(
                product_id=generate_product_id(),
                name=validated_data.get("productName", "未命名商品"),
                ip_name=validated_data.get("ipName", ""),
                character_name=validated_data.get("characterName", ""),
                category=validated_data.get("category", "other"),
                status="active",
            )

        acquire_price = validated_data.get("acquirePrice", 0)
        current_value = product.reference_price if product.reference_price > 0 else acquire_price

        request = self.context.get("request")
        owner = request.user if request and request.user.is_authenticated else None
        asset = UserAsset(
            asset_id=generate_asset_id(),
            owner=owner,
            product=product,
            quantity=validated_data.get("quantity", 1),
            acquire_price=acquire_price,
            current_value=current_value,
            description=validated_data.get("description", ""),
        )
        asset.save()
        return asset


class AssetUpdateSerializer(serializers.Serializer):
    """资产更新序列化器"""
    quantity = serializers.IntegerField(min_value=1, required=False)
    acquirePrice = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    currentValue = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(choices=UserAsset.Status.choices, required=False)

    def update(self, instance, validated_data):
        field_map = {
            "quantity": "quantity",
            "acquirePrice": "acquire_price",
            "currentValue": "current_value",
            "description": "description",
            "status": "status",
        }
        for camel, snake in field_map.items():
            if camel in validated_data:
                setattr(instance, snake, validated_data[camel])
        instance.save()
        return instance


class AssetOperateSerializer(serializers.Serializer):
    """资产操作序列化器（上架/下架/卖出）"""
    type = serializers.ChoiceField(choices=["list", "delist", "sold"])
    assetId = serializers.CharField(max_length=25)
    targetUserId = serializers.CharField(max_length=25, required=False, allow_blank=True)
    reason = serializers.CharField(max_length=200, required=False, allow_blank=True)

    def validate_assetId(self, value):
        try:
            UserAsset.objects.get(asset_id=value)
        except UserAsset.DoesNotExist:
            raise serializers.ValidationError("资产不存在")
        return value
