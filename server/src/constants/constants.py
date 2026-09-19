#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公共常量定义
全局常量统一管理，业务常量按模块拆分
"""

from typing import Final


# -- 应用信息 -----------------------------------------------------------
APP_ID: str = "x-JingWei"
APP_NAME: str = "经纬（JingWei）"
APP_DESCRIPTION: str = "一个基于 FastAPI 构建的生产级工作流后端服务"
APP_VERSION: str = "0.1.0"


# ====================================
# HTTP Headers
# ====================================

HEADER_REQUEST_ID: Final[str] = "X-Request-ID"

# ====================================
# HTTP Status Codes
# ====================================

HTTP_STATUS_OK: Final[int] = 200

HTTP_STATUS_BAD_REQUEST: Final[int] = 400
HTTP_STATUS_UNAUTHORIZED: Final[int] = 401
HTTP_STATUS_FORBIDDEN: Final[int] = 403
HTTP_STATUS_NOT_FOUND: Final[int] = 404
HTTP_STATUS_CONFLICT: Final[int] = 409
HTTP_STATUS_TOO_MANY_REQUESTS: Final[int] = 429

HTTP_STATUS_INTERNAL_SERVER_ERROR: Final[int] = 500

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

# ====================================
# Document Constants
# ====================================

DEFAULT_CHUNK_SIZE: Final[int] = 500
DEFAULT_CHUNK_OVERLAP: Final[int] = 50

# ====================================
# Pagination Constants
# ====================================

DEFAULT_PAGE: Final[int] = 1
DEFAULT_PAGE_SIZE: Final[int] = 20
MAX_PAGE_SIZE: Final[int] = 100
MIN_PAGE_SIZE: Final[int] = 1

# ====================================
# API Version Constants
# ====================================

API_V1_PREFIX: Final[str] = "/api/v1"

# ====================================
# Error Messages
# ====================================

MSG_SUCCESS: Final[str] = "Success"
MSG_ERROR: Final[str] = "An error occurred"