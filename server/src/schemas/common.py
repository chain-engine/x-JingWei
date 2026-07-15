#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用 Schema 定义

包含所有业务 Schema 的基类和通用参数定义。
"""

from typing import Any, Optional, Generic, TypeVar
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from constants.constants import DEFAULT_PAGE, DEFAULT_PAGE_SIZE, MIN_PAGE_SIZE, MAX_PAGE_SIZE, CODE_SUCCESS, CODE_ERROR, MSG_SUCCESS, MSG_ERROR


class BaseSchema(BaseModel):
    """基础 Schema，所有业务 Schema 的基类

    提供统一的 Pydantic 配置：
    - from_attributes: True - 支持从 ORM 模型转换
    - json_schema_extra: 空示例，子类可覆盖
    """

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {"example": {}},
    }


class PaginationParams(BaseSchema):
    """分页参数"""

    page: int = Field(default=DEFAULT_PAGE, ge=1, description="页码")
    page_size: int = Field(
        default=DEFAULT_PAGE_SIZE,
        ge=MIN_PAGE_SIZE,
        le=MAX_PAGE_SIZE,
        description="每页记录数",
    )

    @field_validator("page")
    @classmethod
    def validate_page(cls, v: int) -> int:
        """验证页码，确保最小值为 1"""
        return max(1, v)

    @field_validator("page_size")
    @classmethod
    def validate_page_size(cls, v: int) -> int:
        """验证每页记录数，确保在有效范围内"""
        return max(MIN_PAGE_SIZE, min(MAX_PAGE_SIZE, v))

    model_config = {
        "json_schema_extra": {"example": {"page": 1, "page_size": 20}},
    }


T = TypeVar("T")


class ApiResponse(BaseSchema, Generic[T]):
    """通用 API 响应模型"""

    code: int = Field(default=CODE_SUCCESS, description="状态码")
    message: str = Field(default=MSG_SUCCESS, description="提示信息")
    data: Optional[T] = Field(default=None, description="响应数据")
    timestamp: datetime = Field(default_factory=lambda: datetime.utcnow(), description="响应时间")
    request_id: Optional[str] = Field(default=None, description="请求ID")

    model_config = {
        "json_schema_extra": {
            "example": {
                "code": CODE_SUCCESS,
                "message": MSG_SUCCESS,
                "data": {},
                "timestamp": "2024-01-01T00:00:00Z",
                "request_id": "abc123",
            }
        }
    }


class ApiErrorResponse(BaseSchema):
    """通用 API 错误响应模型"""

    code: int = Field(default=CODE_ERROR, description="错误码")
    message: str = Field(default=MSG_ERROR, description="错误信息")
    errors: Optional[list[dict[str, Any]]] = Field(default=None, description="详细错误列表")
    timestamp: datetime = Field(default_factory=lambda: datetime.utcnow(), description="响应时间")
    request_id: Optional[str] = Field(default=None, description="请求ID")

    model_config = {
        "json_schema_extra": {
            "example": {
                "code": CODE_ERROR,
                "message": MSG_ERROR,
                "errors": [],
                "timestamp": "2024-01-01T00:00:00Z",
                "request_id": "abc123",
            }
        }
    }


class PaginationResponse(BaseSchema, Generic[T]):
    """分页响应模型"""

    items: list[T] = Field(default_factory=list, description="数据列表")
    total: int = Field(default=0, description="总记录数")
    page: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=20, description="每页记录数")


class ApiPaginationResponse(BaseSchema, Generic[T]):
    """带分页的通用 API 响应模型"""

    code: int = Field(default=CODE_SUCCESS, description="状态码")
    message: str = Field(default=MSG_SUCCESS, description="提示信息")
    data: PaginationResponse[T] = Field(default_factory=PaginationResponse, description="分页数据")
    timestamp: datetime = Field(default_factory=lambda: datetime.utcnow(), description="响应时间")
    request_id: Optional[str] = Field(default=None, description="请求ID")