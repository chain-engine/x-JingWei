#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用数据模型和请求/响应Schema
"""

from typing import Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

from constants.constants import (
    DEFAULT_PAGE,
    DEFAULT_PAGE_SIZE,
    MIN_PAGE_SIZE,
    MAX_PAGE_SIZE,
    EMAIL_REGEX,
    PHONE_REGEX,
    UUID_REGEX
)


class BaseSchema(BaseModel):
    """基础Schema"""

    class Config:
        """Pydantic配置"""
        from_attributes = True
        json_schema_extra = {"example": {}}


class TimestampMixin(BaseModel):
    """时间戳Mixin"""

    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")

    class Config:
        from_attributes = True


class IdMixin(BaseModel):
    """ID Mixin"""

    id: str = Field(description="记录ID")

    class Config:
        from_attributes = True


class PaginationParams(BaseModel):
    """分页参数"""

    page: int = Field(default=DEFAULT_PAGE, ge=1, description="页码")
    page_size: int = Field(
        default=DEFAULT_PAGE_SIZE,
        ge=MIN_PAGE_SIZE,
        le=MAX_PAGE_SIZE,
        description="每页记录数"
    )

    @field_validator("page")
    @classmethod
    def validate_page(cls, v: int) -> int:
        """验证页码"""
        return max(1, v)

    @field_validator("page_size")
    @classmethod
    def validate_page_size(cls, v: int) -> int:
        """验证每页记录数"""
        return max(MIN_PAGE_SIZE, min(MAX_PAGE_SIZE, v))

    class Config:
        json_schema_extra = {
            "example": {"page": 1, "page_size": 20}
        }


class SortParams(BaseModel):
    """排序参数"""

    sort_by: Optional[str] = Field(default=None, description="排序字段")
    sort_order: Optional[str] = Field(default="asc", description="排序方向：asc/desc")

    @field_validator("sort_order")
    @classmethod
    def validate_sort_order(cls, v: Optional[str]) -> Optional[str]:
        """验证排序方向"""
        if v is None:
            return "asc"
        if v.lower() not in ("asc", "desc"):
            raise ValueError("sort_order must be 'asc' or 'desc'")
        return v.lower()

    class Config:
        json_schema_extra = {
            "example": {"sort_by": "created_at", "sort_order": "desc"}
        }


class EmailValidator(BaseModel):
    """邮箱验证器"""

    email: str = Field(..., description="邮箱地址")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """验证邮箱格式"""
        import re
        if not re.match(EMAIL_REGEX, v):
            raise ValueError("Invalid email format")
        return v.lower()

    class Config:
        json_schema_extra = {
            "example": {"email": "user@example.com"}
        }


class PhoneValidator(BaseModel):
    """手机号验证器"""

    phone: str = Field(..., description="手机号码")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """验证手机号格式"""
        import re
        if not re.match(PHONE_REGEX, v):
            raise ValueError("Invalid phone number format")
        return v

    class Config:
        json_schema_extra = {
            "example": {"phone": "13800138000"}
        }


class UUIDValidator(BaseModel):
    """UUID验证器"""

    uuid: str = Field(..., description="UUID")

    @field_validator("uuid")
    @classmethod
    def validate_uuid(cls, v: str) -> str:
        """验证UUID格式"""
        import re
        if not re.match(UUID_REGEX, v):
            raise ValueError("Invalid UUID format")
        return v

    class Config:
        json_schema_extra = {
            "example": {"uuid": "123e4567-e89b-12d3-a456-426614174000"}
        }


class HealthCheckResponse(BaseSchema):
    """健康检查响应"""

    status: str = Field(description="服务状态")
    version: str = Field(description="版本号")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="时间戳")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "0.1.0",
                "timestamp": "2024-01-01T00:00:00"
            }
        }


class VersionResponse(BaseSchema):
    """版本信息响应"""

    name: str = Field(description="应用名称")
    version: str = Field(description="版本号")
    description: str = Field(description="应用描述")
    environment: str = Field(description="运行环境")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "x-jingwei",
                "version": "0.1.0",
                "description": "X-JingWei 经纬 - Production Grade LLM Application Development Platform",
                "environment": "development"
            }
        }


class ErrorResponse(BaseSchema):
    """错误响应"""

    code: int = Field(description="错误码")
    message: str = Field(description="错误消息")
    details: Optional[dict[str, Any]] = Field(default=None, description="错误详情")
    request_id: Optional[str] = Field(default=None, description="请求ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="时间戳")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 50001,
                "message": "Internal server error",
                "details": None,
                "request_id": "123e4567-e89b-12d3-a456-426614174000",
                "timestamp": "2024-01-01T00:00:00"
            }
        }


class ValidationErrorDetail(BaseSchema):
    """校验错误详情"""

    field: str = Field(description="字段名")
    message: str = Field(description="错误消息")
    value: Optional[Any] = Field(default=None, description="字段值")

    class Config:
        json_schema_extra = {
            "example": {
                "field": "email",
                "message": "Invalid email format",
                "value": "invalid-email"
            }
        }


class ValidationErrorResponse(BaseSchema):
    """参数校验错误响应"""

    code: int = Field(description="错误码")
    message: str = Field(description="错误消息")
    errors: list[ValidationErrorDetail] = Field(default_factory=list, description="错误详情列表")
    request_id: Optional[str] = Field(default=None, description="请求ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="时间戳")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 40001,
                "message": "Validation failed",
                "errors": [],
                "request_id": "123e4567-e89b-12d3-a456-426614174000",
                "timestamp": "2024-01-01T00:00:00"
            }
        }