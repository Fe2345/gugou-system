import logging
from datetime import timedelta

from django.utils import timezone
from decimal import Decimal

from rest_framework import serializers

from apps.common.id_generator import generate_team_id, generate_team_item_id
from .models import TeamItem, TeamParticipant, TeamProject

logger = logging.getLogger("gugou")


class TeamItemSerializer(serializers.ModelSerializer):
    """小商品选项序列化器（只读展示）"""
    is_selected = serializers.SerializerMethodField()
    selected_user_name = serializers.SerializerMethodField()

    class Meta:
        model = TeamItem
        fields = ["item_id", "name", "is_selected", "selected_user_name", "selected_at", "sort_order"]

    def get_is_selected(self, obj):
        return obj.selected_by_id is not None

    def get_selected_user_name(self, obj):
        if obj.selected_by:
            try:
                return obj.selected_by.nickname
            except Exception:
                return "未知用户"
        return None


class TeamProjectCreateSerializer(serializers.Serializer):
    product_name = serializers.CharField(max_length=100)
    team_price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("0.01"))
    deadline_hours = serializers.IntegerField(min_value=1, max_value=72, default=24)
    items = serializers.ListField(
        child=serializers.CharField(max_length=100),
        min_length=2,
        max_length=50,
    )

    def validate(self, attrs):
        from apps.credits.services import check_team_permission

        user = self.context["request"].user

        # 检查信用分拼团权限
        allowed, msg = check_team_permission(user)
        if not allowed:
            raise serializers.ValidationError({"credit": msg})

        # 验证小商品选项不能重复
        items = attrs["items"]
        cleaned = [name.strip() for name in items if name.strip()]
        if len(cleaned) < 2:
            raise serializers.ValidationError({"items": "至少需要 2 个小商品选项"})
        if len(cleaned) != len(set(cleaned)):
            raise serializers.ValidationError({"items": "小商品选项名称不能重复"})
        attrs["items"] = cleaned

        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        items_data = validated_data.pop("items")

        # 生成拼团编号
        team_id = generate_team_id()

        # 计算截止时间
        deadline = timezone.now() + timedelta(hours=validated_data["deadline_hours"])

        # 目标人数 = 小商品数量（每个小商品对应一个人）
        target_count = len(items_data)

        # 创建拼团项目（不再关联商品库）
        team = TeamProject.objects.create(
            team_id=team_id,
            product=None,
            product_name=validated_data["product_name"],
            creator=user,
            target_count=target_count,
            current_count=1,
            team_price=validated_data["team_price"],
            deadline=deadline,
            status=TeamProject.Status.RECRUITING,
        )

        # 批量创建小商品选项
        team_items = []
        for idx, name in enumerate(items_data):
            team_items.append(TeamItem(
                item_id=generate_team_item_id(),
                team=team,
                name=name,
                sort_order=idx,
            ))
        TeamItem.objects.bulk_create(team_items)

        # 创建者自动参与（不选择小商品）
        participant_id = f"P{generate_team_id()[1:]}"
        TeamParticipant.objects.create(
            participant_id=participant_id,
            team=team,
            user=user,
            status=TeamParticipant.Status.JOINED,
        )

        logger.info("用户 %s 创建拼团 %s，商品：%s，共 %d 个小商品选项",
                     user.user_id, team_id, validated_data["product_name"], len(items_data))
        return team


