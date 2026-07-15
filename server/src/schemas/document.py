#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档 Schema
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

from .base import BaseEntity


class DocumentMetadata(BaseModel):
    """文档元数据"""

    source: Optional[str] = Field(default=None, description="文档来源")
    author: Optional[str] = Field(default=None, description="作者")
    created_at: Optional[datetime] = Field(default=None, description="原始创建时间")
    language: Optional[str] = Field(default="zh", description="语言")
    tags: list[str] = Field(default_factory=list, description="标签")

    model_config = {"from_attributes": True}


class DocumentChunk(BaseModel):
    """文档分块"""

    id: str = Field(description="分块ID")
    document_id: str = Field(description="文档ID")
    content: str = Field(description="分块内容")
    embedding: Optional[list[float]] = Field(default=None, description="向量嵌入")
    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata, description="元数据")
    chunk_index: int = Field(description="分块索引")
    start_position: int = Field(default=0, description="起始位置")
    end_position: int = Field(description="结束位置")

    model_config = {"from_attributes": True}


class Document(BaseEntity):
    """文档实体"""

    name: str = Field(..., description="文档名称")
    content: str = Field(..., description="文档内容")
    file_path: Optional[str] = Field(default=None, description="文件路径")
    file_size: int = Field(default=0, description="文件大小（字节）")
    file_type: str = Field(..., description="文件类型")
    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata, description="元数据")
    chunk_count: int = Field(default=0, description="分块数量")
    is_indexed: bool = Field(default=False, description="是否已索引")
    owner_id: Optional[str] = Field(default=None, description="所有者ID")

    @field_validator("file_size")
    @classmethod
    def validate_file_size(cls, v: int) -> int:
        """验证文件大小"""
        if v < 0:
            raise ValueError("File size cannot be negative")
        return v

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "doc-123",
                "name": "example.txt",
                "content": "This is example content.",
                "file_path": "/path/to/file.txt",
                "file_size": 1024,
                "file_type": "txt",
                "metadata": {},
                "chunk_count": 5,
                "is_indexed": False,
                "owner_id": "user-123",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        },
    }


class KnowledgeBase(BaseEntity):
    """知识库实体"""

    name: str = Field(..., description="知识库名称")
    description: Optional[str] = Field(default=None, description="知识库描述")
    embedding_model: str = Field(default="text-embedding-ada-002", description="嵌入模型")
    chunk_size: int = Field(default=500, description="分块大小")
    chunk_overlap: int = Field(default=50, description="分块重叠")
    document_count: int = Field(default=0, description="文档数量")
    owner_id: str = Field(..., description="所有者ID")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "kb-123",
                "name": "Example Knowledge Base",
                "description": "An example knowledge base",
                "embedding_model": "text-embedding-ada-002",
                "chunk_size": 500,
                "chunk_overlap": 50,
                "document_count": 10,
                "owner_id": "user-123",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        },
    }