import logging

from rest_framework import serializers

from apps.common.id_generator import generate_exchange_id
from .models import ExchangeMatch, ExchangeRequest, ExchangeStatusLog

logger = logging.getLogger("gugou")


class ExchangeRequestCreateSerializer(serializers.Serializer):
    offered_asset_id = serializers.CharField(max_length=25)
    target_condition = serializers.CharField(max_length=500, required=False, allow_blank=True, default="")
    price_difference_note = serializers.CharField(max_length=500, required=False, allow_blank=True, default="")

    def validate(self, attrs):
        from apps.assets.models import UserAsset

        # 验证资产存在且属于当前用户
        try:
            asset = UserAsset.objects.get(asset_id=attrs["offered_asset_id"])
        except UserAsset.DoesNotExist:
            raise serializers.ValidationError({"offered_asset_id": "资产不存在"})

        user = self.context["request"].user
        if asset.owner != user:
            raise serializers.ValidationError({"offered_asset_id": "只能用自己的资产进行换物"})

        # 验证资产数量足够
        if asset.quantity < 1:
            raise serializers.ValidationError({"offered_asset_id": "资产数量不足"})

        attrs["asset"] = asset
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        asset = validated_data["asset"]

        # 生成换物请求编号
        exchange_id = generate_exchange_id()

        # 创建换物请求
        exchange = ExchangeRequest.objects.create(
            exchange_id=exchange_id,
            owner=user,
            offered_asset=asset,
            target_condition=validated_data.get("target_condition", ""),
            price_difference_note=validated_data.get("price_difference_note", ""),
            status=ExchangeRequest.Status.ACTIVE,
        )

        # 锁定资产
        asset.quantity -= 1
        asset.save()

        # 记录状态变更日志
        ExchangeStatusLog.objects.create(
            log_id=f"LOG{exchange_id}",
            exchange=exchange,
            from_status="",
            to_status=ExchangeRequest.Status.ACTIVE,
            operator=user,
            note="发布换物请求",
        )

        logger.info("用户 %s 发布换物请求 %s", user.user_id, exchange_id)
        return exchange


class ExchangeMatchCreateSerializer(serializers.Serializer):
    applicant_asset_id = serializers.CharField(max_length=25)

    def validate(self, attrs):
        from apps.assets.models import UserAsset

        exchange = self.context["exchange"]
        user = self.context["request"].user

        # 验证不能匹配自己的换物请求
        if exchange.owner == user:
            raise serializers.ValidationError("不能匹配自己的换物请求")

        # 验证换物请求状态
        if exchange.status != ExchangeRequest.Status.ACTIVE:
            raise serializers.ValidationError("该换物请求已不可匹配")

        # 验证资产存在且属于当前用户
        try:
            asset = UserAsset.objects.get(asset_id=attrs["applicant_asset_id"])
        except UserAsset.DoesNotExist:
            raise serializers.ValidationError({"applicant_asset_id": "资产不存在"})

        if asset.owner != user:
            raise serializers.ValidationError({"applicant_asset_id": "只能用自己的资产进行换物"})

        # 验证资产数量足够
        if asset.quantity < 1:
            raise serializers.ValidationError({"applicant_asset_id": "资产数量不足"})

        # 验证是否已经匹配过
        if ExchangeMatch.objects.filter(request=exchange, applicant=user).exists():
            raise serializers.ValidationError("已经提交过匹配申请")

        attrs["asset"] = asset
        return attrs

    def create(self, validated_data):
        exchange = self.context["exchange"]
        user = self.context["request"].user
        asset = validated_data["asset"]

        # 生成匹配编号
        match_id = f"M{generate_exchange_id()[1:]}"

        # 创建匹配记录
        match = ExchangeMatch.objects.create(
            match_id=match_id,
            request=exchange,
            applicant=user,
            applicant_asset=asset,
            status=ExchangeMatch.Status.PENDING,
        )

        logger.info("用户 %s 提交匹配 %s 到换物请求 %s", user.user_id, match_id, exchange.exchange_id)
        return match


class ExchangeMatchAcceptSerializer(serializers.Serializer):
    def validate(self, attrs):
        match = self.instance
        if match.status != ExchangeMatch.Status.PENDING:
            raise serializers.ValidationError("该匹配已处理")
        return attrs

    def save(self):
        match = self.instance
        exchange = match.request

        # 更新匹配状态
        match.status = ExchangeMatch.Status.ACCEPTED
        match.save()

        # 更新换物请求状态
        exchange.status = ExchangeRequest.Status.MATCHED
        exchange.save()

        # 记录状态变更日志
        ExchangeStatusLog.objects.create(
            log_id=f"LOG{exchange.exchange_id}_MATCHED",
            exchange=exchange,
            from_status=ExchangeRequest.Status.ACTIVE,
            to_status=ExchangeRequest.Status.MATCHED,
            operator=exchange.owner,
            note=f"接受匹配 {match.match_id}",
        )

        logger.info("换物请求 %s 匹配成功", exchange.exchange_id)
        return match


class ExchangeMatchRejectSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=200, required=False, allow_blank=True, default="")

    def validate(self, attrs):
        match = self.instance
        if match.status != ExchangeMatch.Status.PENDING:
            raise serializers.ValidationError("该匹配已处理")
        return attrs

    def save(self):
        match = self.instance
        reason = self.validated_data.get("reason", "")

        # 更新匹配状态
        match.status = ExchangeMatch.Status.REJECTED
        match.save()

        logger.info("匹配 %s 已被拒绝", match.match_id)
        return match


