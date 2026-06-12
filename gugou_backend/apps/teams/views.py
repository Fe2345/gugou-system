import logging

from django.db import models
from django.db.models import Count, Q
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
                | Q(product_name__icontains=keyword)
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

        # 各状态计数（基于当前筛选条件）
        status_counts = {}
        for status_val, _ in TeamProject.Status.choices:
            status_counts[status_val] = queryset.filter(status=status_val).count()
        data["status_counts"] = status_counts

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

        serializer = TeamProjectJoinSerializer(data=request.data, context={"request": request, "team": team})
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
        keyword = request.query_params.get("keyword", "").strip()

        # 获取用户参与的拼团
        from .models import TeamParticipant
        participant_team_ids = TeamParticipant.objects.filter(
            user=request.user,
            status=TeamParticipant.Status.JOINED,
        ).values_list("team_id", flat=True)

        queryset = TeamProject.objects.filter(
            models.Q(creator=request.user) | models.Q(team_id__in=participant_team_ids)
        ).distinct().order_by("-created_at")

        # 关键词搜索
        if keyword:
            queryset = queryset.filter(
                Q(team_id__icontains=keyword)
                | Q(product_name__icontains=keyword)
                | Q(creator__nickname__icontains=keyword)
            )

        from django.core.paginator import Paginator
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        serializer = TeamProjectListSerializer(page_obj, many=True)
        data = paginated(page_obj, serializer, page_size)

        # 各状态计数
        status_counts = {}
        for status_val, _ in TeamProject.Status.choices:
            status_counts[status_val] = queryset.filter(status=status_val).count()
        data["status_counts"] = status_counts

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


# ==================== 拼团订单相关接口 ====================


class TeamOrderDetailView(APIView):
    """获取当前用户在指定拼团中的订单"""
    permission_classes = [IsAuthenticated]

    def get(self, request, team_id):
        try:
            team = TeamProject.objects.get(team_id=team_id)
        except TeamProject.DoesNotExist:
            return error(message="拼团不存在", code=404)

        from apps.orders.models import Order
        from apps.orders.serializers import OrderDetailSerializer

        try:
            order = Order.objects.get(team=team, buyer=request.user)
        except Order.DoesNotExist:
            return error(message="您在此拼团中没有订单", code=404)

        data = OrderDetailSerializer(order).data
        return success(data=data)


class TeamOrderPayView(APIView):
    """拼团订单支付"""
    permission_classes = [IsAuthenticated]

    def post(self, request, team_id):
        try:
            team = TeamProject.objects.get(team_id=team_id)
        except TeamProject.DoesNotExist:
            return error(message="拼团不存在", code=404)

        from apps.orders.models import Order, PaymentRecord, OrderStatusLog
        from apps.common.id_generator import generate_payment_id, generate_order_id

        try:
            order = Order.objects.get(team=team, buyer=request.user, status=Order.Status.PENDING_PAYMENT)
        except Order.DoesNotExist:
            return error(message="没有待支付的拼团订单", code=400)

        pay_method = request.data.get("pay_method", "simulated")
        address_id = request.data.get("address_id")

        if not address_id:
            return error(message="请选择收货地址", code=400)

        from apps.addresses.models import Address
        try:
            address = Address.objects.select_related("province", "city", "district").get(
                id=address_id, user=request.user
            )
        except Address.DoesNotExist:
            return error(message="收货地址不存在", code=400)

        from django.db import transaction
        from django.utils import timezone

        with transaction.atomic():
            # 创建支付记录
            payment_id = generate_payment_id(request.user.user_id)
            payment = PaymentRecord.objects.create(
                payment_id=payment_id,
                order=order,
                payer=request.user,
                amount=order.amount,
                pay_method=pay_method,
                status=PaymentRecord.Status.SUCCESS,
            )

            # 更新订单状态
            old_status = order.status
            order.status = Order.Status.RECEIVING
            order.paid_at = timezone.now()
            order.shipping_address = address
            order.receiver_name = address.receiver_name
            order.receiver_phone = address.receiver_phone
            order.shipping_address_text = (
                f"{address.province.name}{address.city.name}{address.district.name}"
                f"{address.street}{address.detail}"
            )
            order.save()

            OrderStatusLog.objects.create(
                log_id=f"L{order.order_id}P01",
                order=order,
                from_status=old_status,
                to_status=Order.Status.RECEIVING,
                operator=request.user,
                note="拼团订单支付成功",
            )

        logger.info("用户 %s 支付拼团订单 %s", request.user.user_id, order.order_id)
        return success(message="支付成功")


