import logging

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.common.permissions import IsAuthenticated
from apps.common.response import error, flatten_errors, success, paginated
from .models import ExchangeMatch, ExchangeRequest
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
        status_filter = request.query_params.get("status", ExchangeRequest.Status.ACTIVE)

        queryset = ExchangeRequest.objects.filter(status=status_filter).order_by("-created_at")

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
