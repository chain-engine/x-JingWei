#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
健康检查API
"""

from typing import Any
from fastapi import APIRouter, Request
from core.logger import logger
from core.config import settings
from core.response import success_response
from core.schemas import HealthCheckResponse

router = APIRouter()


@router.get("/health")
async def health_check(request: Request) -> dict[str, Any]:
    """健康检查接口

    Args:
        request: 请求对象

    Returns:
        dict[str, Any]: 健康检查结果
    """
    request_id = getattr(request.state, "request_id", None)
    logger.info(f"Health check requested: {request_id}")

    return success_response(
        data={
            "status": "healthy",
            "version": settings.app_version,
            "timestamp": __import__("datetime").datetime.utcnow().isoformat()
        },
        request_id=request_id
    )