class TeamProjectJoinSerializer(serializers.Serializer):
    item_id = serializers.CharField(max_length=30)
    address_id = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, attrs):
        from apps.credits.services import check_team_permission

        team = self.context["team"]
        user = self.context["request"].user

        # 检查信用分拼团权限
        allowed, msg = check_team_permission(user)
        if not allowed:
            raise serializers.ValidationError({"credit": msg})

        # 验证拼团状态
        if team.status != TeamProject.Status.RECRUITING:
            raise serializers.ValidationError("该拼团已不可参与")

        # 验证是否已满
        if team.current_count >= team.target_count:
            raise serializers.ValidationError("该拼团已满")

        # 验证是否已过期
        if team.deadline < timezone.now():
            raise serializers.ValidationError("该拼团已过期")

        # 验证是否已参与（只检查当前参与中的记录）
        participant = TeamParticipant.objects.filter(team=team, user=user).first()
        if participant:
            if participant.status == TeamParticipant.Status.JOINED:
                if participant.selected_item_id is None:
                    # 发起者创建时未选小商品，允许在此选择
                    attrs["creator_first_select"] = participant
                else:
                    raise serializers.ValidationError("您已经参加了该拼团，不能重复参加")
            elif participant.status == TeamParticipant.Status.CANCELLED:
                # 已退出的用户允许重新参加
                attrs["rejoin_participant"] = participant
            else:
                raise serializers.ValidationError("您的参与状态异常，无法参加")

        # 验证小商品选项
        try:
            item = TeamItem.objects.get(item_id=attrs["item_id"], team=team)
        except TeamItem.DoesNotExist:
            raise serializers.ValidationError({"item_id": "小商品选项不存在"})

        if item.selected_by_id is not None:
            raise serializers.ValidationError({"item_id": "该小商品已被他人选择，请选择其他选项"})

        attrs["item"] = item

        # 验证收货地址（可选）
        address_id = attrs.get("address_id")
        if address_id:
            from apps.addresses.models import Address
            try:
                address = Address.objects.select_related("province", "city", "district").get(
                    id=address_id, user=user
                )
            except Address.DoesNotExist:
                raise serializers.ValidationError({"address_id": "收货地址不存在"})
            attrs["address"] = address

        return attrs

    def create(self, validated_data):
        from django.db import transaction as db_transaction

        team = self.context["team"]
        user = self.context["request"].user
        item = validated_data["item"]
        address = validated_data.get("address")

        with db_transaction.atomic():
            # 检查是否是重新加入或发起者首次选择小商品
            rejoin_participant = validated_data.pop("rejoin_participant", None)
            creator_first_select = validated_data.pop("creator_first_select", None)
            existing_participant = rejoin_participant or creator_first_select

            if existing_participant:
                existing_participant.status = TeamParticipant.Status.JOINED
                existing_participant.selected_item = item
                existing_participant.save()
                participant = existing_participant
                if rejoin_participant:
                    logger.info("用户 %s 重新加入拼团 %s", user.user_id, team.team_id)
                else:
                    logger.info("发起者 %s 选择小商品 %s（拼团 %s）", user.user_id, item.name, team.team_id)
            else:
                participant_id = f"P{generate_team_id()[1:]}"
                participant = TeamParticipant.objects.create(
                    participant_id=participant_id,
                    team=team,
                    user=user,
                    status=TeamParticipant.Status.JOINED,
                    selected_item=item,
                )

            # 锁定小商品选项
            item.selected_by = user
            item.selected_at = timezone.now()
            item.save()

            # 更新当前人数（发起者首次选择小商品时不增加，因为创建时已计为1人）
            if not creator_first_select:
                team.current_count += 1

            # 检查是否达到目标人数
            if team.current_count >= team.target_count:
                team.status = TeamProject.Status.SUCCESS
                logger.info("拼团 %s 已成功", team.team_id)

                # 拼团成功，为每个参与者创建待付款订单
                from apps.orders.models import Order, OrderStatusLog
                from apps.common.id_generator import generate_order_id

                participants = TeamParticipant.objects.filter(team=team, status=TeamParticipant.Status.JOINED)
                for p in participants:
                    order_id = generate_order_id()
                    order_kwargs = dict(
                        order_id=order_id,
                        buyer=p.user,
                        seller=team.creator,
                        listing=None,
                        team=team,
                        product=team.product,
                        quantity=1,
                        amount=team.team_price,
                        status=Order.Status.PENDING_PAYMENT,
                    )
                    # 如果是当前加入的用户且提供了地址，绑定到订单
                    if p.user == user and address:
                        order_kwargs.update(
                            shipping_address=address,
                            receiver_name=address.receiver_name,
                            receiver_phone=address.receiver_phone,
                            shipping_address_text=(
                                f"{address.province.name}{address.city.name}{address.district.name}"
                                f"{address.street}{address.detail}"
                            ),
                        )
                    order = Order.objects.create(**order_kwargs)
                    OrderStatusLog.objects.create(
                        log_id=f"L{order_id}",
                        order=order,
                        from_status="",
                        to_status=Order.Status.PENDING_PAYMENT,
                        operator=p.user,
                        note=f"拼团 {team.team_id} 成功，自动生成订单",
                    )
                    logger.info("为用户 %s 创建拼团订单 %s", p.user.user_id, order_id)

                # 所有参与者获得信用分
                from apps.credits.services import create_credit_record, CREDIT_TEAM_SUCCESS
                for p in participants:
                    create_credit_record(
                        user=p.user,
                        change_value=CREDIT_TEAM_SUCCESS,
                        reason=f"拼团成功 {team.team_id}",
                    )

            team.save()

        logger.info("用户 %s 参与拼团 %s，选择小商品：%s", user.user_id, team.team_id, item.name)
        return participant


