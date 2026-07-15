#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一响应封装

提供标准化的成功/错误响应构造函数，确保接口返回格式一致。
"""

from typing import Any

from datetime import datetime, timezone

from constants.constants import CODE_SUCCESS, CODE_ERROR, MSG_SUCCESS, MSG_ERROR


def success_response(
    data: Any = None,
    message: str = MSG_SUCCESS,
    code: int = CODE_SUCCESS,
    request_id: str | None = None,
) -> dict[str, Any]:
    """构造成功响应"""
    return {
        "code": code,
        "message": message,
        "data": data,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_id": request_id,
    }


def error_response(
    message: str = MSG_ERROR,
    code: int = CODE_ERROR,
    errors: list[dict[str, Any]] | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    """构造错误响应"""
    response = {
        "code": code,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_id": request_id,
    }

    if errors:
        response["errors"] = errors

    return response