class ExchangeCompleteSerializer(serializers.Serializer):
    def validate(self, attrs):
        exchange = self.instance
        if exchange.status != ExchangeRequest.Status.MATCHED:
            raise serializers.ValidationError("换物请求状态不允许完成")
        return attrs

    def save(self):
        from apps.credits.services import create_credit_record

        exchange = self.instance

        # 获取已接受的匹配
        match = exchange.matches.filter(status=ExchangeMatch.Status.ACCEPTED).first()
        if not match:
            raise serializers.ValidationError("没有已接受的匹配")

        # 更新换物请求状态
        exchange.status = ExchangeRequest.Status.COMPLETED
        exchange.save()

        # 交换资产所有权
        owner_asset = exchange.offered_asset
        applicant_asset = match.applicant_asset

        # 更新资产归属
        owner_asset.owner = match.applicant
        owner_asset.quantity += 1
        owner_asset.save()

        applicant_asset.owner = exchange.owner
        applicant_asset.quantity += 1
        applicant_asset.save()

        # 记录状态变更日志
        ExchangeStatusLog.objects.create(
            log_id=f"LOG{exchange.exchange_id}_COMPLETED",
            exchange=exchange,
            from_status=ExchangeRequest.Status.MATCHED,
            to_status=ExchangeRequest.Status.COMPLETED,
            operator=exchange.owner,
            note="换物完成",
        )

        # 双方获得信用
        create_credit_record(
            user=exchange.owner,
            change_value=1,
            reason=f"完成换物 {exchange.exchange_id}",
        )
        create_credit_record(
            user=match.applicant,
            change_value=1,
            reason=f"完成换物 {exchange.exchange_id}",
        )

        logger.info("换物请求 %s 已完成", exchange.exchange_id)
        return exchange


class ExchangeCancelSerializer(serializers.Serializer):
    def validate(self, attrs):
        exchange = self.instance
        if exchange.status not in (ExchangeRequest.Status.ACTIVE, ExchangeRequest.Status.MATCHED):
            raise serializers.ValidationError("当前状态不允许取消")
        return attrs

    def save(self):
        exchange = self.instance
        user = self.context["request"].user

        # 更新换物请求状态
        exchange.status = ExchangeRequest.Status.CANCELLED
        exchange.save()

        # 释放资产
        asset = exchange.offered_asset
        asset.quantity += 1
        asset.save()

        # 如果已匹配，释放对方资产
        match = exchange.matches.filter(status=ExchangeMatch.Status.ACCEPTED).first()
        if match:
            match.applicant_asset.quantity += 1
            match.applicant_asset.save()
            match.status = ExchangeMatch.Status.REJECTED
            match.save()

        # 记录状态变更日志
        ExchangeStatusLog.objects.create(
            log_id=f"LOG{exchange.exchange_id}_CANCELLED",
            exchange=exchange,
            from_status=exchange.status,
            to_status=ExchangeRequest.Status.CANCELLED,
            operator=user,
            note="取消换物请求",
        )

        logger.info("换物请求 %s 已取消", exchange.exchange_id)
        return exchange


class ExchangeRequestListSerializer(serializers.ModelSerializer):
    owner_id = serializers.CharField(source="owner.user_id", read_only=True)
    owner_name = serializers.CharField(source="owner.nickname", read_only=True)
    offered_asset_name = serializers.CharField(source="offered_asset.product.name", read_only=True)

    class Meta:
        model = ExchangeRequest
        fields = [
            "exchange_id", "owner_id", "owner_name", "offered_asset_id",
            "offered_asset_name", "target_condition", "status", "created_at",
        ]


class ExchangeRequestDetailSerializer(serializers.ModelSerializer):
    owner_id = serializers.CharField(source="owner.user_id", read_only=True)
    owner_name = serializers.CharField(source="owner.nickname", read_only=True)
    offered_asset_name = serializers.CharField(source="offered_asset.product.name", read_only=True)
    matches = serializers.SerializerMethodField()
    status_logs = serializers.SerializerMethodField()

    class Meta:
        model = ExchangeRequest
        fields = [
            "exchange_id", "owner_id", "owner_name", "offered_asset_id",
            "offered_asset_name", "target_condition", "price_difference_note",
            "status", "created_at", "updated_at", "matches", "status_logs",
        ]

    def get_matches(self, obj):
        matches = obj.matches.all().order_by("-created_at")
        return ExchangeMatchSerializer(matches, many=True).data

    def get_status_logs(self, obj):
        logs = obj.status_logs.all().order_by("-created_at")
        return ExchangeStatusLogSerializer(logs, many=True).data


class ExchangeMatchSerializer(serializers.ModelSerializer):
    applicant_id = serializers.CharField(source="applicant.user_id", read_only=True)
    applicant_name = serializers.CharField(source="applicant.nickname", read_only=True)
    applicant_asset_name = serializers.CharField(source="applicant_asset.product.name", read_only=True)

    class Meta:
        model = ExchangeMatch
        fields = [
            "match_id", "applicant_id", "applicant_name", "applicant_asset_id",
            "applicant_asset_name", "status", "created_at",
        ]


class ExchangeStatusLogSerializer(serializers.ModelSerializer):
    operator_id = serializers.CharField(source="operator.user_id", read_only=True)
    operator_name = serializers.CharField(source="operator.nickname", read_only=True)

    class Meta:
        model = ExchangeStatusLog
        fields = [
            "log_id", "from_status", "to_status", "operator_id",
            "operator_name", "note", "created_at",
        ]
