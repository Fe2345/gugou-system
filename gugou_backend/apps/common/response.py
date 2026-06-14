"""
统一响应格式。

成功:
  {"code": 200, "message": "success", "data": {...}}

分页:
  {"code": 200, "message": "success", "data": {"count": 100, "page": 1, "page_size": 10, "results": [...]}}

错误:
  {"code": 400, "message": "参数错误", "data": null}
"""

from typing import Optional

from rest_framework.response import Response as DRFResponse


def success(data=None, message: str = "success", code: int = 200) -> DRFResponse:
    return DRFResponse({"code": code, "message": message, "data": data})


def error(message: str = "error", code: int = 400, data=None, http_status: Optional[int] = None) -> DRFResponse:
    if http_status is None:
        http_status = code
    return DRFResponse({"code": code, "message": message, "data": data}, status=http_status)


def flatten_errors(errors) -> str:
    """将 DRF serializer.errors（dict/list）展平为一条可读字符串。"""
    if isinstance(errors, list):
        return str(errors[0]) if errors else "参数错误"
    if isinstance(errors, dict):
        first_key = next(iter(errors))
        first_val = errors[first_key]
        if isinstance(first_val, list):
            return str(first_val[0]) if first_val else f"{first_key}: 参数错误"
        if isinstance(first_val, str):
            return str(first_val)
        return f"{first_key}: 参数错误"
    return str(errors)


def paginated(page_obj, serializer, page_size=None) -> dict:
    """组装分页响应 data 部分，配合 Django Paginator 使用。

    Args:
        page_obj: Paginator.get_page() 返回的 Page 对象
        serializer: 序列化器实例
        page_size: 每页数量
    """
    return {
        "count": page_obj.paginator.count,
        "page": page_obj.number,
        "page_size": page_size or page_obj.paginator.per_page,
        "results": serializer.data,
    }
