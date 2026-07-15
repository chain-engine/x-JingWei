#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本信息API
"""

from typing import Any

from fastapi import APIRouter, Request

from core.logger import logger
from core.config import settings
from schemas.common import ApiResponse

router = APIRouter()


@router.get("/version", response_model=ApiResponse[dict[str, Any]])
async def get_version(request: Request) -> ApiResponse[dict[str, Any]]:
    """获取版本信息接口

    Args:
        request: 请求对象

    Returns:
        ApiResponse: 版本信息
    """
    request_id = getattr(request.state, "request_id", None)
    logger.info(f"Version requested: {request_id}")

    return ApiResponse(
        code=0,
        message="",
        data={
            "name": settings.app_name,
            "version": settings.app_version,
            "description": settings.app_description,
            "environment": settings.app_environment
        },
        request_id=request_id
    )