class TeamOrderConfirmView(APIView):
    """拼团订单确认收货"""
    permission_classes = [IsAuthenticated]

    def post(self, request, team_id):
        try:
            team = TeamProject.objects.get(team_id=team_id)
        except TeamProject.DoesNotExist:
            return error(message="拼团不存在", code=404)

        from apps.orders.models import Order
        from apps.orders.serializers import OrderCompleteSerializer

        try:
            order = Order.objects.get(team=team, buyer=request.user, status=Order.Status.RECEIVING)
        except Order.DoesNotExist:
            return error(message="没有待确认收货的拼团订单", code=400)

        serializer = OrderCompleteSerializer(order, data={})
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors), code=400)

        try:
            serializer.save()
        except Exception as e:
            logger.exception("拼团订单确认收货失败: %s", str(e))
            return error(message=f"操作失败: {str(e)}", code=500)

        return success(message="确认收货成功")


class TeamOrderReturnView(APIView):
    """拼团订单退货"""
    permission_classes = [IsAuthenticated]

    def post(self, request, team_id):
        try:
            team = TeamProject.objects.get(team_id=team_id)
        except TeamProject.DoesNotExist:
            return error(message="拼团不存在", code=404)

        from apps.orders.models import Order
        from apps.orders.serializers import OrderReturnSerializer

        try:
            order = Order.objects.get(team=team, buyer=request.user, status=Order.Status.RECEIVING)
        except Order.DoesNotExist:
            return error(message="没有可退货的拼团订单", code=400)

        serializer = OrderReturnSerializer(order, data=request.data, context={"request": request})
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors), code=400)

        try:
            serializer.save()
        except Exception as e:
            logger.exception("拼团订单退货失败: %s", str(e))
            return error(message=f"操作失败: {str(e)}", code=500)

        return success(message="退货成功")


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
                | Q(product_name__icontains=keyword)
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

        # 各状态计数
        status_counts = {}
        for status_val, _ in TeamProject.Status.choices:
            status_counts[status_val] = queryset.filter(status=status_val).count()
        data["status_counts"] = status_counts

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

        # 更新所有参与者状态，释放小商品选项
        participants = TeamParticipant.objects.filter(team=team, status=TeamParticipant.Status.JOINED)
        for participant in participants:
            participant.status = TeamParticipant.Status.CANCELLED
            if participant.selected_item:
                participant.selected_item.selected_by = None
                participant.selected_item.selected_at = None
                participant.selected_item.save()
                participant.selected_item = None
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

        # 更新所有参与者状态，释放小商品选项
        participants = TeamParticipant.objects.filter(team=team, status=TeamParticipant.Status.JOINED)
        for participant in participants:
            participant.status = TeamParticipant.Status.CANCELLED
            if participant.selected_item:
                participant.selected_item.selected_by = None
                participant.selected_item.selected_at = None
                participant.selected_item.save()
                participant.selected_item = None
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

        # 为每个参与者创建待付款订单
        from django.db import transaction
        from apps.orders.models import Order, OrderStatusLog
        from apps.common.id_generator import generate_order_id

        with transaction.atomic():
            participants = TeamParticipant.objects.filter(team=team, status=TeamParticipant.Status.JOINED)
            for p in participants:
                order_id = generate_order_id()
                order = Order.objects.create(
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
                OrderStatusLog.objects.create(
                    log_id=f"L{order_id}",
                    order=order,
                    from_status="",
                    to_status=Order.Status.PENDING_PAYMENT,
                    operator=p.user,
                    note=f"拼团 {team_id} 成功，管理员确认后自动生成订单",
                )
                logger.info("为用户 %s 创建拼团订单 %s", p.user.user_id, order_id)

            # 所有参与者获得信用分
            from apps.credits.services import create_credit_record, CREDIT_TEAM_SUCCESS
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
