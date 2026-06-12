import logging

from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.common.permissions import IsAuthenticated, IsAdmin
from apps.common.response import error, flatten_errors, success, paginated
from .models import ExchangeMatch, ExchangeRequest, ExchangeStatusLog
from .serializers import (
    ExchangeCancelSerializer,
    ExchangeCompleteSerializer,
    ExchangeMatchAcceptSerializer,
    ExchangeMatchCreateSerializer,
    ExchangeMatchRejectSerializer,
    ExchangeRequestCreateSerializer,
    ExchangeRequestDetailSerializer,
    ExchangeRequestListSerializer,
)

logger = logging.getLogger("gugou")


class ExchangeRequestCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ExchangeRequestCreateSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors), code=400)
        exchange = serializer.save()
        data = ExchangeRequestDetailSerializer(exchange).data
        return success(data=data, message="换物请求发布成功")


class ExchangeRequestListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))
        keyword = request.query_params.get("keyword", "").strip()
        status_filter = request.query_params.get("status", "").strip()

        queryset = ExchangeRequest.objects.select_related(
            "owner", "offered_asset__product"
        ).all()

        # 关键词搜索：编号、发起用户昵称/手机号、换出资产商品名
        if keyword:
            queryset = queryset.filter(
                Q(exchange_id__icontains=keyword)
                | Q(owner__nickname__icontains=keyword)
                | Q(owner__phone__icontains=keyword)
                | Q(offered_asset__product__name__icontains=keyword)
            )

        # 状态筛选：不传则显示全部状态
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        queryset = queryset.order_by("-created_at")

        from django.core.paginator import Paginator
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        serializer = ExchangeRequestListSerializer(page_obj, many=True)
        data = paginated(page_obj, serializer, page_size)

        return success(data=data)


class ExchangeRequestDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, exchange_id):
        try:
            exchange = ExchangeRequest.objects.get(exchange_id=exchange_id)
        except ExchangeRequest.DoesNotExist:
            return error(message="换物请求不存在", code=404)

        data = ExchangeRequestDetailSerializer(exchange).data
        return success(data=data)


class MyExchangeRequestListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))

        queryset = ExchangeRequest.objects.filter(owner=request.user).order_by("-created_at")

        from django.core.paginator import Paginator
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        serializer = ExchangeRequestListSerializer(page_obj, many=True)
        data = paginated(page_obj, serializer, page_size)

        return success(data=data)


class ExchangeMatchCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, exchange_id):
        try:
            exchange = ExchangeRequest.objects.get(exchange_id=exchange_id)
        except ExchangeRequest.DoesNotExist:
            return error(message="换物请求不存在", code=404)

        serializer = ExchangeMatchCreateSerializer(
            data=request.data,
            context={"request": request, "exchange": exchange},
        )
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors), code=400)
        match = serializer.save()
        return success(data={"match_id": match.match_id}, message="匹配申请已提交")


class ExchangeMatchAcceptView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, exchange_id, match_id):
        try:
            exchange = ExchangeRequest.objects.get(exchange_id=exchange_id)
        except ExchangeRequest.DoesNotExist:
            return error(message="换物请求不存在", code=404)

        # 验证权限：只有换物请求发起者可以接受匹配
        if request.user != exchange.owner:
            return error(message="无权操作此换物请求", code=403)

        try:
            match = ExchangeMatch.objects.get(match_id=match_id, request=exchange)
        except ExchangeMatch.DoesNotExist:
            return error(message="匹配记录不存在", code=404)

        serializer = ExchangeMatchAcceptSerializer(match, data={})
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors), code=400)
        serializer.save()
        return success(message="匹配已接受")


