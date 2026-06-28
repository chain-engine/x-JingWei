#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
响应格式标准化
定义统一的响应数据结构
"""

from typing import Any, Generic, TypeVar
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from constants.constants import (
    CODE_SUCCESS,
    CODE_ERROR,
    CODE_VALIDATION_ERROR,
    CODE_UNAUTHORIZED,
    CODE_FORBIDDEN,
    CODE_NOT_FOUND,
    CODE_RATE_LIMIT_EXCEEDED,
    MSG_SUCCESS
)

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    """通用响应模型"""

    code: int = Field(..., description="响应状态码", example=0)
    message: str = Field(..., description="响应消息", example="Success")
    data: T | None = Field(None, description="响应数据")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="响应时间戳")
    request_id: str | None = Field(None, description="请求ID")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 0,
                "message": "Success",
                "data": None,
                "timestamp": "2024-01-01T00:00:00",
                "request_id": "uuid-here"
            }
        }

    @classmethod
    def success(
        cls,
        data: T | None = None,
        message: str = MSG_SUCCESS,
        code: int = CODE_SUCCESS,
        request_id: str | None = None
    ) -> dict[str, Any]:
        """构造成功响应

        Args:
            data: 响应数据
            message: 响应消息
            code: 状态码
            request_id: 请求ID

        Returns:
            dict[str, Any]: 响应字典
        """
        return cls(code=code, message=message, data=data, request_id=request_id).model_dump()

    @classmethod
    def error(
        cls,
        message: str = "An error occurred",
        code: int = CODE_ERROR,
        data: T | None = None,
        request_id: str | None = None
    ) -> dict[str, Any]:
        """构造错误响应

        Args:
            message: 错误消息
            code: 错误状态码
            data: 错误详情数据
            request_id: 请求ID

        Returns:
            dict[str, Any]: 错误响应字典
        """
        return cls(code=code, message=message, data=data, request_id=request_id).model_dump()

    @classmethod
    def validation_error(
        cls,
        message: str = "Validation failed",
        errors: list[dict[str, Any]] | None = None,
        request_id: str | None = None
    ) -> dict[str, Any]:
        """创建参数校验错误响应

        Args:
            message: 错误消息
            errors: 错误详情列表
            request_id: 请求ID

        Returns:
            dict[str, Any]: 响应字典
        """
        return cls(
            code=CODE_VALIDATION_ERROR,
            message=message,
            data={"errors": errors} if errors else None,
            request_id=request_id
        ).model_dump()

    @classmethod
    def unauthorized(
        cls,
        message: str = "Unauthorized",
        request_id: str | None = None
    ) -> dict[str, Any]:
        """创建未授权响应

        Args:
            message: 错误消息
            request_id: 请求ID

        Returns:
            dict[str, Any]: 响应字典
        """
        return cls(code=CODE_UNAUTHORIZED, message=message, request_id=request_id).model_dump()

    @classmethod
    def forbidden(
        cls,
        message: str = "Forbidden",
        request_id: str | None = None
    ) -> dict[str, Any]:
        """创建禁止访问响应

        Args:
            message: 错误消息
            request_id: 请求ID

        Returns:
            dict[str, Any]: 响应字典
        """
        return cls(code=CODE_FORBIDDEN, message=message, request_id=request_id).model_dump()

    @classmethod
    def not_found(
        cls,
        message: str = "Resource not found",
        request_id: str | None = None
    ) -> dict[str, Any]:
        """创建资源未找到响应

        Args:
            message: 错误消息
            request_id: 请求ID

        Returns:
            dict[str, Any]: 响应字典
        """
        return cls(code=CODE_NOT_FOUND, message=message, request_id=request_id).model_dump()

    @classmethod
    def conflict(
        cls,
        message: str = "Resource conflict",
        request_id: str | None = None
    ) -> dict[str, Any]:
        """创建资源冲突响应

        Args:
            message: 错误消息
            request_id: 请求ID

        Returns:
            dict[str, Any]: 响应字典
        """
        return cls(code=40901, message=message, request_id=request_id).model_dump()

    @classmethod
    def rate_limit_exceeded(
        cls,
        message: str = "Rate limit exceeded",
        request_id: str | None = None
    ) -> dict[str, Any]:
        """创建限流响应

        Args:
            message: 错误消息
            request_id: 请求ID

        Returns:
            dict[str, Any]: 响应字典
        """
        return cls(code=CODE_RATE_LIMIT_EXCEEDED, message=message, request_id=request_id).model_dump()


class PageModel(BaseModel, Generic[T]):
    """分页模型"""

    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页记录数")
    total_pages: int = Field(..., description="总页数")
    items: list[T] = Field(..., description="数据列表")

    class Config:
        json_schema_extra = {
            "example": {
                "total": 100,
                "page": 1,
                "page_size": 20,
                "total_pages": 5,
                "items": []
            }
        }


class ErrorDetail(BaseModel):
    """错误详情模型"""

    field: str | None = Field(None, description="错误字段")
    message: str = Field(..., description="错误消息")
    type: str = Field(..., description="错误类型")

    class Config:
        json_schema_extra = {
            "example": {
                "field": "email",
                "message": "Invalid email format",
                "type": "ValueError"
            }
        }


class ErrorResponse(BaseModel):
    """错误响应模型"""

    code: int = Field(..., description="错误状态码", example=400)
    message: str = Field(..., description="错误消息", example="Bad Request")
    errors: list[ErrorDetail] | None = Field(None, description="错误详情列表")
    request_id: str | None = Field(None, description="请求ID")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 400,
                "message": "Bad Request",
                "errors": [
                    {
                        "field": "email",
                        "message": "Invalid email format",
                        "type": "ValueError"
                    }
                ],
                "request_id": "uuid-here"
            }
        }


def success_response(
    data: Any = None,
    message: str = "success",
    code: int = 200,
    request_id: str | None = None
) -> dict[str, Any]:
    """构造成功响应（便捷函数）

    Args:
        data: 响应数据
        message: 响应消息
        code: 状态码
        request_id: 请求ID

    Returns:
        dict[str, Any]: 响应字典
    """
    return {
        "code": code,
        "message": message,
        "data": data,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_id": request_id
    }


def error_response(
    message: str,
    code: int = 500,
    errors: list[ErrorDetail] | None = None,
    request_id: str | None = None
) -> dict[str, Any]:
    """构造错误响应（便捷函数）

    Args:
        message: 错误消息
        code: 错误状态码
        errors: 错误详情列表
        request_id: 请求ID

    Returns:
        dict[str, Any]: 错误响应字典
    """
    response = {
        "code": code,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_id": request_id
    }

    if errors:
        response["errors"] = errors

    return response


def pagination_response(
    items: list[Any],
    total: int,
    page: int,
    page_size: int,
    message: str = MSG_SUCCESS,
    code: int = CODE_SUCCESS,
    request_id: str | None = None
) -> dict[str, Any]:
    """分页响应便捷函数

    Args:
        items: 数据列表
        total: 总记录数
        page: 当前页码
        page_size: 每页记录数
        message: 响应消息
        code: 业务状态码
        request_id: 请求ID

    Returns:
        dict[str, Any]: 响应字典
    """
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    paginated = PageModel(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        items=items
    )

    return success_response(
        data=paginated.model_dump(),
        message=message,
        code=code,
        request_id=request_id
    )