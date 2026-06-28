#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档数据访问层
"""

from typing import Any, Optional

from core.logger import logger
from models.base import Repository


class DocumentRepository(Repository):
    """文档仓库

    实现文档数据的访问操作
    """

    def __init__(self) -> None:
        """初始化文档仓库"""
        self._documents: dict[str, dict[str, Any]] = {}
        logger.info("Document repository initialized")

    async def get_by_id(self, entity_id: str) -> Optional[dict[str, Any]]:
        """根据ID获取文档

        Args:
            entity_id: 文档ID

        Returns:
            Optional[dict[str, Any]]: 文档对象或None
        """
        return self._documents.get(entity_id)

    async def create(self, entity: dict[str, Any]) -> dict[str, Any]:
        """创建文档

        Args:
            entity: 文档对象

        Returns:
            dict[str, Any]: 创建的文档对象
        """
        entity_id = entity.get("id")
        if not entity_id:
            raise ValueError("Document ID is required")

        self._documents[entity_id] = entity
        logger.info(f"Document created: {entity_id}")
        return entity

    async def update(self, entity: dict[str, Any]) -> dict[str, Any]:
        """更新文档

        Args:
            entity: 文档对象

        Returns:
            dict[str, Any]: 更新后的文档对象
        """
        entity_id = entity.get("id")
        if not entity_id:
            raise ValueError("Document ID is required")

        if entity_id not in self._documents:
            raise ValueError(f"Document not found: {entity_id}")

        self._documents[entity_id].update(entity)
        logger.info(f"Document updated: {entity_id}")
        return self._documents[entity_id]

    async def delete(self, entity_id: str) -> bool:
        """删除文档

        Args:
            entity_id: 文档ID

        Returns:
            bool: 是否删除成功
        """
        if entity_id in self._documents:
            del self._documents[entity_id]
            logger.info(f"Document deleted: {entity_id}")
            return True
        return False

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[dict[str, Any]] = None
    ) -> tuple[list[dict[str, Any]], int]:
        """查询所有文档

        Args:
            skip: 跳过记录数
            limit: 限制记录数
            filters: 过滤条件

        Returns:
            tuple[list[dict[str, Any]], int]: 文档列表和总数
        """
        documents = list(self._documents.values())

        # 应用过滤条件
        if filters:
            for key, value in filters.items():
                documents = [doc for doc in documents if doc.get(key) == value]

        total = len(documents)
        items = documents[skip:skip + limit]

        return items, total

    async def count(self, filters: Optional[dict[str, Any]] = None) -> int:
        """统计文档数量

        Args:
            filters: 过滤条件

        Returns:
            int: 文档数量
        """
        items, _ = await self.list_all(skip=0, limit=999999, filters=filters)
        return len(items)