class ExchangeMatchRejectView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, exchange_id, match_id):
        try:
            exchange = ExchangeRequest.objects.get(exchange_id=exchange_id)
        except ExchangeRequest.DoesNotExist:
            return error(message="换物请求不存在", code=404)

        # 验证权限：只有换物请求发起者可以拒绝匹配
        if request.user != exchange.owner:
            return error(message="无权操作此换物请求", code=403)

        try:
            match = ExchangeMatch.objects.get(match_id=match_id, request=exchange)
        except ExchangeMatch.DoesNotExist:
            return error(message="匹配记录不存在", code=404)

        serializer = ExchangeMatchRejectSerializer(match, data=request.data)
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors), code=400)
        serializer.save()
        return success(message="匹配已拒绝")


class ExchangeCompleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, exchange_id):
        try:
            exchange = ExchangeRequest.objects.get(exchange_id=exchange_id)
        except ExchangeRequest.DoesNotExist:
            return error(message="换物请求不存在", code=404)

        # 验证权限：只有换物请求发起者可以确认完成
        if request.user != exchange.owner:
            return error(message="无权操作此换物请求", code=403)

        serializer = ExchangeCompleteSerializer(exchange, data={})
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors), code=400)
        serializer.save()
        return success(message="换物已完成")


class ExchangeCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, exchange_id):
        try:
            exchange = ExchangeRequest.objects.get(exchange_id=exchange_id)
        except ExchangeRequest.DoesNotExist:
            return error(message="换物请求不存在", code=404)

        # 验证权限：只有换物请求发起者可以取消
        if request.user != exchange.owner:
            return error(message="无权操作此换物请求", code=403)

        serializer = ExchangeCancelSerializer(exchange, data={}, context={"request": request})
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors), code=400)
        serializer.save()
        return success(message="换物请求已取消")


# ==================== 管理员端换物管理 ====================


