#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖注入示例
展示如何使用依赖注入容器
"""

from core.container import container, singleton, inject
from core.logger import logger


@singleton
class DatabaseService:
    """数据库服务"""

    def __init__(self) -> None:
        self.connection = "mock_connection"

    def query(self, sql: str) -> list[dict]:
        """查询数据库"""
        logger.info(f"Executing query: {sql}")
        return [{"id": 1, "name": "example"}]


@singleton
class CacheService:
    """缓存服务"""

    def __init__(self) -> None:
        self.cache = {}

    def get(self, key: str) -> str | None:
        """获取缓存"""
        return self.cache.get(key)

    def set(self, key: str, value: str) -> None:
        """设置缓存"""
        self.cache[key] = value


@singleton
class UserService:
    """用户服务"""

    def __init__(self, db_service: DatabaseService, cache_service: CacheService) -> None:
        self.db = db_service
        self.cache = cache_service

    def get_user(self, user_id: int) -> dict | None:
        """获取用户"""
        # 先从缓存获取
        cache_key = f"user:{user_id}"
        cached = self.cache.get(cache_key)
        if cached:
            logger.info(f"User {user_id} found in cache")
            return {"id": user_id, "name": cached}

        # 从数据库获取
        users = self.db.query(f"SELECT * FROM users WHERE id = {user_id}")
        if users:
            user = users[0]
            self.cache.set(cache_key, user["name"])
            return user

        return None


def dependency_injection_example() -> None:
    """依赖注入示例"""
    # 使用自动注入
    user_service = container.resolve(UserService)

    # 调用服务
    user = user_service.get_user(1)
    logger.info(f"User: {user}")


if __name__ == "__main__":
    dependency_injection_example()