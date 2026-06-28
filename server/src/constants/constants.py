#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公共常量定义
全局常量统一管理，业务常量按模块拆分
"""

from typing import Final

# ====================================
# HTTP Headers
# ====================================

HEADER_REQUEST_ID: Final[str] = "X-Request-ID"
HEADER_AUTHORIZATION: Final[str] = "Authorization"
HEADER_CONTENT_TYPE: Final[str] = "Content-Type"
HEADER_ACCEPT: Final[str] = "Accept"
HEADER_USER_AGENT: Final[str] = "User-Agent"
HEADER_X_FORWARDED_FOR: Final[str] = "X-Forwarded-For"

# ====================================
# HTTP Status Codes
# ====================================

HTTP_STATUS_OK: Final[int] = 200
HTTP_STATUS_CREATED: Final[int] = 201
HTTP_STATUS_ACCEPTED: Final[int] = 202
HTTP_STATUS_NO_CONTENT: Final[int] = 204

HTTP_STATUS_BAD_REQUEST: Final[int] = 400
HTTP_STATUS_UNAUTHORIZED: Final[int] = 401
HTTP_STATUS_FORBIDDEN: Final[int] = 403
HTTP_STATUS_NOT_FOUND: Final[int] = 404
HTTP_STATUS_METHOD_NOT_ALLOWED: Final[int] = 405
HTTP_STATUS_CONFLICT: Final[int] = 409
HTTP_STATUS_UNPROCESSABLE_ENTITY: Final[int] = 422
HTTP_STATUS_TOO_MANY_REQUESTS: Final[int] = 429

HTTP_STATUS_INTERNAL_SERVER_ERROR: Final[int] = 500
HTTP_STATUS_NOT_IMPLEMENTED: Final[int] = 501
HTTP_STATUS_BAD_GATEWAY: Final[int] = 502
HTTP_STATUS_SERVICE_UNAVAILABLE: Final[int] = 503
HTTP_STATUS_GATEWAY_TIMEOUT: Final[int] = 504

# ====================================
# Response Codes (Business)
# ====================================

CODE_SUCCESS: Final[int] = 0
CODE_ERROR: Final[int] = -1
CODE_VALIDATION_ERROR: Final[int] = 40001
CODE_UNAUTHORIZED: Final[int] = 40101
CODE_FORBIDDEN: Final[int] = 40301
CODE_NOT_FOUND: Final[int] = 40401
CODE_RATE_LIMIT_EXCEEDED: Final[int] = 42901
CODE_SERVER_ERROR: Final[int] = 50001
CODE_DATABASE_ERROR: Final[int] = 50002
CODE_EXTERNAL_SERVICE_ERROR: Final[int] = 50003
CODE_DOCUMENT_ERROR: Final[int] = 50004
CODE_EMBEDDING_ERROR: Final[int] = 50005
CODE_VECTOR_STORE_ERROR: Final[int] = 50006
CODE_RETRIEVAL_ERROR: Final[int] = 50007
CODE_GENERATION_ERROR: Final[int] = 50008

# ====================================
# Time Constants
# ====================================

SECONDS_PER_MINUTE: Final[int] = 60
SECONDS_PER_HOUR: Final[int] = 3600
SECONDS_PER_DAY: Final[int] = 86400
SECONDS_PER_WEEK: Final[int] = 604800
MILLISECONDS_PER_SECOND: Final[int] = 1000
MICROSECONDS_PER_SECOND: Final[int] = 1000000

# ====================================
# File Size Constants
# ====================================

KB: Final[int] = 1024
MB: Final[int] = 1024 * KB
GB: Final[int] = 1024 * MB
TB: Final[int] = 1024 * GB

# ====================================
# Regex Patterns
# ====================================

EMAIL_REGEX: Final[str] = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
PHONE_REGEX: Final[str] = r"^1[3-9]\d{9}$"
URL_REGEX: Final[str] = r"^https?://[^\s/$.?#].[^\s]*$"
UUID_REGEX: Final[str] = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"

# ====================================
# LLM Constants
# ====================================

DEFAULT_TEMPERATURE: Final[float] = 0.0
DEFAULT_MAX_TOKENS: Final[int] = 2000
DEFAULT_TIMEOUT: Final[int] = 60
MIN_TEMPERATURE: Final[float] = 0.0
MAX_TEMPERATURE: Final[float] = 2.0

# ====================================
# Document Constants
# ====================================

DEFAULT_CHUNK_SIZE: Final[int] = 500
DEFAULT_CHUNK_OVERLAP: Final[int] = 50
MAX_FILE_SIZE: Final[int] = 10 * MB
SUPPORTED_FILE_FORMATS: Final[list[str]] = [".txt", ".md", ".pdf", ".docx", ".doc"]

# ====================================
# Pagination Constants
# ====================================

DEFAULT_PAGE: Final[int] = 1
DEFAULT_PAGE_SIZE: Final[int] = 20
MAX_PAGE_SIZE: Final[int] = 100
MIN_PAGE_SIZE: Final[int] = 1

# ====================================
# Cache Constants
# ====================================

DEFAULT_CACHE_TTL: Final[int] = 300  # 5 minutes
SHORT_CACHE_TTL: Final[int] = 60     # 1 minute
LONG_CACHE_TTL: Final[int] = 3600    # 1 hour

# ====================================
# Environment Constants
# ====================================

ENV_DEVELOPMENT: Final[str] = "development"
ENV_TESTING: Final[str] = "testing"
ENV_PRODUCTION: Final[str] = "production"

# ====================================
# Security Constants
# ====================================

DEFAULT_SECRET_KEY: Final[str] = "your-secret-key-change-this-in-production"
DEFAULT_ALGORITHM: Final[str] = "HS256"
DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES: Final[int] = 30
DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS: Final[int] = 7

# ====================================
# API Version Constants
# ====================================

API_V1_PREFIX: Final[str] = "/api/v1"
API_V2_PREFIX: Final[str] = "/api/v2"

# ====================================
# Error Messages
# ====================================

MSG_SUCCESS: Final[str] = "Success"
MSG_ERROR: Final[str] = "An error occurred"
MSG_VALIDATION_ERROR: Final[str] = "Validation failed"
MSG_UNAUTHORIZED: Final[str] = "Unauthorized"
MSG_FORBIDDEN: Final[str] = "Forbidden"
MSG_NOT_FOUND: Final[str] = "Resource not found"
MSG_RATE_LIMIT_EXCEEDED: Final[str] = "Rate limit exceeded"
MSG_SERVER_ERROR: Final[str] = "Internal server error"
MSG_DATABASE_ERROR: Final[str] = "Database operation failed"
MSG_EXTERNAL_SERVICE_ERROR: Final[str] = "External service call failed"