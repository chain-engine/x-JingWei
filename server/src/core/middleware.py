#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中间件模块
实现CORS、限流、请求ID追踪等中间件
"""

import uuid
from typing import Callable
from functools import wraps
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from core.logger import logger
from core.config import settings
from core.exceptions import RateLimitError
from constants.constants import HEADER_REQUEST_ID


# 限流器实例
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.rate_limit.requests_per_minute}/minute",
                   f"{settings.rate_limit.requests_per_hour}/hour"]
)


async def request_id_middleware(request: Request, call_next: Callable) -> Response:
    """请求ID中间件

    为每个请求生成唯一的请求ID，并添加到响应头中

    Args:
        request: 请求对象
        call_next: 下一个中间件或路由处理器

    Returns:
        Response: 响应对象
    """
    request_id: str = request.headers.get(HEADER_REQUEST_ID) or str(uuid.uuid4())
    request.state.request_id = request_id

    response: Response = await call_next(request)
    response.headers[HEADER_REQUEST_ID] = request_id

    logger.info(f"Request {request_id}: {request.method} {request.url.path}")

    return response


async def error_handler_middleware(request: Request, call_next: Callable) -> Response:
    """错误处理中间件（兜底）

    作为异常处理的最后一道防线，只处理未被专门异常处理器捕获的异常

    Args:
        request: 请求对象
        call_next: 下一个中间件或路由处理器

    Returns:
        Response: 响应对象
    """
    try:
        return await call_next(request)
    except Exception as e:
        logger.opt(exception=True).error(
            f"Unhandled exception for request {getattr(request.state, 'request_id', 'unknown')}: {e}"
        )
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": "Internal server error",
                "detail": str(e),
                "request_id": getattr(request.state, "request_id", None)
            }
        )


async def logging_middleware(request: Request, call_next: Callable) -> Response:
    """日志中间件

    记录请求和响应的详细信息

    Args:
        request: 请求对象
        call_next: 下一个中间件或路由处理器

    Returns:
        Response: 响应对象
    """
    start_time: float = request.state.start_time if hasattr(request.state, "start_time") else 0.0
    request.state.start_time = start_time

    response: Response = await call_next(request)

    process_time: float = (request.state.start_time - start_time) * 1000
    logger.info(
        f"Request {getattr(request.state, 'request_id', 'unknown')} "
        f"completed in {process_time:.2f}ms "
        f"with status {response.status_code}"
    )

    return response


def get_cors_middleware_origins() -> list[str]:
    """获取CORS允许的来源

    Returns:
        list[str]: 允许的来源列表
    """
    cors_origins: str = settings.cors.allow_origins
    if cors_origins == "*":
        return ["*"]
    return [origin.strip() for origin in cors_origins.split(",")]


def setup_cors_middleware(app: FastAPI) -> None:
    """配置CORS中间件

    Args:
        app: FastAPI应用实例
    """
    if not settings.cors.enabled:
        return

    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_cors_middleware_origins(),      # 允许跨域请求的来源列表
        allow_credentials=settings.cors.allow_credentials,  # 是否允许携带凭证（Cookie等）
        allow_methods=settings.cors.allow_methods,          # 允许的HTTP方法列表
        allow_headers=settings.cors.allow_headers,          # 允许的请求头列表
    )


def setup_middleware(app: FastAPI) -> None:
    """配置所有中间件

    Args:
        app: FastAPI应用实例
    """
    # CORS中间件
    setup_cors_middleware(app)

    # 请求ID中间件
    app.middleware("http")(request_id_middleware)

    # 错误处理中间件
    app.middleware("http")(error_handler_middleware)

    # 日志中间件
    app.middleware("http")(logging_middleware)