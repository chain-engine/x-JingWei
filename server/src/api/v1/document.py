#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档处理API

API接口层：极薄，只做参数转发，不写业务逻辑
"""

from typing import Any, Optional

from fastapi import APIRouter, Request, UploadFile, File, Form

from core.logger import logger
from core.container import container
from services.document_service import DocumentService
from schemas.common import ApiResponse
from constants.constants import (
    DEFAULT_PAGE,
    DEFAULT_PAGE_SIZE,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP
)

router = APIRouter()


@router.post("/upload", response_model=ApiResponse[dict[str, Any]])
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    chunk_size: int = Form(DEFAULT_CHUNK_SIZE),
    chunk_overlap: int = Form(DEFAULT_CHUNK_OVERLAP)
) -> ApiResponse[dict[str, Any]]:
    """上传文档接口

    Args:
        request: 请求对象
        file: 上传的文件
        chunk_size: 分块大小
        chunk_overlap: 分块重叠

    Returns:
        ApiResponse: 上传响应
    """
    request_id = getattr(request.state, "request_id", None)
    logger.info(f"Document upload requested: {request_id}, filename: {file.filename}")

    content = await file.read()

    document_service = container.resolve(DocumentService)
    result = document_service.upload_document(
        filename=file.filename,
        content=content,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    return ApiResponse(
        code=0,
        message="Document uploaded successfully",
        data=result,
        request_id=request_id
    )


@router.get("", response_model=ApiResponse[dict[str, Any]])
async def list_documents(
    request: Request,
    page: int = DEFAULT_PAGE,
    page_size: int = DEFAULT_PAGE_SIZE,
    file_type: Optional[str] = None
) -> ApiResponse[dict[str, Any]]:
    """获取文档列表接口

    Args:
        request: 请求对象
        page: 页码
        page_size: 每页记录数
        file_type: 文件类型过滤

    Returns:
        ApiResponse: 文档列表
    """
    request_id = getattr(request.state, "request_id", None)
    logger.info(f"List documents requested: {request_id}, page: {page}, page_size: {page_size}")

    document_service = container.resolve(DocumentService)
    result = document_service.list_documents(page=page, page_size=page_size, file_type=file_type)

    return ApiResponse(
        code=0,
        message="",
        data=result,
        request_id=request_id
    )


@router.get("/{document_id}", response_model=ApiResponse[dict[str, Any]])
async def get_document(request: Request, document_id: str) -> ApiResponse[dict[str, Any]]:
    """获取文档详情接口

    Args:
        request: 请求对象
        document_id: 文档ID

    Returns:
        ApiResponse: 文档详情
    """
    request_id = getattr(request.state, "request_id", None)
    logger.info(f"Get document requested: {request_id}, document_id: {document_id}")

    document_service = container.resolve(DocumentService)
    result = document_service.get_document(document_id=document_id)

    return ApiResponse(
        code=0,
        message="",
        data=result,
        request_id=request_id
    )


@router.delete("/{document_id}", response_model=ApiResponse[dict[str, Any]])
async def delete_document(request: Request, document_id: str) -> ApiResponse[dict[str, Any]]:
    """删除文档接口

    Args:
        request: 请求对象
        document_id: 文档ID

    Returns:
        ApiResponse: 删除结果
    """
    request_id = getattr(request.state, "request_id", None)
    logger.info(f"Delete document requested: {request_id}, document_id: {document_id}")

    document_service = container.resolve(DocumentService)
    document_service.delete_document(document_id=document_id)

    return ApiResponse(
        code=0,
        message="Document deleted successfully",
        data=None,
        request_id=request_id
    )
