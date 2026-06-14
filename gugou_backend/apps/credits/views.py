import logging

from django.db import models
from rest_framework import status as http_status
from rest_framework.views import APIView

from apps.common.permissions import IsAuthenticated, IsAdmin
from apps.common.response import error, flatten_errors, success, paginated
from .models import CreditRecord
from .serializers import AdminCreditAdjustSerializer, CreditRecordListSerializer, CreditSummarySerializer

logger = logging.getLogger("gugou")


class CreditRecordListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))

        queryset = CreditRecord.objects.filter(user=request.user).order_by("-created_at")

        from django.core.paginator import Paginator
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        serializer = CreditRecordListSerializer(page_obj, many=True)
        data = paginated(page_obj, serializer, page_size)

        return success(data=data)


class CreditSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        total_credit = user.credit_score

        # 统计正负记录数
        positive_count = CreditRecord.objects.filter(user=user, change_value__gt=0).count()
        negative_count = CreditRecord.objects.filter(user=user, change_value__lt=0).count()

        # 获取最近记录
        recent_records = CreditRecord.objects.filter(user=user).order_by("-created_at")[:5]

        # 获取交易限制信息
        from apps.credits.services import get_trading_restrictions
        restrictions = get_trading_restrictions(user.credit_score)

        data = {
            "total_credit": total_credit,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "recent_records": CreditRecordListSerializer(recent_records, many=True).data,
            "restrictions": restrictions,
        }

        return success(data=data)


class AdminCreditAdjustView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        serializer = AdminCreditAdjustSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors), code=400)

        from apps.accounts.models import User
        from apps.credits.services import create_credit_record

        user = User.objects.get(user_id=serializer.validated_data["user_id"])
        change_value = serializer.validated_data["change_value"]
        reason = serializer.validated_data["reason"]

        credit_record = create_credit_record(
            user=user,
            change_value=change_value,
            reason=f"[管理员调整] {reason}",
        )

        logger.info(
            "管理员 %s 调整用户 %s 信用分: %s, 原因: %s",
            request.user.user_id,
            user.user_id,
            f"{change_value:+d}",
            reason,
        )

        return success(data={
            "user_id": user.user_id,
            "credit_score": user.credit_score,
            "change_value": change_value,
            "reason": reason,
        }, message="信用分调整成功")
