#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档处理服务
"""

from typing import Any
from pathlib import Path

from core.logger import logger
from core.exceptions import DocumentError
from constants.constants import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP


class DocumentService:
    """文档处理服务"""

    def __init__(self) -> None:
        """初始化文档服务"""
        logger.info("Document service initialized")

    def parse_file(self, file_path: str) -> str:
        """解析文件内容

        Args:
            file_path: 文件路径

        Returns:
            str: 文件内容

        Raises:
            DocumentError: 文档处理错误
        """
        path = Path(file_path)

        if not path.exists():
            raise DocumentError(f"File not found: {file_path}")

        file_extension = path.suffix.lower()

        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except UnicodeDecodeError:
            # 尝试其他编码
            try:
                with open(path, 'r', encoding='gbk') as f:
                    content = f.read()
                return content
            except Exception as e:
                raise DocumentError(f"Failed to decode file: {e}")
        except Exception as e:
            raise DocumentError(f"Failed to read file: {e}")

    def chunk_document(
        self,
        content: str,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP
    ) -> list[dict[str, Any]]:
        """分块文档

        Args:
            content: 文档内容
            chunk_size: 分块大小
            chunk_overlap: 分块重叠

        Returns:
            list[dict[str, Any]]: 分块列表
        """
        chunks_text = self._chunk_text(content, chunk_size, chunk_overlap)

        chunks = []
        for index, chunk_text in enumerate(chunks_text):
            chunks.append({
                "index": index,
                "content": chunk_text,
                "token_count": len(chunk_text.split())
            })

        logger.info(f"Document chunked into {len(chunks)} chunks")
        return chunks

    def validate_file_type(self, file_name: str) -> bool:
        """验证文件类型

        Args:
            file_name: 文件名

        Returns:
            bool: 是否有效
        """
        supported_formats = [".txt", ".md", ".pdf", ".docx", ".doc"]
        file_extension = Path(file_name).suffix.lower()
        return file_extension in supported_formats

    def validate_file_size(self, file_size: int, max_size: int = 10 * 1024 * 1024) -> bool:
        """验证文件大小

        Args:
            file_size: 文件大小
            max_size: 最大文件大小

        Returns:
            bool: 是否有效
        """
        return file_size <= max_size

    def _chunk_text(self, text: str, chunk_size: int, overlap: int) -> list[str]:
        """分块文本

        Args:
            text: 文本内容
            chunk_size: 分块大小
            overlap: 重叠大小

        Returns:
            list[str]: 分块列表
        """
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            if chunk.strip():
                chunks.append(chunk.strip())
            start = end - overlap
            if start >= len(text):
                break
        return chunks