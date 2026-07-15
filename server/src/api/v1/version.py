#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本信息API
"""

from typing import Any
from fastapi import APIRouter, Request
from core.logger import logger
from core.config import settings
from core.response import success_response

router = APIRouter()


@router.get("/version")
async def get_version(request: Request) -> dict[str, Any]:
    """获取版本信息接口

    Args:
        request: 请求对象

    Returns:
        dict[str, Any]: 版本信息
    """
    request_id = getattr(request.state, "request_id", None)
    logger.info(f"Version requested: {request_id}")

    return success_response(
        data={
            "name": settings.app_name,
            "version": settings.app_version,
            "description": settings.app_description,
            "environment": settings.app_environment
        },
        request_id=request_id
    )