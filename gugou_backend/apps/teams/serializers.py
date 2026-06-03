import logging
from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from apps.common.id_generator import generate_team_id
from .models import TeamParticipant, TeamProject

logger = logging.getLogger("gugou")


class TeamProjectCreateSerializer(serializers.Serializer):
    product_id = serializers.CharField(max_length=25)
    target_count = serializers.IntegerField(min_value=2, max_value=100)
    team_price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    deadline_hours = serializers.IntegerField(min_value=1, max_value=72, default=24)

    def validate(self, attrs):
        from apps.products.models import Product
        from apps.credits.services import check_team_permission

        user = self.context["request"].user

        # 检查信用分拼团权限
        allowed, msg = check_team_permission(user)
        if not allowed:
            raise serializers.ValidationError({"credit": msg})

        # 验证商品存在
        try:
            product = Product.objects.get(product_id=attrs["product_id"])
        except Product.DoesNotExist:
            raise serializers.ValidationError({"product_id": "商品不存在"})

        attrs["product"] = product
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        product = validated_data["product"]

        # 生成拼团编号
        team_id = generate_team_id()

        # 计算截止时间
        deadline = timezone.now() + timedelta(hours=validated_data["deadline_hours"])

        # 创建拼团项目
        team = TeamProject.objects.create(
            team_id=team_id,
            product=product,
            creator=user,
            target_count=validated_data["target_count"],
            current_count=1,
            team_price=validated_data["team_price"],
            deadline=deadline,
            status=TeamProject.Status.RECRUITING,
        )

        # 创建者自动参与
        participant_id = f"P{generate_team_id()[1:]}"
        TeamParticipant.objects.create(
            participant_id=participant_id,
            team=team,
            user=user,
            status=TeamParticipant.Status.JOINED,
        )

        logger.info("用户 %s 创建拼团 %s", user.user_id, team_id)
        return team


class TeamProjectJoinSerializer(serializers.Serializer):
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

        # 验证是否已参与
        if TeamParticipant.objects.filter(team=team, user=user).exists():
            raise serializers.ValidationError("已经参与了该拼团")

        return attrs

    def create(self, validated_data):
        team = self.context["team"]
        user = self.context["request"].user

        # 生成参与记录编号
        participant_id = f"P{generate_team_id()[1:]}"

        # 创建参与记录
        participant = TeamParticipant.objects.create(
            participant_id=participant_id,
            team=team,
            user=user,
            status=TeamParticipant.Status.JOINED,
        )

        # 更新当前人数
        team.current_count += 1

        # 检查是否达到目标人数
        if team.current_count >= team.target_count:
            team.status = TeamProject.Status.SUCCESS
            logger.info("拼团 %s 已成功", team.team_id)

            # 拼团成功，所有参与者获得信用分
            from apps.credits.services import create_credit_record, CREDIT_TEAM_SUCCESS
            participants = TeamParticipant.objects.filter(team=team, status=TeamParticipant.Status.JOINED)
            for p in participants:
                create_credit_record(
                    user=p.user,
                    change_value=CREDIT_TEAM_SUCCESS,
                    reason=f"拼团成功 {team.team_id}",
                )

        team.save()

        logger.info("用户 %s 参与拼团 %s", user.user_id, team.team_id)
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

        # 更新所有参与者的状态
        participants = TeamParticipant.objects.filter(team=team, status=TeamParticipant.Status.JOINED)
        for participant in participants:
            participant.status = TeamParticipant.Status.CANCELLED
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
        if user == team.creator:
            raise serializers.ValidationError("团长不能退出拼团，请使用取消拼团功能")

        attrs["participant"] = participant
        return attrs

    def save(self):
        team = self.context["team"]
        participant = self.validated_data["participant"]

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

        # 更新所有参与者的状态
        participants = TeamParticipant.objects.filter(team=team, status=TeamParticipant.Status.JOINED)
        for participant in participants:
            participant.status = TeamParticipant.Status.CANCELLED
            participant.save()

        logger.info("拼团 %s 已失败", team.team_id)
        return team


class TeamProjectListSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_price = serializers.DecimalField(source="product.reference_price", max_digits=10, decimal_places=2, read_only=True)
    creator_id = serializers.CharField(source="creator.user_id", read_only=True)
    creator_name = serializers.CharField(source="creator.nickname", read_only=True)
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = TeamProject
        fields = [
            "team_id", "product_id", "product_name", "product_price",
            "creator_id", "creator_name", "target_count", "current_count",
            "team_price", "deadline", "status", "is_expired", "created_at",
        ]

    def get_is_expired(self, obj):
        return obj.deadline < timezone.now()


class TeamProjectDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_price = serializers.DecimalField(source="product.reference_price", max_digits=10, decimal_places=2, read_only=True)
    creator_id = serializers.CharField(source="creator.user_id", read_only=True)
    creator_name = serializers.CharField(source="creator.nickname", read_only=True)
    participants = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = TeamProject
        fields = [
            "team_id", "product_id", "product_name", "product_price",
            "creator_id", "creator_name", "target_count", "current_count",
            "team_price", "deadline", "status", "is_expired", "created_at",
            "updated_at", "participants",
        ]

    def get_participants(self, obj):
        participants = obj.participants.filter(status=TeamParticipant.Status.JOINED)
        return TeamParticipantSerializer(participants, many=True).data

    def get_is_expired(self, obj):
        return obj.deadline < timezone.now()


class TeamParticipantSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(source="user.user_id", read_only=True)
    user_name = serializers.CharField(source="user.nickname", read_only=True)

    class Meta:
        model = TeamParticipant
        fields = ["participant_id", "user_id", "user_name", "status", "joined_at"]
