"""
统一响应格式。

成功:
  {"code": 200, "message": "success", "data": {...}}

分页:
  {"code": 200, "message": "success", "data": {"count": 100, "page": 1, "page_size": 10, "results": [...]}}

错误:
  {"code": 400, "message": "参数错误", "data": null}
"""

from rest_framework.response import Response as DRFResponse


def success(data=None, message: str = "success", code: int = 200) -> DRFResponse:
    return DRFResponse({"code": code, "message": message, "data": data})


def error(message: str = "error", code: int = 400, data=None) -> DRFResponse:
    return DRFResponse({"code": code, "message": message, "data": data})


def paginated(paginator, serializer) -> dict:
    """组装分页响应 data 部分，配合 DRF PageNumberPagination 使用。"""
    return {
        "count": paginator.page.paginator.count,
        "page": paginator.page.number,
        "page_size": paginator.get_page_size(paginator.request),
        "results": serializer.data,
    }