class TeamProjectCancelSerializer(serializers.Serializer):
    def validate(self, attrs):
        team = self.instance
        if team.status != TeamProject.Status.RECRUITING:
            raise serializers.ValidationError("只能取消招募中的拼团")
        return attrs

    def save(self):
        from apps.credits.services import create_credit_record, CREDIT_TEAM_EXIT_AFTER_SUCCESS

        team = self.instance
        user = self.context["request"].user

        # 更新拼团状态
        team.status = TeamProject.Status.CANCELLED
        team.save()

        # 更新所有参与者的状态，释放小商品选项
        participants = TeamParticipant.objects.filter(team=team, status=TeamParticipant.Status.JOINED)
        for participant in participants:
            participant.status = TeamParticipant.Status.CANCELLED
            # 释放小商品选项
            if participant.selected_item:
                participant.selected_item.selected_by = None
                participant.selected_item.selected_at = None
                participant.selected_item.save()
                participant.selected_item = None
            participant.save()

        # 创建者取消拼团，扣除信用分
        create_credit_record(
            user=user,
            change_value=CREDIT_TEAM_EXIT_AFTER_SUCCESS,
            reason=f"取消拼团 {team.team_id}",
        )

        logger.info("拼团 %s 已取消", team.team_id)
        return team


class TeamProjectLeaveSerializer(serializers.Serializer):
    """团员退出拼团序列化器"""

    def validate(self, attrs):
        team = self.context["team"]
        user = self.context["request"].user

        # 验证拼团状态
        if team.status != TeamProject.Status.RECRUITING:
            raise serializers.ValidationError("只能退出招募中的拼团")

        # 验证是否是参与者
        try:
            participant = TeamParticipant.objects.get(
                team=team, user=user, status=TeamParticipant.Status.JOINED
            )
        except TeamParticipant.DoesNotExist:
            raise serializers.ValidationError("您尚未参与此拼团")

        # 团长不能用此接口退出，需要用取消接口
        if user.user_id == team.creator_id:
            raise serializers.ValidationError("团长不能退出拼团，请使用取消拼团功能")

        attrs["participant"] = participant
        return attrs

    def save(self):
        team = self.context["team"]
        participant = self.validated_data["participant"]

        # 释放小商品选项
        if participant.selected_item:
            participant.selected_item.selected_by = None
            participant.selected_item.selected_at = None
            participant.selected_item.save()
            participant.selected_item = None

        # 更新参与者状态
        participant.status = TeamParticipant.Status.CANCELLED
        participant.save()

        # 更新当前人数
        team.current_count = max(0, team.current_count - 1)
        team.save()

        logger.info("用户 %s 退出拼团 %s", participant.user.user_id, team.team_id)
        return team