class AdminExchangeListView(APIView):
    """管理员查看换物请求列表，支持搜索、状态筛选、时间筛选。"""
    permission_classes = [IsAdmin]

    def get(self, request):
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))
        keyword = request.query_params.get("keyword", "").strip()
        status_filter = request.query_params.get("status", "").strip()
        start_date = request.query_params.get("start_date", "").strip()
        end_date = request.query_params.get("end_date", "").strip()

        queryset = ExchangeRequest.objects.select_related(
            "owner", "offered_asset__product"
        ).all()

        # 关键词搜索：编号、发起用户昵称/手机号、换出资产商品名
        if keyword:
            queryset = queryset.filter(
                Q(exchange_id__icontains=keyword)
                | Q(owner__nickname__icontains=keyword)
                | Q(owner__phone__icontains=keyword)
                | Q(offered_asset__product__name__icontains=keyword)
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

        serializer = ExchangeRequestListSerializer(page_obj, many=True)
        data = paginated(page_obj, serializer, page_size)

        return success(data=data)


class AdminExchangeDetailView(APIView):
    """管理员查看换物请求详情（含匹配记录和状态日志）。"""
    permission_classes = [IsAdmin]

    def get(self, request, exchange_id):
        try:
            exchange = ExchangeRequest.objects.select_related(
                "owner", "offered_asset__product"
            ).get(exchange_id=exchange_id)
        except ExchangeRequest.DoesNotExist:
            return error(message="换物请求不存在", code=404)

        data = ExchangeRequestDetailSerializer(exchange).data
        return success(data=data)


class AdminExchangeExpireView(APIView):
    """管理员标记换物请求为已过期，释放资产。"""
    permission_classes = [IsAdmin]

    def post(self, request, exchange_id):
        try:
            exchange = ExchangeRequest.objects.get(exchange_id=exchange_id)
        except ExchangeRequest.DoesNotExist:
            return error(message="换物请求不存在", code=404)

        if exchange.status not in (ExchangeRequest.Status.ACTIVE, ExchangeRequest.Status.MATCHED):
            return error(message="当前状态不允许标记过期", code=400)

        old_status = exchange.status

        # 释放发起方资产
        asset = exchange.offered_asset
        asset.quantity += 1
        asset.save()

        # 如果已匹配，释放对方资产并更新匹配记录
        if old_status == ExchangeRequest.Status.MATCHED:
            match = exchange.matches.filter(status=ExchangeMatch.Status.ACCEPTED).first()
            if match:
                match.applicant_asset.quantity += 1
                match.applicant_asset.save()
                match.status = ExchangeMatch.Status.EXPIRED
                match.save()

        # 更新换物请求状态
        exchange.status = ExchangeRequest.Status.EXPIRED
        exchange.save()

        # 记录状态日志
        from apps.common.id_generator import generate_op_log_id
        ExchangeStatusLog.objects.create(
            log_id=generate_op_log_id(),
            exchange=exchange,
            from_status=old_status,
            to_status=ExchangeRequest.Status.EXPIRED,
            operator=request.user,
            note="管理员标记过期",
        )

        # 记录管理员操作日志
        from apps.operations.models import AdminOperationLog
        AdminOperationLog.objects.create(
            op_log_id=generate_op_log_id(),
            admin=request.user,
            module="换物管理",
            action="标记过期",
            target_id=exchange_id,
            detail=f"将换物请求 {exchange_id} 从 {old_status} 标记为已过期",
        )

        logger.info("管理员 %s 标记换物请求 %s 为已过期", request.user.user_id, exchange_id)
        return success(message="换物请求已标记为过期")


class AdminExchangeCancelView(APIView):
    """管理员取消换物请求，释放资产。"""
    permission_classes = [IsAdmin]

    def post(self, request, exchange_id):
        try:
            exchange = ExchangeRequest.objects.get(exchange_id=exchange_id)
        except ExchangeRequest.DoesNotExist:
            return error(message="换物请求不存在", code=404)

        if exchange.status not in (ExchangeRequest.Status.ACTIVE, ExchangeRequest.Status.MATCHED):
            return error(message="当前状态不允许取消", code=400)

        reason = request.data.get("reason", "管理员取消")
        old_status = exchange.status

        # 释放发起方资产
        asset = exchange.offered_asset
        asset.quantity += 1
        asset.save()

        # 如果已匹配，释放对方资产并更新匹配记录
        if old_status == ExchangeRequest.Status.MATCHED:
            match = exchange.matches.filter(status=ExchangeMatch.Status.ACCEPTED).first()
            if match:
                match.applicant_asset.quantity += 1
                match.applicant_asset.save()
                match.status = ExchangeMatch.Status.REJECTED
                match.save()

        # 更新换物请求状态
        exchange.status = ExchangeRequest.Status.CANCELLED
        exchange.save()

        # 记录状态日志
        from apps.common.id_generator import generate_op_log_id
        ExchangeStatusLog.objects.create(
            log_id=generate_op_log_id(),
            exchange=exchange,
            from_status=old_status,
            to_status=ExchangeRequest.Status.CANCELLED,
            operator=request.user,
            note=f"管理员取消：{reason}",
        )

        # 记录管理员操作日志
        from apps.operations.models import AdminOperationLog
        AdminOperationLog.objects.create(
            op_log_id=generate_op_log_id(),
            admin=request.user,
            module="换物管理",
            action="取消换物",
            target_id=exchange_id,
            detail=f"管理员取消换物请求 {exchange_id}，原因：{reason}",
        )

        logger.info("管理员 %s 取消换物请求 %s", request.user.user_id, exchange_id)
        return success(message="换物请求已取消")


class AdminExchangeCompleteView(APIView):
    """管理员手动完成换物请求（双方资产交换归属）。"""
    permission_classes = [IsAdmin]

    def post(self, request, exchange_id):
        try:
            exchange = ExchangeRequest.objects.get(exchange_id=exchange_id)
        except ExchangeRequest.DoesNotExist:
            return error(message="换物请求不存在", code=404)

        if exchange.status != ExchangeRequest.Status.MATCHED:
            return error(message="只有已匹配的换物请求才能标记完成", code=400)

        match = exchange.matches.filter(status=ExchangeMatch.Status.ACCEPTED).first()
        if not match:
            return error(message="没有已接受的匹配记录", code=400)

        # 交换资产归属
        owner_asset = exchange.offered_asset
        applicant_asset = match.applicant_asset

        owner_asset.owner = match.applicant
        owner_asset.quantity += 1
        owner_asset.save()

        applicant_asset.owner = exchange.owner
        applicant_asset.quantity += 1
        applicant_asset.save()

        # 更新状态
        exchange.status = ExchangeRequest.Status.COMPLETED
        exchange.save()

        # 记录状态日志
        from apps.common.id_generator import generate_op_log_id
        ExchangeStatusLog.objects.create(
            log_id=generate_op_log_id(),
            exchange=exchange,
            from_status=ExchangeRequest.Status.MATCHED,
            to_status=ExchangeRequest.Status.COMPLETED,
            operator=request.user,
            note="管理员确认完成",
        )

        # 记录管理员操作日志
        from apps.operations.models import AdminOperationLog
        AdminOperationLog.objects.create(
            op_log_id=generate_op_log_id(),
            admin=request.user,
            module="换物管理",
            action="确认完成",
            target_id=exchange_id,
            detail=f"管理员确认换物请求 {exchange_id} 完成",
        )

        # 双方获得信用分
        from apps.credits.services import create_credit_record, CREDIT_EXCHANGE_COMPLETE
        create_credit_record(user=exchange.owner, change_value=CREDIT_EXCHANGE_COMPLETE, reason=f"完成换物 {exchange_id}")
        create_credit_record(user=match.applicant, change_value=CREDIT_EXCHANGE_COMPLETE, reason=f"完成换物 {exchange_id}")

        logger.info("管理员 %s 确认换物请求 %s 完成", request.user.user_id, exchange_id)
        return success(message="换物已完成")


class AdminExchangeHandleAbnormalView(APIView):
    """管理员处理异常换物请求（如资产不可用、系统异常等），标记为已取消并释放资产。"""
    permission_classes = [IsAdmin]

    def post(self, request, exchange_id):
        try:
            exchange = ExchangeRequest.objects.get(exchange_id=exchange_id)
        except ExchangeRequest.DoesNotExist:
            return error(message="换物请求不存在", code=404)

        if exchange.status in (ExchangeRequest.Status.COMPLETED, ExchangeRequest.Status.CANCELLED, ExchangeRequest.Status.EXPIRED):
            return error(message="当前状态不允许处理异常", code=400)

        reason = request.data.get("reason", "")
        if not reason:
            return error(message="请填写异常原因", code=400)

        old_status = exchange.status

        # 释放发起方资产
        asset = exchange.offered_asset
        asset.quantity += 1
        asset.save()

        # 如果已匹配，释放对方资产并更新匹配记录
        if old_status == ExchangeRequest.Status.MATCHED:
            match = exchange.matches.filter(status=ExchangeMatch.Status.ACCEPTED).first()
            if match:
                match.applicant_asset.quantity += 1
                match.applicant_asset.save()
                match.status = ExchangeMatch.Status.REJECTED
                match.save()

        # 更新换物请求状态为已取消
        exchange.status = ExchangeRequest.Status.CANCELLED
        exchange.save()

        # 记录状态日志
        from apps.common.id_generator import generate_op_log_id
        ExchangeStatusLog.objects.create(
            log_id=generate_op_log_id(),
            exchange=exchange,
            from_status=old_status,
            to_status=ExchangeRequest.Status.CANCELLED,
            operator=request.user,
            note=f"管理员处理异常：{reason}",
        )

        # 记录管理员操作日志
        from apps.operations.models import AdminOperationLog
        AdminOperationLog.objects.create(
            op_log_id=generate_op_log_id(),
            admin=request.user,
            module="换物管理",
            action="处理异常",
            target_id=exchange_id,
            detail=f"管理员处理异常换物 {exchange_id}，原因：{reason}",
        )

        logger.info("管理员 %s 处理异常换物请求 %s，原因：%s", request.user.user_id, exchange_id, reason)
        return success(message="异常换物已处理，资产已释放")
