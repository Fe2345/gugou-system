from rest_framework import serializers

from .models import Address, Division


class DivisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Division
        fields = ["code", "name", "level"]


class AddressSerializer(serializers.ModelSerializer):
    province = DivisionSerializer(read_only=True)
    city = DivisionSerializer(read_only=True)
    district = DivisionSerializer(read_only=True)

    class Meta:
        model = Address
        fields = [
            "id", "receiver_name", "receiver_phone",
            "province", "city", "district",
            "street", "detail", "is_default",
        ]
        read_only_fields = ["id"]

    def validate_receiver_phone(self, value):
        import re
        if not re.match(r"^1[3-9]\d{9}$", value):
            raise serializers.ValidationError("请输入有效的 11 位手机号")
        return value


class AddressWriteSerializer(serializers.Serializer):
    receiver_name = serializers.CharField(max_length=30)
    receiver_phone = serializers.CharField(max_length=11)
    province_code = serializers.CharField(max_length=6)
    city_code = serializers.CharField(max_length=6)
    district_code = serializers.CharField(max_length=6)
    street = serializers.CharField(max_length=100)
    detail = serializers.CharField(max_length=200)
    is_default = serializers.BooleanField(default=False)

    def validate_receiver_phone(self, value):
        import re
        if not re.match(r"^1[3-9]\d{9}$", value):
            raise serializers.ValidationError("请输入有效的 11 位手机号")
        return value

    def validate(self, attrs):
        codes = [attrs["province_code"], attrs["city_code"], attrs["district_code"]]
        divisions = Division.objects.filter(code__in=codes)
        found = {d.code: d for d in divisions}
        for code in codes:
            if code not in found:
                raise serializers.ValidationError(f"行政区划代码 {code} 不存在")
        return attrs
