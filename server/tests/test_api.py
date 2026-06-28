#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API测试
"""

import pytest
from httpx import AsyncClient
from main import create_app


@pytest.mark.asyncio
class TestAPI:
    """API测试"""

    async def test_health_check(self) -> None:
        """测试健康检查接口"""
        app = create_app()
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/health")
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 0
            assert "data" in data
            assert data["data"]["status"] == "healthy"

    async def test_version_info(self) -> None:
        """测试版本信息接口"""
        app = create_app()
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/version")
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 0
            assert "data" in data
            assert data["data"]["name"] == "x-jingwei"
            assert data["data"]["version"]

    async def test_llm_providers(self) -> None:
        """测试LLM提供商列表接口"""
        app = create_app()
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/llm/providers")
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 0
            assert "data" in data
            assert "providers" in data["data"]
            assert isinstance(data["data"]["providers"], list)

    async def test_llm_chat(self) -> None:
        """测试LLM聊天接口"""
        app = create_app()
        async with AsyncClient(app=app, base_url="http://test") as client:
            request_data = {
                "messages": [{"role": "user", "content": "Hello"}],
                "temperature": 0.7,
                "max_tokens": 100
            }
            response = await client.post("/api/v1/llm/chat", json=request_data)
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 0
            assert "data" in data
            assert "choices" in data["data"]
            assert len(data["data"]["choices"]) > 0

    async def test_llm_chat_validation_error(self) -> None:
        """测试LLM聊天接口参数校验"""
        app = create_app()
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 空消息列表
            request_data = {
                "messages": [],
                "temperature": 0.7,
                "max_tokens": 100
            }
            response = await client.post("/api/v1/llm/chat", json=request_data)
            assert response.status_code == 400

    async def test_document_list(self) -> None:
        """测试文档列表接口"""
        app = create_app()
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/documents/")
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 0
            assert "data" in data
            assert "items" in data["data"]
            assert isinstance(data["data"]["items"], list)

    async def test_document_not_found(self) -> None:
        """测试文档未找到接口"""
        app = create_app()
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/documents/non-existent-id")
            assert response.status_code == 404
            data = response.json()
            assert data["code"] != 0

    async def test_document_list_pagination(self) -> None:
        """测试文档列表分页接口"""
        app = create_app()
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/documents/?page=1&page_size=5")
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 0
            assert "data" in data
            assert data["data"]["page"] == 1
            assert data["data"]["page_size"] == 5