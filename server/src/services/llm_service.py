#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM服务
"""

from typing import Any, Optional
from abc import ABC, abstractmethod

from core.logger import logger
from core.config import settings
from core.exceptions import ExternalServiceError, GenerationError
from schemas.llm import ChatCompletionRequest, Message


class LLMProvider(ABC):
    """LLM提供商抽象基类"""

    @abstractmethod
    async def chat_completion(self, request: ChatCompletionRequest) -> dict[str, Any]:
        """聊天完成

        Args:
            request: 聊天请求

        Returns:
            dict[str, Any]: 聊天响应

        Raises:
            ExternalServiceError: 外部服务错误
            GenerationError: 生成错误
        """
        pass

    @abstractmethod
    async def stream_chat_completion(self, request: ChatCompletionRequest):
        """流式聊天完成

        Args:
            request: 聊天请求

        Yields:
            dict[str, Any]: 聊天响应片段

        Raises:
            ExternalServiceError: 外部服务错误
            GenerationError: 生成错误
        """
        pass


class DeepSeekProvider(LLMProvider):
    """DeepSeek提供商"""

    def __init__(self, api_key: str, api_base: str) -> None:
        """初始化DeepSeek提供商

        Args:
            api_key: API密钥
            api_base: API基础URL
        """
        self.api_key = api_key
        self.api_base = api_base
        logger.info("DeepSeek provider initialized")

    async def chat_completion(self, request: ChatCompletionRequest) -> dict[str, Any]:
        """聊天完成

        Args:
            request: 聊天请求

        Returns:
            dict[str, Any]: 聊天响应
        """
        logger.info(f"DeepSeek chat completion requested: {request.model}")

        # 实际项目中，这里会调用DeepSeek API
        # 这里返回模拟数据
        return {
            "id": "chatcmpl-deepseek-mock",
            "object": "chat.completion",
            "created": __import__("time").time(),
            "model": request.model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "This is a simulated response from DeepSeek."
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": sum(len(msg.content.split()) for msg in request.messages),
                "completion_tokens": 10,
                "total_tokens": sum(len(msg.content.split()) for msg in request.messages) + 10
            }
        }

    async def stream_chat_completion(self, request: ChatCompletionRequest):
        """流式聊天完成

        Args:
            request: 聊天请求

        Yields:
            dict[str, Any]: 聊天响应片段
        """
        logger.info(f"DeepSeek stream chat completion requested: {request.model}")

        # 实际项目中，这里会流式调用DeepSeek API
        # 这里返回模拟数据
        yield {
            "id": "chatcmpl-deepseek-stream-mock",
            "object": "chat.completion.chunk",
            "created": __import__("time").time(),
            "model": request.model,
            "choices": [
                {
                    "index": 0,
                    "delta": {"content": "This "},
                    "finish_reason": None
                }
            ]
        }
        yield {
            "id": "chatcmpl-deepseek-stream-mock",
            "object": "chat.completion.chunk",
            "created": __import__("time").time(),
            "model": request.model,
            "choices": [
                {
                    "index": 0,
                    "delta": {"content": "is "},
                    "finish_reason": None
                }
            ]
        }
        yield {
            "id": "chatcmpl-deepseek-stream-mock",
            "object": "chat.completion.chunk",
            "created": __import__("time").time(),
            "model": request.model,
            "choices": [
                {
                    "index": 0,
                    "delta": {"content": "a "},
                    "finish_reason": None
                }
            ]
        }
        yield {
            "id": "chatcmpl-deepseek-stream-mock",
            "object": "chat.completion.chunk",
            "created": __import__("time").time(),
            "model": request.model,
            "choices": [
                {
                    "index": 0,
                    "delta": {"content": "streamed "},
                    "finish_reason": None
                }
            ]
        }
        yield {
            "id": "chatcmpl-deepseek-stream-mock",
            "object": "chat.completion.chunk",
            "created": __import__("time").time(),
            "model": request.model,
            "choices": [
                {
                    "index": 0,
                    "delta": {"content": "response."},
                    "finish_reason": "stop"
                }
            ]
        }


class LLMService:
    """LLM服务"""

    def __init__(self) -> None:
        """初始化LLM服务"""
        self.providers: dict[str, LLMProvider] = {}
        self._init_providers()

    def _init_providers(self) -> None:
        """初始化提供商"""
        for provider_name, config in settings.llm.providers.items():
            if provider_name == "deepseek":
                self.providers[provider_name] = DeepSeekProvider(
                    api_key=config.api_key,
                    api_base=config.api_base
                )
            elif provider_name == "doubao":
                # TODO: 实现Doubao提供商
                pass
            elif provider_name == "aliyun":
                # TODO: 实现Aliyun提供商
                pass

        logger.info(f"Initialized {len(self.providers)} LLM providers")

    def list_providers(self) -> list[dict[str, Any]]:
        """获取可用LLM提供商列表

        Returns:
            list[dict[str, Any]]: 提供商列表
        """
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
        return providers

    def get_provider(self, provider_name: Optional[str] = None) -> LLMProvider:
        """获取提供商

        Args:
            provider_name: 提供商名称

        Returns:
            LLMProvider: 提供商实例

        Raises:
            ValueError: 提供商不存在
        """
        if provider_name is None:
            provider_name = settings.llm.default_provider

        if provider_name not in self.providers:
            raise ValueError(f"Provider '{provider_name}' not found")

        return self.providers[provider_name]

    async def chat_completion(
        self,
        messages: list[Message],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> dict[str, Any]:
        """聊天完成

        Args:
            messages: 消息列表
            provider: 提供商名称
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数

        Returns:
            dict[str, Any]: 聊天响应

        Raises:
            ExternalServiceError: 外部服务错误
            GenerationError: 生成错误
        """
        provider_instance = self.get_provider(provider)

        # 如果没有指定模型，使用配置中的模型
        if model is None:
            provider_name = provider or settings.llm.default_provider
            if provider_name in settings.llm.providers:
                model = settings.llm.providers[provider_name].model_name
            else:
                model = "default"

        # 如果没有指定温度和最大token数，使用默认值
        if temperature is None:
            temperature = settings.llm.temperature
        if max_tokens is None:
            max_tokens = settings.llm.max_tokens

        request = ChatCompletionRequest(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False
        )

        return await provider_instance.chat_completion(request)

    async def stream_chat_completion(
        self,
        messages: list[Message],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ):
        """流式聊天完成

        Args:
            messages: 消息列表
            provider: 提供商名称
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数

        Yields:
            dict[str, Any]: 聊天响应片段

        Raises:
            ExternalServiceError: 外部服务错误
            GenerationError: 生成错误
        """
        provider_instance = self.get_provider(provider)

        if model is None:
            provider_name = provider or settings.llm.default_provider
            if provider_name in settings.llm.providers:
                model = settings.llm.providers[provider_name].model_name
            else:
                model = "default"

        if temperature is None:
            temperature = settings.llm.temperature
        if max_tokens is None:
            max_tokens = settings.llm.max_tokens

        request = ChatCompletionRequest(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )

        async for chunk in provider_instance.stream_chat_completion(request):
            yield chunk