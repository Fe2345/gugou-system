from django.core.paginator import Paginator
from django.db.models import Q, Sum
from rest_framework.views import APIView

from apps.common.permissions import IsAdmin
from apps.common.response import error, paginated, success

from .models import User
from .serializers import AdminUserSerializer


class AdminUserListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        keyword = request.query_params.get("keyword", "").strip()
        status_filter = request.query_params.get("status", "").strip()
        credit_level = request.query_params.get("creditLevel", "").strip()

        queryset = User.objects.all().order_by("-created_at")

        if keyword:
            queryset = queryset.filter(
                Q(user_id__icontains=keyword)
                | Q(nickname__icontains=keyword)
                | Q(phone__icontains=keyword)
            )

        if status_filter and status_filter != "all":
            # frontend sends Chinese labels, map to backend values
            status_map = {"正常": User.Status.NORMAL, "冻结": User.Status.FROZEN,
                          "active": User.Status.NORMAL}
            status_filter = status_map.get(status_filter, status_filter)
            queryset = queryset.filter(status=status_filter)

        if credit_level:
            if credit_level == "高":
                queryset = queryset.filter(credit_score__gte=90)
            elif credit_level == "中":
                queryset = queryset.filter(credit_score__gte=70, credit_score__lt=90)
            elif credit_level == "低":
                queryset = queryset.filter(credit_score__lt=70)

        queryset = queryset.annotate(
            total_assets=Sum("assets__current_value", default=0)
        )

        try:
            page = int(request.query_params.get("page", 1))
            page_size = int(request.query_params.get("page_size", 20))
        except (ValueError, TypeError):
            page, page_size = 1, 20

        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        serializer = AdminUserSerializer(page_obj, many=True)
        return success(data=paginated(page_obj, serializer, page_size))


class AdminUserFreezeView(APIView):
    permission_classes = [IsAdmin]

    def put(self, request, user_id):
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return error(message="用户不存在", code=404)

        if user.status == User.Status.FROZEN:
            return error(message="用户已被冻结", code=400)

        user.status = User.Status.FROZEN
        user.save(update_fields=["status", "updated_at"])
        return success(message="操作成功")


class AdminUserUnfreezeView(APIView):
    permission_classes = [IsAdmin]

    def put(self, request, user_id):
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return error(message="用户不存在", code=404)

        if user.status != User.Status.FROZEN:
            return error(message="当前状态不允许此操作", code=400)

        user.status = User.Status.NORMAL
        user.save(update_fields=["status", "updated_at"])
        return success(message="操作成功")
