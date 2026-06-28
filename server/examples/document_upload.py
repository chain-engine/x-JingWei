#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档上传示例
展示如何上传和处理文档
"""

import asyncio
import httpx
from pathlib import Path


async def document_upload_example() -> None:
    """文档上传示例"""
    base_url = "http://localhost:8000"

    async with httpx.AsyncClient() as client:
        # 创建示例文档
        example_file = Path("example.txt")
        if not example_file.exists():
            example_file.write_text(
                "这是一个示例文档。\n"
                "X-JingWei 经纬 是一个生产级 LLM 应用开发平台。\n"
                "它提供了完整的文档处理、向量检索和对话生成功能。\n"
                "通过这个项目，您可以学习如何构建现代化的 AI 应用。",
                encoding="utf-8"
            )

        # 上传文档
        with open(example_file, "rb") as f:
            files = {"file": ("example.txt", f, "text/plain")}
            data = {"chunk_size": 100, "chunk_overlap": 20}

            response = await client.post(
                f"{base_url}/api/v1/documents/upload",
                files=files,
                data=data
            )
            print(f"Upload result: {response.json()}")

        # 获取文档列表
        response = await client.get(f"{base_url}/api/v1/documents/")
        print(f"Document list: {response.json()}")

        # 获取文档详情
        doc_id = response.json()["data"]["items"][0]["id"]
        response = await client.get(f"{base_url}/api/v1/documents/{doc_id}")
        print(f"Document detail: {response.json()}")

        # 删除文档
        response = await client.delete(f"{base_url}/api/v1/documents/{doc_id}")
        print(f"Delete result: {response.json()}")

        # 清理示例文件
        example_file.unlink()


if __name__ == "__main__":
    asyncio.run(document_upload_example())