class TeamProjectFailSerializer(serializers.Serializer):
    def validate(self, attrs):
        team = self.instance
        if team.status != TeamProject.Status.RECRUITING:
            raise serializers.ValidationError("当前状态不允许标记失败")
        return attrs

    def save(self):
        team = self.instance

        # 更新拼团状态
        team.status = TeamProject.Status.FAILED
        team.save()

        # 更新所有参与者的状态，释放小商品选项
        participants = TeamParticipant.objects.filter(team=team, status=TeamParticipant.Status.JOINED)
        for participant in participants:
            participant.status = TeamParticipant.Status.CANCELLED
            # 释放小商品选项
            if participant.selected_item:
                participant.selected_item.selected_by = None
                participant.selected_item.selected_at = None
                participant.selected_item.save()
                participant.selected_item = None
            participant.save()

        logger.info("拼团 %s 已失败", team.team_id)
        return team


class TeamProjectListSerializer(serializers.ModelSerializer):
    product_name_display = serializers.SerializerMethodField()
    product_price = serializers.SerializerMethodField()
    creator_id = serializers.CharField(read_only=True)
    creator_name = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    current_user_joined = serializers.SerializerMethodField()
    items_count = serializers.SerializerMethodField()
    items_selected_count = serializers.SerializerMethodField()

    class Meta:
        model = TeamProject
        fields = [
            "team_id", "product_name", "product_name_display", "product_price",
            "creator_id", "creator_name", "target_count", "current_count",
            "team_price", "deadline", "status", "is_expired", "created_at",
            "current_user_joined", "items_count", "items_selected_count",
        ]

    def get_product_name_display(self, obj):
        """优先展示自定义名称"""
        return obj.product_name

    def get_product_price(self, obj):
        if obj.product:
            return obj.product.reference_price
        return None

    def get_creator_name(self, obj):
        try:
            return obj.creator.nickname
        except Exception:
            return "未知用户"

    def get_is_expired(self, obj):
        return obj.deadline < timezone.now()

    def get_current_user_joined(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.participants.filter(
            user=request.user,
            status=TeamParticipant.Status.JOINED,
        ).exists()

    def get_items_count(self, obj):
        return obj.items.count()

    def get_items_selected_count(self, obj):
        return obj.items.filter(selected_by__isnull=False).count()


class TeamProjectDetailSerializer(serializers.ModelSerializer):
    product_name_display = serializers.SerializerMethodField()
    product_price = serializers.SerializerMethodField()
    creator_id = serializers.CharField(read_only=True)
    creator_name = serializers.SerializerMethodField()
    participants = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = TeamProject
        fields = [
            "team_id", "product_name", "product_name_display", "product_price",
            "creator_id", "creator_name", "target_count", "current_count",
            "team_price", "deadline", "status", "is_expired", "created_at",
            "updated_at", "participants", "items",
        ]

    def get_product_name_display(self, obj):
        return obj.product_name

    def get_product_price(self, obj):
        if obj.product:
            return obj.product.reference_price
        return None

    def get_creator_name(self, obj):
        try:
            return obj.creator.nickname
        except Exception:
            return "未知用户"

    def get_participants(self, obj):
        participants = obj.participants.filter(status=TeamParticipant.Status.JOINED)
        return TeamParticipantSerializer(participants, many=True).data

    def get_items(self, obj):
        items = obj.items.all()
        return TeamItemSerializer(items, many=True).data

    def get_is_expired(self, obj):
        return obj.deadline < timezone.now()


class TeamParticipantSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(source="user.user_id", read_only=True)
    user_name = serializers.CharField(source="user.nickname", read_only=True)
    selected_item_name = serializers.SerializerMethodField()
    selected_item_id = serializers.SerializerMethodField()

    class Meta:
        model = TeamParticipant
        fields = ["participant_id", "user_id", "user_name", "status", "joined_at",
                  "selected_item_id", "selected_item_name"]

    def get_selected_item_name(self, obj):
        if obj.selected_item:
            return obj.selected_item.name
        return None

    def get_selected_item_id(self, obj):
        if obj.selected_item:
            return obj.selected_item.item_id
        return None
