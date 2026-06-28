#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档处理API
"""

from typing import Any, Optional
from fastapi import APIRouter, Request, UploadFile, File, Form, HTTPException
from pydantic import BaseModel

from core.logger import logger
from core.exceptions import (
    ValidationError,
    DocumentError,
    NotFoundError,
    BusinessError
)
from core.response import success_response, error_response
from constants.constants import (
    DEFAULT_PAGE,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP
)
from core.schemas import PaginationParams

router = APIRouter()


class DocumentUploadResponse(BaseModel):
    """文档上传响应"""

    id: str
    name: str
    file_size: int
    file_type: str
    chunk_count: int
    created_at: str


class DocumentListResponse(BaseModel):
    """文档列表响应"""

    items: list[DocumentUploadResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


@router.post("/upload")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    chunk_size: int = Form(DEFAULT_CHUNK_SIZE),
    chunk_overlap: int = Form(DEFAULT_CHUNK_OVERLAP)
) -> dict[str, Any]:
    """上传文档接口

    Args:
        request: 请求对象
        file: 上传的文件
        chunk_size: 分块大小
        chunk_overlap: 分块重叠

    Returns:
        dict[str, Any]: 上传响应

    Raises:
        ValidationError: 参数校验失败
        DocumentError: 文档处理错误
    """
    request_id = getattr(request.state, "request_id", None)
    logger.info(f"Document upload requested: {request_id}, filename: {file.filename}")

    try:
        # 验证文件类型
        if not file.filename:
            raise ValidationError("Filename cannot be empty", request_id=request_id)

        file_extension = __import__("os").path.splitext(file.filename)[1].lower()
        supported_formats = [".txt", ".md", ".pdf", ".docx", ".doc"]

        if file_extension not in supported_formats:
            raise ValidationError(
                f"Unsupported file format: {file_extension}. Supported formats: {supported_formats}",
                request_id=request_id
            )

        # 读取文件内容
        content = await file.read()
        file_size = len(content)

        # 验证文件大小
        max_file_size = 10 * 1024 * 1024  # 10MB
        if file_size > max_file_size:
            raise ValidationError(
                f"File size exceeds maximum allowed size of {max_file_size} bytes",
                request_id=request_id
            )

        # 解码内容（简化处理，实际需要根据文件类型使用不同的解析器）
        try:
            text_content = content.decode("utf-8")
        except UnicodeDecodeError:
            raise ValidationError(
                "Failed to decode file content. Please ensure the file is UTF-8 encoded.",
                request_id=request_id
            )

        # 分块处理
        chunks = []
        if len(text_content) > chunk_size:
            start = 0
            chunk_index = 0
            while start < len(text_content):
                end = start + chunk_size
                chunk = text_content[start:end]
                if chunk.strip():
                    chunks.append({
                        "index": chunk_index,
                        "content": chunk.strip(),
                        "start_position": start,
                        "end_position": end
                    })
                    chunk_index += 1
                start = end - chunk_overlap
                if start >= len(text_content):
                    break
        else:
            chunks.append({
                "index": 0,
                "content": text_content.strip(),
                "start_position": 0,
                "end_position": len(text_content)
            })

        # 生成文档ID
        import uuid
        doc_id = str(uuid.uuid4())

        # 返回响应
        return success_response(
            data={
                "id": doc_id,
                "name": file.filename,
                "file_size": file_size,
                "file_type": file_extension[1:],  # 去掉点号
                "chunk_count": len(chunks),
                "created_at": __import__("datetime").datetime.utcnow().isoformat(),
                "chunks": chunks[:5]  # 只返回前5个分块作为示例
            },
            message="Document uploaded successfully",
            request_id=request_id
        )

    except ValidationError as e:
        logger.warning(f"Validation error in document upload: {e.message}")
        return error_response(message=e.message, code=e.code, request_id=request_id)
    except DocumentError as e:
        logger.error(f"Document error in upload: {e.message}")
        return error_response(message=e.message, code=e.code, request_id=request_id)
    except Exception as e:
        logger.error(f"Unexpected error in document upload: {e}", exc_info=True)
        return error_response(message="Internal server error", code=50001, request_id=request_id)


@router.get("/")
async def list_documents(
    request: Request,
    page: int = DEFAULT_PAGE,
    page_size: int = DEFAULT_PAGE_SIZE,
    file_type: Optional[str] = None
) -> dict[str, Any]:
    """获取文档列表接口

    Args:
        request: 请求对象
        page: 页码
        page_size: 每页记录数
        file_type: 文件类型过滤

    Returns:
        dict[str, Any]: 文档列表
    """
    request_id = getattr(request.state, "request_id", None)
    logger.info(f"List documents requested: {request_id}, page: {page}, page_size: {page_size}")

    try:
        # 验证分页参数
        if page < 1:
            page = DEFAULT_PAGE
        if page_size < 1 or page_size > MAX_PAGE_SIZE:
            page_size = DEFAULT_PAGE_SIZE

        # 模拟数据（实际项目从数据库查询）
        mock_documents = [
            {
                "id": f"doc-{i}",
                "name": f"example{i}.txt",
                "file_size": 1024 * i,
                "file_type": "txt",
                "chunk_count": i * 2,
                "created_at": "2024-01-01T00:00:00"
            }
            for i in range(1, 11)
        ]

        # 过滤
        if file_type:
            mock_documents = [doc for doc in mock_documents if doc["file_type"] == file_type]

        # 分页
        total = len(mock_documents)
        start = (page - 1) * page_size
        end = start + page_size
        items = mock_documents[start:end]
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0

        return success_response(
            data={
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            },
            request_id=request_id
        )

    except Exception as e:
        logger.error(f"Unexpected error in list documents: {e}", exc_info=True)
        return error_response(message="Internal server error", code=50001, request_id=request_id)


@router.get("/{document_id}")
async def get_document(request: Request, document_id: str) -> dict[str, Any]:
    """获取文档详情接口

    Args:
        request: 请求对象
        document_id: 文档ID

    Returns:
        dict[str, Any]: 文档详情

    Raises:
        NotFoundError: 文档未找到
    """
    request_id = getattr(request.state, "request_id", None)
    logger.info(f"Get document requested: {request_id}, document_id: {document_id}")

    try:
        # 模拟查询（实际项目从数据库查询）
        if document_id == "doc-1":
            return success_response(
                data={
                    "id": document_id,
                    "name": "example1.txt",
                    "content": "This is the content of example1.txt.",
                    "file_size": 1024,
                    "file_type": "txt",
                    "chunk_count": 2,
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T00:00:00"
                },
                request_id=request_id
            )
        else:
            raise NotFoundError(f"Document not found: {document_id}", request_id=request_id)

    except NotFoundError as e:
        logger.warning(f"Document not found: {e.message}")
        return error_response(message=e.message, code=e.code, request_id=request_id)
    except Exception as e:
        logger.error(f"Unexpected error in get document: {e}", exc_info=True)
        return error_response(message="Internal server error", code=50001, request_id=request_id)


@router.delete("/{document_id}")
async def delete_document(request: Request, document_id: str) -> dict[str, Any]:
    """删除文档接口

    Args:
        request: 请求对象
        document_id: 文档ID

    Returns:
        dict[str, Any]: 删除结果

    Raises:
        NotFoundError: 文档未找到
    """
    request_id = getattr(request.state, "request_id", None)
    logger.info(f"Delete document requested: {request_id}, document_id: {document_id}")

    try:
        # 模拟删除（实际项目从数据库删除）
        if document_id == "doc-1":
            return success_response(
                message="Document deleted successfully",
                request_id=request_id
            )
        else:
            raise NotFoundError(f"Document not found: {document_id}", request_id=request_id)

    except NotFoundError as e:
        logger.warning(f"Document not found: {e.message}")
        return error_response(message=e.message, code=e.code, request_id=request_id)
    except Exception as e:
        logger.error(f"Unexpected error in delete document: {e}", exc_info=True)
        return error_response(message="Internal server error", code=50001, request_id=request_id)