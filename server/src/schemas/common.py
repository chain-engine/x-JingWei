#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用 Schema 定义

包含所有业务 Schema 的基类和通用参数定义。
"""

from pydantic import BaseModel, Field, field_validator

from constants.constants import DEFAULT_PAGE, DEFAULT_PAGE_SIZE, MIN_PAGE_SIZE, MAX_PAGE_SIZE


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