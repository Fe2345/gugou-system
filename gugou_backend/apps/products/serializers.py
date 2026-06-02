from rest_framework import serializers

from apps.common.id_generator import generate_product_id
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    """商品输出序列化器，snake_case -> camelCase"""
    id = serializers.CharField(source="product_id", read_only=True)
    ipName = serializers.CharField(source="ip_name", read_only=True)
    characterName = serializers.CharField(source="character_name", read_only=True)
    referencePrice = serializers.DecimalField(source="reference_price", max_digits=10, decimal_places=2, read_only=True)
    mainImage = serializers.ImageField(source="main_image", read_only=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = Product
        fields = ["id", "name", "ipName", "characterName", "category",
                  "referencePrice", "mainImage", "description", "status", "createdAt"]


class ProductCreateSerializer(serializers.Serializer):
    """商品创建序列化器"""
    name = serializers.CharField(max_length=100)
    ipName = serializers.CharField(max_length=50, required=False, default="", allow_blank=True)
    characterName = serializers.CharField(max_length=50, required=False, default="", allow_blank=True)
    category = serializers.CharField(max_length=20)
    referencePrice = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0)
    mainImage = serializers.ImageField(required=False)
    description = serializers.CharField(required=False, default="", allow_blank=True)

    def create(self, validated_data):
        request = self.context.get("request")
        product = Product(
            product_id=generate_product_id(),
            name=validated_data["name"],
            ip_name=validated_data.get("ipName", ""),
            character_name=validated_data.get("characterName", ""),
            category=validated_data["category"],
            reference_price=validated_data.get("referencePrice", 0),
            main_image=validated_data.get("mainImage", ""),
            description=validated_data.get("description", ""),
            status=Product.Status.INACTIVE,
        )
        if request and hasattr(request, "user") and request.user.is_authenticated:
            product.created_by = request.user
        product.save()
        return product


class ProductUpdateSerializer(serializers.Serializer):
    """商品更新序列化器"""
    name = serializers.CharField(max_length=100, required=False)
    ipName = serializers.CharField(max_length=50, required=False, allow_blank=True)
    characterName = serializers.CharField(max_length=50, required=False, allow_blank=True)
    category = serializers.CharField(max_length=20, required=False)
    referencePrice = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    mainImage = serializers.ImageField(required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(choices=Product.Status.choices, required=False)

    def update(self, instance, validated_data):
        if "mainImage" in validated_data and validated_data["mainImage"] is None:
            validated_data.pop("mainImage")
        field_map = {
            "name": "name",
            "ipName": "ip_name",
            "characterName": "character_name",
            "category": "category",
            "referencePrice": "reference_price",
            "mainImage": "main_image",
            "description": "description",
            "status": "status",
        }
        for camel, snake in field_map.items():
            if camel in validated_data:
                setattr(instance, snake, validated_data[camel])
        instance.save()
        return instance


class AdminGoodsSerializer(serializers.ModelSerializer):
    """管理员商品列表序列化器"""
    id = serializers.CharField(source="product_id", read_only=True)
    ipName = serializers.CharField(source="ip_name", read_only=True)
    characterName = serializers.CharField(source="character_name", read_only=True)
    referencePrice = serializers.DecimalField(source="reference_price", max_digits=10, decimal_places=2, read_only=True)
    mainImage = serializers.ImageField(source="main_image", read_only=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    submittedAt = serializers.DateTimeField(source="created_at", read_only=True)
    stock = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Product
        fields = [
            "id", "name", "ipName", "characterName", "category",
            "referencePrice", "mainImage", "description", "status",
            "createdAt", "submittedAt", "stock",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["seller"] = instance.created_by.user_id if instance.created_by else ""
        return data
