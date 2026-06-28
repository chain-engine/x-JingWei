#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM相关API
"""

from typing import Any
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel

from core.logger import logger
from core.config import settings
from core.exceptions import (
    BusinessError,
    ValidationError,
    ExternalServiceError,
    GenerationError
)
from core.response import success_response, error_response
from constants.constants import (
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TIMEOUT
)
from models.llm import ChatCompletionRequest, Message

router = APIRouter()


class LLMChatRequest(BaseModel):
    """LLM聊天请求"""

    messages: list[Message]
    provider: str = None
    model: str = None
    temperature: float = DEFAULT_TEMPERATURE
    max_tokens: int = DEFAULT_MAX_TOKENS
    stream: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "messages": [
                    {"role": "user", "content": "Hello, how are you?"}
                ],
                "temperature": 0.7,
                "max_tokens": 2000,
                "stream": False
            }
        }


@router.post("/chat")
async def chat_completion(request: Request, chat_request: LLMChatRequest) -> dict[str, Any]:
    """LLM聊天完成接口

    Args:
        request: 请求对象
        chat_request: 聊天请求

    Returns:
        dict[str, Any]: 聊天响应

    Raises:
        ValidationError: 参数校验失败
        BusinessError: 业务错误
        ExternalServiceError: 外部服务错误
        GenerationError: 生成错误
    """
    request_id = getattr(request.state, "request_id", None)
    logger.info(f"Chat completion requested: {request_id}")

    try:
        # 验证请求参数
        if not chat_request.messages:
            raise ValidationError("Messages cannot be empty", request_id=request_id)

        # 获取LLM提供商配置
        provider = chat_request.provider or settings.llm.default_provider
        if provider not in settings.llm.providers:
            available_providers = list(settings.llm.providers.keys())
            raise ValidationError(
                f"Provider '{provider}' not available. Available providers: {available_providers}",
                request_id=request_id
            )

        provider_config = settings.llm.providers[provider]

        # 构建请求
        completion_request = ChatCompletionRequest(
            messages=chat_request.messages,
            model=chat_request.model or provider_config.model_name,
            temperature=chat_request.temperature,
            max_tokens=chat_request.max_tokens,
            stream=chat_request.stream
        )

        # 模拟LLM调用（实际项目中替换为真实调用）
        logger.info(f"Calling LLM provider: {provider}, model: {completion_request.model}")

        response_content = "This is a simulated response from the LLM service."

        return success_response(
            data={
                "id": f"chatcmpl-{request_id}",
                "object": "chat.completion",
                "created": __import__("time").time(),
                "model": completion_request.model,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": response_content
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": sum(len(msg.content.split()) for msg in chat_request.messages),
                    "completion_tokens": len(response_content.split()),
                    "total_tokens": sum(len(msg.content.split()) for msg in chat_request.messages) + len(response_content.split())
                },
                "provider": provider
            },
            request_id=request_id
        )

    except ValidationError as e:
        logger.warning(f"Validation error in chat completion: {e.message}")
        return error_response(message=e.message, code=e.code, request_id=request_id)
    except BusinessError as e:
        logger.warning(f"Business error in chat completion: {e.message}")
        return error_response(message=e.message, code=e.code, request_id=request_id)
    except ExternalServiceError as e:
        logger.error(f"External service error in chat completion: {e.message}")
        return error_response(message=e.message, code=e.code, request_id=request_id)
    except GenerationError as e:
        logger.error(f"Generation error in chat completion: {e.message}")
        return error_response(message=e.message, code=e.code, request_id=request_id)
    except Exception as e:
        logger.error(f"Unexpected error in chat completion: {e}", exc_info=True)
        return error_response(message="Internal server error", code=50001, request_id=request_id)


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

    providers = []
    for provider_name, config in settings.llm.providers.items():
        providers.append({
            "name": provider_name,
            "model_name": config.model_name,
            "is_default": provider_name == settings.llm.default_provider,
            "temperature_range": [0.0, 2.0],
            "max_tokens": settings.llm.max_tokens,
            "timeout": settings.llm.timeout
        })

    return success_response(data={"providers": providers}, request_id=request_id)