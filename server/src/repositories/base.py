#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
仓库基类

定义数据访问层的通用接口
"""

from typing import Any, Optional
from abc import ABC, abstractmethod


class Repository(ABC):
    """仓库基类"""

    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[Any]:
        """根据ID获取实体"""
        pass

    @abstractmethod
    async def create(self, entity: Any) -> Any:
        """创建实体"""
        pass

    @abstractmethod
    async def update(self, entity: Any) -> Any:
        """更新实体"""
        pass

    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        """删除实体"""
        pass

    @abstractmethod
    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[dict[str, Any]] = None,
    ) -> tuple[list[Any], int]:
        """查询所有实体"""
        pass