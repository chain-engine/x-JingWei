#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Schema 基类
"""

from typing import Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import uuid4


class BaseEntity(BaseModel):
    """实体基类"""

    id: str = Field(default_factory=lambda: str(uuid4()), description="实体ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")

    model_config = {"from_attributes": True}

    def model_post_init(self, __context: Any) -> None:
        """模型初始化后处理"""
        if not self.updated_at:
            self.updated_at = datetime.utcnow()


class TimestampMixin(BaseModel):
    """时间戳Mixin"""

    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")

    def update_timestamp(self) -> None:
        """更新时间戳"""
        self.updated_at = datetime.utcnow()


class SoftDeleteMixin(BaseModel):
    """软删除Mixin"""

    is_deleted: bool = Field(default=False, description="是否删除")
    deleted_at: Optional[datetime] = Field(default=None, description="删除时间")
    deleted_by: Optional[str] = Field(default=None, description="删除人ID")

    def soft_delete(self, deleted_by: Optional[str] = None) -> None:
        """软删除"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        self.deleted_by = deleted_by

    def restore(self) -> None:
        """恢复"""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None