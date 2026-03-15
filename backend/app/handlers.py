"""
全局异常处理器
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError

from app.exceptions import AppException


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """处理自定义应用异常"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
            "detail": exc.detail
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """处理请求验证错误"""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error.get("loc", []))
        errors.append({
            "field": field,
            "message": error.get("msg", "验证失败"),
            "type": error.get("type", "validation_error")
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": "VALIDATION_ERROR",
            "message": "请求参数验证失败",
            "detail": {"errors": errors}
        }
    )


async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """处理数据库完整性错误"""
    error_msg = str(exc.orig) if hasattr(exc, "orig") else str(exc)

    # 解析常见错误类型
    if "UNIQUE constraint failed" in error_msg or "Duplicate entry" in error_msg:
        message = "数据已存在，请检查是否重复提交"
    elif "FOREIGN KEY constraint failed" in error_msg or "foreign key constraint" in error_msg:
        message = "关联数据不存在"
    else:
        message = "数据操作失败，请检查数据完整性"

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "code": "INTEGRITY_ERROR",
            "message": message,
            "detail": {"original_error": error_msg}
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """处理未捕获的通用异常"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": "INTERNAL_ERROR",
            "message": "服务器内部错误，请稍后重试",
            "detail": {}
        }
    )


def register_exception_handlers(app):
    """注册异常处理器到应用"""
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    # 生产环境可以注释掉下面的通用异常处理器
    # app.add_exception_handler(Exception, generic_exception_handler)
