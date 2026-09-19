#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API路由管理
"""

from fastapi import APIRouter
from constants.constants import API_V1_PREFIX

# 创建主路由器
api_router = APIRouter()

from .v1 import health, version, llm, document, workflow

# 注册健康检查路由
api_router.include_router(health.router, prefix=API_V1_PREFIX, tags=["健康检查"])

# 注册版本管理路由
api_router.include_router(version.router, prefix=API_V1_PREFIX, tags=["版本管理"])

# 注册大模型路由
api_router.include_router(llm.router, prefix=f"{API_V1_PREFIX}/llm", tags=["大模型管理"])

# 注册文档管理路由
api_router.include_router(document.router, prefix=f"{API_V1_PREFIX}/documents", tags=["文档管理"])

# 注册工作流管理路由
api_router.include_router(workflow.router, prefix=f"{API_V1_PREFIX}/workflows", tags=["工作流管理"])


__all__ = ["api_router"]