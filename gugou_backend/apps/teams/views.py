import logging

from django.db import models
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.common.permissions import IsAuthenticated
from apps.common.response import error, flatten_errors, success, paginated
from .models import TeamProject
from .serializers import (
    TeamProjectCancelSerializer,
    TeamProjectCreateSerializer,
    TeamProjectDetailSerializer,
    TeamProjectFailSerializer,
    TeamProjectJoinSerializer,
    TeamProjectListSerializer,
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
        status_filter = request.query_params.get("status")
        product_id = request.query_params.get("product_id")

        queryset = TeamProject.objects.all()

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

        serializer = TeamProjectListSerializer(page_obj, many=True)
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
        if request.user != team.creator:
            return error(message="无权操作此拼团", code=403)

        serializer = TeamProjectCancelSerializer(team, data={}, context={"request": request})
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors), code=400)
        serializer.save()
        return success(message="拼团已取消")


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
