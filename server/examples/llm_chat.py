#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM聊天示例
展示如何使用LLM服务进行聊天
"""

import asyncio
import httpx


async def chat_completion_example() -> None:
    """聊天完成示例"""
    base_url = "http://localhost:8000"

    async with httpx.AsyncClient() as client:
        # 健康检查
        response = await client.get(f"{base_url}/api/v1/health")
        print(f"Health check: {response.json()}")

        # 获取版本信息
        response = await client.get(f"{base_url}/api/v1/version")
        print(f"Version info: {response.json()}")

        # 获取可用提供商
        response = await client.get(f"{base_url}/api/v1/llm/providers")
        print(f"Available providers: {response.json()}")

        # 聊天完成
        chat_request = {
            "messages": [
                {"role": "user", "content": "你好，请介绍一下你自己"}
            ],
            "temperature": 0.7,
            "max_tokens": 200
        }

        response = await client.post(
            f"{base_url}/api/v1/llm/chat",
            json=chat_request
        )
        print(f"Chat completion: {response.json()}")


if __name__ == "__main__":
    asyncio.run(chat_completion_example())