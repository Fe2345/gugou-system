import logging

from django.db import models
from rest_framework import status
from rest_framework.views import APIView

from apps.common.permissions import IsAuthenticated
from apps.common.response import error, success, paginated
from .models import CreditRecord
from .serializers import CreditRecordListSerializer, CreditSummarySerializer

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

        # 计算总信用分
        total_credit = CreditRecord.objects.filter(user=user).aggregate(
            total=models.Sum("change_value")
        )["total"] or 0

        # 统计正负记录数
        positive_count = CreditRecord.objects.filter(user=user, change_value__gt=0).count()
        negative_count = CreditRecord.objects.filter(user=user, change_value__lt=0).count()

        # 获取最近记录
        recent_records = CreditRecord.objects.filter(user=user).order_by("-created_at")[:5]

        data = {
            "total_credit": total_credit,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "recent_records": CreditRecordListSerializer(recent_records, many=True).data,
        }

        return success(data=data)
