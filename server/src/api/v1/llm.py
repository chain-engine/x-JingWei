#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM相关API

API接口层：极薄，只做参数转发，不写业务逻辑
"""

from typing import Any

from fastapi import APIRouter, Request

from core.logger import logger
from core.container import container
from services.llm_service import LLMService
from schemas.common import ApiResponse
from schemas.llm import Message

router = APIRouter()


@router.post("/chat", response_model=ApiResponse[dict[str, Any]])
async def chat_completion(request: Request) -> ApiResponse[dict[str, Any]]:
    """LLM聊天完成接口

    Args:
        request: 请求对象

    Returns:
        ApiResponse: 聊天响应
    """
    request_id = getattr(request.state, "request_id", None)
    logger.info(f"Chat completion requested: {request_id}")

    body = await request.json()
    messages = [Message(**msg) for msg in body.get("messages", [])]

    llm_service = container.resolve(LLMService)
    result = await llm_service.chat_completion(
        messages=messages,
        provider=body.get("provider"),
        model=body.get("model"),
        temperature=body.get("temperature"),
        max_tokens=body.get("max_tokens")
    )

    return ApiResponse(
        code=0,
        message="",
        data=result,
        request_id=request_id
    )


@router.get("/providers", response_model=ApiResponse[dict[str, Any]])
async def list_providers(request: Request) -> ApiResponse[dict[str, Any]]:
    """获取可用LLM提供商列表

    Args:
        request: 请求对象

    Returns:
        ApiResponse: 提供商列表
    """
    request_id = getattr(request.state, "request_id", None)
    logger.info(f"List providers requested: {request_id}")

    llm_service = container.resolve(LLMService)
    providers = llm_service.list_providers()

    return ApiResponse(
        code=0,
        message="",
        data={"providers": providers},
        request_id=request_id
    )
