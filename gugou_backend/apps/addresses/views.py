import logging

from django.db.models import Q
from rest_framework.views import APIView

from apps.common.permissions import IsAuthenticated
from apps.common.response import error, flatten_errors, success
from .models import Address, Division
from .serializers import AddressSerializer, AddressWriteSerializer, DivisionSerializer

logger = logging.getLogger("gugou")


class DivisionListView(APIView):
    """查询行政区划：?parent_code=440000 → 列出下辖市/区"""

    def get(self, request):
        parent_code = request.query_params.get("parent_code")
        qs = Division.objects.all()
        if parent_code:
            qs = qs.filter(parent__code=parent_code)
        else:
            qs = qs.filter(level=1)  # 默认返回所有省
        return success(data=DivisionSerializer(qs, many=True).data)


class AddressListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Address.objects.filter(user=request.user)
        # 确保有且只有一个默认地址
        self._ensure_default(request.user)
        return success(data=AddressSerializer(qs, many=True).data)

    def post(self, request):
        user = request.user
        if Address.objects.filter(user=user).count() >= 10:
            return error(message="最多添加 10 个收货地址", code=400)

        serializer = AddressWriteSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors), code=400)
        data = serializer.validated_data
        addr = Address.objects.create(
            user=user,
            receiver_name=data["receiver_name"],
            receiver_phone=data["receiver_phone"],
            province_id=data["province_code"],
            city_id=data["city_code"],
            district_id=data["district_code"],
            street=data["street"],
            detail=data["detail"],
            is_default=data["is_default"],
        )
        return success(data=AddressSerializer(addr).data)

    @staticmethod
    def _ensure_default(user):
        qs = Address.objects.filter(user=user)
        if not qs.filter(is_default=True).exists() and qs.exists():
            first = qs.first()
            first.is_default = True
            first.save(update_fields=["is_default"])


class AddressDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get(self, user, pk):
        try:
            return Address.objects.get(pk=pk, user=user)
        except Address.DoesNotExist:
            return None

    def put(self, request, pk):
        addr = self._get(request.user, pk)
        if addr is None:
            return error(message="地址不存在", code=404)

        serializer = AddressWriteSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message=flatten_errors(serializer.errors), code=400)
        d = serializer.validated_data
        addr.receiver_name = d["receiver_name"]
        addr.receiver_phone = d["receiver_phone"]
        addr.province_id = d["province_code"]
        addr.city_id = d["city_code"]
        addr.district_id = d["district_code"]
        addr.street = d["street"]
        addr.detail = d["detail"]
        addr.is_default = d["is_default"]
        addr.save()
        return success(data=AddressSerializer(addr).data)

    def delete(self, request, pk):
        addr = self._get(request.user, pk)
        if addr is None:
            return error(message="地址不存在", code=404)
        user = request.user
        was_default = addr.is_default
        addr.delete()
        # 删了默认地址，补一个
        if was_default:
            first = Address.objects.filter(user=user).first()
            if first:
                first.is_default = True
                first.save(update_fields=["is_default"])
        return success(message="已删除")
