#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API路由管理
"""

from fastapi import APIRouter
from constants.constants import API_V1_PREFIX

# 创建主路由器
api_router = APIRouter()

# 导入子路由
from .v1 import health, version, llm, document, workflow

# 注册子路由
api_router.include_router(health.router, prefix=API_V1_PREFIX, tags=["health"])
api_router.include_router(version.router, prefix=API_V1_PREFIX, tags=["version"])
api_router.include_router(llm.router, prefix=f"{API_V1_PREFIX}/llm", tags=["llm"])
api_router.include_router(document.router, prefix=f"{API_V1_PREFIX}/documents", tags=["documents"])
api_router.include_router(workflow.router, prefix=f"{API_V1_PREFIX}/workflows", tags=["workflow"])


__all__ = ["api_router"]