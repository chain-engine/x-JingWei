#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ORM 实体基类

纯数据表映射模型基类，仅定义字段、表关联关系，无任何查询、业务逻辑。
"""

from infra.mysql.models import Base


__all__ = ["Base"]