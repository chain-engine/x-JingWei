#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM Schema
"""

from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

from .base import BaseEntity


class Message(BaseModel):
    """消息模型"""

    role: str = Field(..., description="角色：system/user/assistant")
    content: str = Field(..., description="消息内容")
    name: Optional[str] = Field(default=None, description="发送者名称")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "role": "user",
                "content": "Hello, how are you?",
            }
        },
    }


class ChatCompletionRequest(BaseModel):
    """聊天完成请求"""

    messages: list[Message] = Field(..., description="消息列表")
    model: str = Field(..., description="模型名称")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="温度参数")
    max_tokens: int = Field(default=2000, ge=1, description="最大token数")
    stream: bool = Field(default=False, description="是否流式输出")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "messages": [{"role": "user", "content": "Hello, how are you?"}],
                "model": "deepseek-chat",
                "temperature": 0.7,
                "max_tokens": 2000,
                "stream": False,
            }
        },
    }


class ChatCompletionChoice(BaseModel):
    """聊天完成选项"""

    index: int = Field(description="选项索引")
    message: Message = Field(description="消息")
    finish_reason: Optional[str] = Field(default=None, description="结束原因")

    model_config = {"from_attributes": True}


class ChatCompletionUsage(BaseModel):
    """聊天完成使用量"""

    prompt_tokens: int = Field(description="提示词token数")
    completion_tokens: int = Field(description="完成token数")
    total_tokens: int = Field(description="总token数")

    model_config = {"from_attributes": True}


class ChatCompletionResponse(BaseModel):
    """聊天完成响应"""

    id: str = Field(description="响应ID")
    object: str = Field(default="chat.completion", description="对象类型")
    created: int = Field(description="创建时间戳")
    model: str = Field(description="模型名称")
    choices: list[ChatCompletionChoice] = Field(..., description="选项列表")
    usage: ChatCompletionUsage = Field(..., description="使用量")

    model_config = {"from_attributes": True}


class LLMConfig(BaseEntity):
    """LLM配置实体"""

    provider: str = Field(..., description="提供商：deepseek/doubao/aliyun")
    model_name: str = Field(..., description="模型名称")
    api_key: str = Field(..., description="API密钥")
    api_base: str = Field(..., description="API基础URL")
    is_default: bool = Field(default=False, description="是否为默认配置")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="温度参数")
    max_tokens: int = Field(default=2000, ge=1, description="最大token数")
    timeout: int = Field(default=60, ge=1, description="超时时间（秒）")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "llm-123",
                "provider": "deepseek",
                "model_name": "deepseek-chat",
                "api_key": "sk-***",
                "api_base": "https://api.deepseek.com/v1",
                "is_default": True,
                "temperature": 0.7,
                "max_tokens": 2000,
                "timeout": 60,
            }
        },
    }


class Conversation(BaseEntity):
    """对话实体"""

    title: Optional[str] = Field(default=None, description="对话标题")
    user_id: str = Field(..., description="用户ID")
    llm_config_id: str = Field(..., description="LLM配置ID")
    message_count: int = Field(default=0, description="消息数量")
    is_active: bool = Field(default=True, description="是否活跃")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "conv-123",
                "title": "Example Conversation",
                "user_id": "user-123",
                "llm_config_id": "llm-123",
                "message_count": 10,
                "is_active": True,
            }
        },
    }


class ConversationMessage(BaseEntity):
    """对话消息实体"""

    conversation_id: str = Field(..., description="对话ID")
    role: str = Field(..., description="角色：system/user/assistant")
    content: str = Field(..., description="消息内容")
    token_count: int = Field(default=0, description="token数量")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "msg-123",
                "conversation_id": "conv-123",
                "role": "user",
                "content": "Hello, how are you?",
                "token_count": 10,
            }
        },
    }