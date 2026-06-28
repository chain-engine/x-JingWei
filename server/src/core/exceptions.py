#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全局异常定义
定义业务异常和系统异常基类
"""

from typing import Any
from core.logger import logger


class BaseException(Exception):
    """异常基类"""

    def __init__(
        self,
        message: str,
        code: int = 500,
        detail: str | None = None
    ) -> None:
        self.message: str = message
        self.code: int = code
        self.detail: str | None = detail
        super().__init__(self.message)


class BusinessError(BaseException):
    """业务异常"""

    def __init__(self, message: str, code: int = 400, detail: str | None = None) -> None:
        super().__init__(message, code, detail)
        logger.warning(f"BusinessError: {message}")


class SystemError(BaseException):
    """系统异常"""

    def __init__(self, message: str, code: int = 500, detail: str | None = None) -> None:
        super().__init__(message, code, detail)
        logger.error(f"SystemError: {message}")


class NotFoundError(BusinessError):
    """资源未找到异常"""

    def __init__(self, message: str = "Resource not found", detail: str | None = None) -> None:
        super().__init__(message, 404, detail)


class ValidationError(BusinessError):
    """参数校验异常"""

    def __init__(self, message: str = "Validation failed", detail: str | None = None) -> None:
        super().__init__(message, 400, detail)


class UnauthorizedError(BusinessError):
    """未授权异常"""

    def __init__(self, message: str = "Unauthorized", detail: str | None = None) -> None:
        super().__init__(message, 401, detail)


class ForbiddenError(BusinessError):
    """禁止访问异常"""

    def __init__(self, message: str = "Forbidden", detail: str | None = None) -> None:
        super().__init__(message, 403, detail)


class ConflictError(BusinessError):
    """资源冲突异常"""

    def __init__(self, message: str = "Resource conflict", detail: str | None = None) -> None:
        super().__init__(message, 409, detail)


class RateLimitError(BusinessError):
    """限流异常"""

    def __init__(self, message: str = "Rate limit exceeded", detail: str | None = None) -> None:
        super().__init__(message, 429, detail)


class DocumentError(BusinessError):
    """文档处理异常"""

    def __init__(self, message: str = "Document processing failed", detail: str | None = None) -> None:
        super().__init__(message, 400, detail)


class EmbeddingError(SystemError):
    """向量化异常"""

    def __init__(self, message: str = "Embedding generation failed", detail: str | None = None) -> None:
        super().__init__(message, 500, detail)


class VectorStoreError(SystemError):
    """向量存储异常"""

    def __init__(self, message: str = "Vector store operation failed", detail: str | None = None) -> None:
        super().__init__(message, 500, detail)


class RetrievalError(SystemError):
    """检索异常"""

    def __init__(self, message: str = "Retrieval failed", detail: str | None = None) -> None:
        super().__init__(message, 500, detail)


class GenerationError(SystemError):
    """生成异常"""

    def __init__(self, message: str = "Generation failed", detail: str | None = None) -> None:
        super().__init__(message, 500, detail)


class DatabaseError(SystemError):
    """数据库异常"""

    def __init__(self, message: str = "Database operation failed", detail: str | None = None) -> None:
        super().__init__(message, 500, detail)


class ExternalServiceError(SystemError):
    """外部服务异常"""

    def __init__(self, message: str = "External service call failed", detail: str | None = None) -> None:
        super().__init__(message, 502, detail)


class ConfigurationError(SystemError):
    """配置异常"""

    def __init__(self, message: str = "Configuration error", detail: str | None = None) -> None:
        super().__init__(message, 500, detail)