from rest_framework import serializers

from .models import CreditRecord


class CreditRecordListSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(source="user.user_id", read_only=True)
    user_name = serializers.CharField(source="user.nickname", read_only=True)
    related_order_id = serializers.CharField(source="related_order.order_id", read_only=True, default=None)

    class Meta:
        model = CreditRecord
        fields = [
            "credit_record_id", "user_id", "user_name", "change_value",
            "reason", "related_order_id", "created_at",
        ]


class CreditSummarySerializer(serializers.Serializer):
    total_credit = serializers.IntegerField()
    positive_count = serializers.IntegerField()
    negative_count = serializers.IntegerField()
    recent_records = CreditRecordListSerializer(many=True)
