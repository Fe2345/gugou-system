import logging

from django.db import models
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.common.permissions import IsAuthenticated, IsAdmin
from apps.common.response import error, flatten_errors, success, paginated
from .models import TeamParticipant, TeamProject
from .serializers import (
    TeamProjectCancelSerializer,
    TeamProjectCreateSerializer,
    TeamProjectDetailSerializer,
    TeamProjectFailSerializer,
    TeamProjectJoinSerializer,
    TeamProjectLeaveSerializer,
    TeamProjectListSerializer,
    TeamParticipantSerializer,
)

logger = logging.getLogger("gugou")


class TeamProjectCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TeamProjectCreateSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors), code=400)
        team = serializer.save()
        data = TeamProjectDetailSerializer(team).data
        return success(data=data, message="拼团创建成功")


class TeamProjectListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))
        keyword = request.query_params.get("keyword", "").strip()
        status_filter = request.query_params.get("status")
        product_id = request.query_params.get("product_id")

        queryset = TeamProject.objects.all()

        # 关键词搜索：编号、商品名称、发起人昵称
        if keyword:
            queryset = queryset.filter(
                Q(team_id__icontains=keyword)
                | Q(product__name__icontains=keyword)
                | Q(creator__nickname__icontains=keyword)
            )

        # 按状态筛选
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # 按商品筛选
        if product_id:
            queryset = queryset.filter(product_id=product_id)

        # 排序
        queryset = queryset.order_by("-created_at")

        from django.core.paginator import Paginator
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        serializer = TeamProjectListSerializer(page_obj, many=True, context={"request": request})
        data = paginated(page_obj, serializer, page_size)

        return success(data=data)


class TeamProjectDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, team_id):
        try:
            team = TeamProject.objects.get(team_id=team_id)
        except TeamProject.DoesNotExist:
            return error(message="拼团不存在", code=404)

        data = TeamProjectDetailSerializer(team).data
        return success(data=data)


class TeamProjectJoinView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, team_id):
        try:
            team = TeamProject.objects.get(team_id=team_id)
        except TeamProject.DoesNotExist:
            return error(message="拼团不存在", code=404)

        serializer = TeamProjectJoinSerializer(data={}, context={"request": request, "team": team})
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors), code=400)
        serializer.save()

        # 重新获取拼团信息
        team.refresh_from_db()
        data = TeamProjectDetailSerializer(team).data
        return success(data=data, message="参与拼团成功")


class TeamProjectCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, team_id):
        try:
            team = TeamProject.objects.get(team_id=team_id)
        except TeamProject.DoesNotExist:
            return error(message="拼团不存在", code=404)

        # 验证权限：只有创建者可以取消
        if request.user.user_id != team.creator_id:
            return error(message="无权操作此拼团", code=403)

        serializer = TeamProjectCancelSerializer(team, data={}, context={"request": request})
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors), code=400)
        serializer.save()
        return success(message="拼团已取消")


class TeamProjectLeaveView(APIView):
    """团员退出拼团"""
    permission_classes = [IsAuthenticated]

    def post(self, request, team_id):
        try:
            team = TeamProject.objects.get(team_id=team_id)
        except TeamProject.DoesNotExist:
            return error(message="拼团不存在", code=404)

        serializer = TeamProjectLeaveSerializer(
            data={},
            context={"request": request, "team": team}
        )
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors), code=400)
        serializer.save()

        # 重新获取拼团信息
        team.refresh_from_db()
        data = TeamProjectDetailSerializer(team).data
        return success(data=data, message="已退出拼团")


class MyTeamProjectListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))

        # 获取用户参与的拼团
        from .models import TeamParticipant
        participant_team_ids = TeamParticipant.objects.filter(
            user=request.user,
            status=TeamParticipant.Status.JOINED,
        ).values_list("team_id", flat=True)

        queryset = TeamProject.objects.filter(
            models.Q(creator=request.user) | models.Q(team_id__in=participant_team_ids)
        ).distinct().order_by("-created_at")

        from django.core.paginator import Paginator
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        serializer = TeamProjectListSerializer(page_obj, many=True)
        data = paginated(page_obj, serializer, page_size)

        return success(data=data)


class TeamProjectCheckFailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, team_id):
        """检查并标记失败的拼团（通常由定时任务调用）"""
        try:
            team = TeamProject.objects.get(team_id=team_id)
        except TeamProject.DoesNotExist:
            return error(message="拼团不存在", code=404)

        # 验证拼团是否已过期且未成功
        from django.utils import timezone
        if team.status != TeamProject.Status.RECRUITING:
            return error(message="拼团状态不允许标记失败", code=400)

        if team.deadline >= timezone.now():
            return error(message="拼团尚未过期", code=400)

        serializer = TeamProjectFailSerializer(team, data={})
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors), code=400)
        serializer.save()
        return success(message="拼团已标记为失败")


# ==================== 管理员端拼团管理 ====================


class AdminTeamListView(APIView):
    """管理员查看拼团列表，支持搜索、状态筛选、时间筛选。"""
    permission_classes = [IsAdmin]

    def get(self, request):
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))
        keyword = request.query_params.get("keyword", "").strip()
        status_filter = request.query_params.get("status", "").strip()
        start_date = request.query_params.get("start_date", "").strip()
        end_date = request.query_params.get("end_date", "").strip()

        queryset = TeamProject.objects.select_related(
            "product", "creator"
        ).all()

        # 关键词搜索：编号、商品名称、发起用户昵称/手机号
        if keyword:
            queryset = queryset.filter(
                Q(team_id__icontains=keyword)
                | Q(product__name__icontains=keyword)
                | Q(creator__nickname__icontains=keyword)
                | Q(creator__phone__icontains=keyword)
            )

        # 状态筛选
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # 时间范围筛选
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        queryset = queryset.order_by("-created_at")

        from django.core.paginator import Paginator
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        serializer = TeamProjectListSerializer(page_obj, many=True)
        data = paginated(page_obj, serializer, page_size)

        return success(data=data)


