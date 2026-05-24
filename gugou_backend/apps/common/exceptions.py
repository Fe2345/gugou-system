import logging

from rest_framework.exceptions import (
    APIException,
    AuthenticationFailed,
    NotAuthenticated,
    NotFound,
    ParseError,
    PermissionDenied,
    ValidationError,
)
from rest_framework.views import exception_handler as drf_exception_handler

from apps.common.response import error

logger = logging.getLogger("gugou")


def _first_message(detail):
    """从 DRF 的 detail 结构（可能是列表/字典）中提取第一条消息。"""
    if isinstance(detail, list):
        return str(detail[0])
    if isinstance(detail, dict):
        key = next(iter(detail))
        val = detail[key]
        if isinstance(val, list):
            return f"{key}: {val[0]}"
        return f"{key}: {val}"
    return str(detail)


def custom_exception_handler(exc, context):
    """统一异常响应 {code, message, data}。"""
    response = drf_exception_handler(exc, context)

    if response is not None:
        # DRF 已识别的异常
        if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
            response.data = error(message="请先登录", code=401).data
        elif isinstance(exc, PermissionDenied):
            response.data = error(message="没有权限执行此操作", code=403).data
        elif isinstance(exc, NotFound):
            response.data = error(message="资源不存在", code=404).data
        elif isinstance(exc, (ValidationError, ParseError)):
            response.data = error(message=_first_message(exc.detail), code=400).data
        elif isinstance(exc, APIException):
            response.data = error(message=str(exc.detail), code=exc.status_code).data
        else:
            response.data = error(message="请求处理错误", code=response.status_code).data
    else:
        # DRF 无法识别的异常 → 500
        logger.exception("未处理的异常: %s", exc)
        from rest_framework.response import Response
        return Response(error(message="服务器内部错误", code=500).data, status=500)

    return response
