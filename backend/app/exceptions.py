"""
自定义异常类
"""
from typing import Any, Dict, Optional


class AppException(Exception):
    """应用基础异常"""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        detail: Optional[Dict[str, Any]] = None
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.detail = detail or {}
        super().__init__(self.message)


class NotFoundError(AppException):
    """资源不存在异常"""

    def __init__(self, resource: str, resource_id: Optional[int] = None):
        message = f"{resource}不存在"
        if resource_id:
            message = f"{resource} (ID: {resource_id}) 不存在"
        super().__init__(
            code="NOT_FOUND",
            message=message,
            status_code=404
        )


class ValidationError(AppException):
    """验证错误异常"""

    def __init__(self, message: str, detail: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            status_code=422,
            detail=detail
        )


class ConflictError(AppException):
    """冲突错误异常（如重复、已存在等）"""

    def __init__(self, message: str, detail: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="CONFLICT",
            message=message,
            status_code=409,
            detail=detail
        )


class BusinessError(AppException):
    """业务逻辑错误异常"""

    def __init__(self, message: str, detail: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="BUSINESS_ERROR",
            message=message,
            status_code=400,
            detail=detail
        )