class AdminTeamDetailView(APIView):
    """管理员查看拼团详情（含参与记录）。"""
    permission_classes = [IsAdmin]

    def get(self, request, team_id):
        try:
            team = TeamProject.objects.select_related(
                "product", "creator"
            ).get(team_id=team_id)
        except TeamProject.DoesNotExist:
            return error(message="拼团不存在", code=404)

        data = TeamProjectDetailSerializer(team).data
        return success(data=data)


class AdminTeamParticipantsView(APIView):
    """管理员查看拼团参与记录列表。"""
    permission_classes = [IsAdmin]

    def get(self, request, team_id):
        try:
            team = TeamProject.objects.get(team_id=team_id)
        except TeamProject.DoesNotExist:
            return error(message="拼团不存在", code=404)

        participants = TeamParticipant.objects.filter(team=team).select_related("user").order_by("-joined_at")
        serializer = TeamParticipantSerializer(participants, many=True)
        return success(data=serializer.data)


class AdminTeamCancelView(APIView):
    """管理员取消拼团，更新所有参与者状态。"""
    permission_classes = [IsAdmin]

    def post(self, request, team_id):
        try:
            team = TeamProject.objects.get(team_id=team_id)
        except TeamProject.DoesNotExist:
            return error(message="拼团不存在", code=404)

        if team.status != TeamProject.Status.RECRUITING:
            return error(message="只能取消招募中的拼团", code=400)

        reason = request.data.get("reason", "管理员取消")

        # 更新拼团状态
        team.status = TeamProject.Status.CANCELLED
        team.save()

        # 更新所有参与者状态
        participants = TeamParticipant.objects.filter(team=team, status=TeamParticipant.Status.JOINED)
        for participant in participants:
            participant.status = TeamParticipant.Status.CANCELLED
            participant.save()

        # 记录管理员操作日志
        from apps.common.id_generator import generate_op_log_id
        from apps.operations.models import AdminOperationLog
        AdminOperationLog.objects.create(
            op_log_id=generate_op_log_id(),
            admin=request.user,
            module="拼团管理",
            action="取消拼团",
            target_id=team_id,
            detail=f"管理员取消拼团 {team_id}，原因：{reason}",
        )

        logger.info("管理员 %s 取消拼团 %s", request.user.user_id, team_id)
        return success(message="拼团已取消")


class AdminTeamFailView(APIView):
    """管理员标记拼团为失败（适用于过期未满的拼团）。"""
    permission_classes = [IsAdmin]

    def post(self, request, team_id):
        try:
            team = TeamProject.objects.get(team_id=team_id)
        except TeamProject.DoesNotExist:
            return error(message="拼团不存在", code=404)

        if team.status != TeamProject.Status.RECRUITING:
            return error(message="当前状态不允许标记失败", code=400)

        # 更新拼团状态
        team.status = TeamProject.Status.FAILED
        team.save()

        # 更新所有参与者状态
        participants = TeamParticipant.objects.filter(team=team, status=TeamParticipant.Status.JOINED)
        for participant in participants:
            participant.status = TeamParticipant.Status.CANCELLED
            participant.save()

        # 记录管理员操作日志
        from apps.common.id_generator import generate_op_log_id
        from apps.operations.models import AdminOperationLog
        AdminOperationLog.objects.create(
            op_log_id=generate_op_log_id(),
            admin=request.user,
            module="拼团管理",
            action="标记失败",
            target_id=team_id,
            detail=f"管理员标记拼团 {team_id} 为失败",
        )

        logger.info("管理员 %s 标记拼团 %s 为失败", request.user.user_id, team_id)
        return success(message="拼团已标记为失败")


class AdminTeamSuccessView(APIView):
    """管理员手动标记拼团为成功（适用于人数已满但状态未更新的情况）。"""
    permission_classes = [IsAdmin]

    def post(self, request, team_id):
        try:
            team = TeamProject.objects.get(team_id=team_id)
        except TeamProject.DoesNotExist:
            return error(message="拼团不存在", code=404)

        if team.status != TeamProject.Status.RECRUITING:
            return error(message="当前状态不允许标记成功", code=400)

        if team.current_count < team.target_count:
            return error(message=f"当前人数 {team.current_count} 未达到目标 {team.target_count}", code=400)

        # 更新拼团状态
        team.status = TeamProject.Status.SUCCESS
        team.save()

        # 所有参与者获得信用分
        from apps.credits.services import create_credit_record, CREDIT_TEAM_SUCCESS
        participants = TeamParticipant.objects.filter(team=team, status=TeamParticipant.Status.JOINED)
        for p in participants:
            create_credit_record(
                user=p.user,
                change_value=CREDIT_TEAM_SUCCESS,
                reason=f"拼团成功 {team_id}",
            )

        # 记录管理员操作日志
        from apps.common.id_generator import generate_op_log_id
        from apps.operations.models import AdminOperationLog
        AdminOperationLog.objects.create(
            op_log_id=generate_op_log_id(),
            admin=request.user,
            module="拼团管理",
            action="确认成功",
            target_id=team_id,
            detail=f"管理员确认拼团 {team_id} 成功",
        )

        logger.info("管理员 %s 确认拼团 %s 成功", request.user.user_id, team_id)
        return success(message="拼团已标记为成功")
