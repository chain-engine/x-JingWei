#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ORM 实体基类

纯数据表映射模型基类，仅定义字段、表关联关系，无任何查询、业务逻辑。
"""

from datetime import datetime
from sqlalchemy import Column, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TimestampMixin:
    """时间戳混入类"""
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)


class SoftDeleteMixin:
    """软删除混入类"""
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)


__all__ = ["Base", "TimestampMixin", "SoftDeleteMixin"]