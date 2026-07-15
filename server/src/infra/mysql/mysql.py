# -*- coding: utf-8 -*-
"""
数据库连接管理

提供同步和异步的数据库连接。
"""

from typing import AsyncGenerator, Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from core.config import settings
from models.base import Base

# 获取数据库 URL
def _get_sync_url() -> str:
    """获取同步数据库 URL"""
    url = settings.database.url
    return url.replace("mysql+aiomysql", "mysql+pymysql")

def _get_async_url() -> str:
    """获取异步数据库 URL"""
    if settings.database.url_async:
        return settings.database.url_async
    url = settings.database.url
    return url.replace("mysql+pymysql", "mysql+aiomysql")

# 同步引擎
engine = create_engine(
    _get_sync_url(),
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.app_debug,
)

# 异步引擎
async_engine = create_async_engine(
    _get_async_url(),
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.app_debug,
)

# 同步会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    获取同步数据库会话（用于依赖注入）
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取异步数据库会话（用于依赖注入）
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def init_db() -> None:
    """
    初始化数据库表结构
    """
    Base.metadata.create_all(bind=engine)


async def async_init_db() -> None:
    """
    异步初始化数据库表结构
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
