#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM相关API

API接口层：极薄，只做参数转发，不写业务逻辑
"""

from typing import Any
from fastapi import APIRouter, Request

from core.logger import logger
from core.response import success_response
from core.container import container
from service.llm_service import LLMService
from schemas.llm import Message

router = APIRouter()


@router.post("/chat")
async def chat_completion(request: Request) -> dict[str, Any]:
    """LLM聊天完成接口

    Args:
        request: 请求对象

    Returns:
        dict[str, Any]: 聊天响应
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

    return success_response(data=result, request_id=request_id)


@router.get("/providers")
async def list_providers(request: Request) -> dict[str, Any]:
    """获取可用LLM提供商列表

    Args:
        request: 请求对象

    Returns:
        dict[str, Any]: 提供商列表
    """
    request_id = getattr(request.state, "request_id", None)
    logger.info(f"List providers requested: {request_id}")

    llm_service = container.resolve(LLMService)
    providers = llm_service.list_providers()

    return success_response(data={"providers": providers}, request_id=request_id)