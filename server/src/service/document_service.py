#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档处理服务
"""

from typing import Any, Optional, List, Dict
from pathlib import Path
import uuid
from datetime import datetime

from core.logger import logger
from core.exceptions import DocumentError, ValidationError, NotFoundError
from constants.constants import (
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_PAGE,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE
)


class DocumentService:
    """文档处理服务"""

    def __init__(self) -> None:
        """初始化文档服务"""
        self._documents: Dict[str, Dict[str, Any]] = {}
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
    ) -> List[Dict[str, Any]]:
        """分块文档

        Args:
            content: 文档内容
            chunk_size: 分块大小
            chunk_overlap: 分块重叠

        Returns:
            List[Dict[str, Any]]: 分块列表
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

    def _chunk_text(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """分块文本

        Args:
            text: 文本内容
            chunk_size: 分块大小
            overlap: 重叠大小

        Returns:
            List[str]: 分块列表
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

    def upload_document(
        self,
        filename: str,
        content: bytes,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP
    ) -> Dict[str, Any]:
        """上传文档

        Args:
            filename: 文件名
            content: 文件内容（字节）
            chunk_size: 分块大小
            chunk_overlap: 分块重叠

        Returns:
            Dict[str, Any]: 上传结果

        Raises:
            ValidationError: 参数校验失败
            DocumentError: 文档处理错误
        """
        if not filename:
            raise ValidationError("Filename cannot be empty")

        file_extension = Path(filename).suffix.lower()
        supported_formats = [".txt", ".md", ".pdf", ".docx", ".doc"]

        if file_extension not in supported_formats:
            raise ValidationError(
                f"Unsupported file format: {file_extension}. Supported formats: {supported_formats}"
            )

        file_size = len(content)
        max_file_size = 10 * 1024 * 1024
        if file_size > max_file_size:
            raise ValidationError(f"File size exceeds maximum allowed size of {max_file_size} bytes")

        try:
            text_content = content.decode("utf-8")
        except UnicodeDecodeError:
            raise ValidationError("Failed to decode file content. Please ensure the file is UTF-8 encoded.")

        chunks = self.chunk_document(text_content, chunk_size, chunk_overlap)

        doc_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()

        self._documents[doc_id] = {
            "id": doc_id,
            "name": filename,
            "file_size": file_size,
            "file_type": file_extension[1:],
            "chunk_count": len(chunks),
            "content": text_content,
            "chunks": chunks,
            "created_at": created_at,
            "updated_at": created_at
        }

        logger.info(f"Document uploaded: {doc_id}, name: {filename}, chunks: {len(chunks)}")

        return {
            "id": doc_id,
            "name": filename,
            "file_size": file_size,
            "file_type": file_extension[1:],
            "chunk_count": len(chunks),
            "created_at": created_at,
            "chunks": chunks[:5]
        }

    def list_documents(
        self,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
        file_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取文档列表

        Args:
            page: 页码
            page_size: 每页记录数
            file_type: 文件类型过滤

        Returns:
            Dict[str, Any]: 文档列表
        """
        if page < 1:
            page = DEFAULT_PAGE
        if page_size < 1 or page_size > MAX_PAGE_SIZE:
            page_size = DEFAULT_PAGE_SIZE

        documents = list(self._documents.values())

        if file_type:
            documents = [doc for doc in documents if doc["file_type"] == file_type]

        total = len(documents)
        start = (page - 1) * page_size
        end = start + page_size
        items = documents[start:end]
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0

        result_items = []
        for doc in items:
            result_items.append({
                "id": doc["id"],
                "name": doc["name"],
                "file_size": doc["file_size"],
                "file_type": doc["file_type"],
                "chunk_count": doc["chunk_count"],
                "created_at": doc["created_at"]
            })

        return {
            "items": result_items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }

    def get_document(self, document_id: str) -> Dict[str, Any]:
        """获取文档详情

        Args:
            document_id: 文档ID

        Returns:
            Dict[str, Any]: 文档详情

        Raises:
            NotFoundError: 文档未找到
        """
        if document_id not in self._documents:
            raise NotFoundError(f"Document not found: {document_id}")

        doc = self._documents[document_id]

        return {
            "id": doc["id"],
            "name": doc["name"],
            "content": doc["content"],
            "file_size": doc["file_size"],
            "file_type": doc["file_type"],
            "chunk_count": doc["chunk_count"],
            "created_at": doc["created_at"],
            "updated_at": doc["updated_at"]
        }

    def delete_document(self, document_id: str) -> None:
        """删除文档

        Args:
            document_id: 文档ID

        Raises:
            NotFoundError: 文档未找到
        """
        if document_id not in self._documents:
            raise NotFoundError(f"Document not found: {document_id}")

        del self._documents[document_id]
        logger.info(f"Document deleted: {document_id}")