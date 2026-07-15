#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用工具函数
"""

import hashlib
import re
import uuid
from typing import Any, Optional
from datetime import datetime


def generate_uuid() -> str:
    """生成UUID

    Returns:
        str: UUID字符串
    """
    return str(uuid.uuid4())


def generate_short_uuid() -> str:
    """生成短UUID

    Returns:
        str: 短UUID字符串
    """
    return str(uuid.uuid4()).replace("-", "")[:16]


def hash_string(text: str, algorithm: str = "sha256") -> str:
    """字符串哈希

    Args:
        text: 待哈希的字符串
        algorithm: 哈希算法

    Returns:
        str: 哈希值
    """
    if algorithm == "md5":
        return hashlib.md5(text.encode()).hexdigest()
    elif algorithm == "sha1":
        return hashlib.sha1(text.encode()).hexdigest()
    elif algorithm == "sha256":
        return hashlib.sha256(text.encode()).hexdigest()
    elif algorithm == "sha512":
        return hashlib.sha512(text.encode()).hexdigest()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")


def is_valid_email(email: str) -> bool:
    """验证邮箱格式

    Args:
        email: 邮箱地址

    Returns:
        bool: 是否有效
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def is_valid_phone(phone: str) -> bool:
    """验证手机号格式

    Args:
        phone: 手机号码

    Returns:
        bool: 是否有效
    """
    pattern = r"^1[3-9]\d{9}$"
    return bool(re.match(pattern, phone))


def is_valid_url(url: str) -> bool:
    """验证URL格式

    Args:
        url: URL字符串

    Returns:
        bool: 是否有效
    """
    pattern = r"^https?://[^\s/$.?#].[^\s]*$"
    return bool(re.match(pattern, url))


def is_valid_uuid(uuid_str: str) -> bool:
    """验证UUID格式

    Args:
        uuid_str: UUID字符串

    Returns:
        bool: 是否有效
    """
    pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    return bool(re.match(pattern, uuid_str.lower()))


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """截断文本

    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 后缀

    Returns:
        str: 截断后的文本
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def clean_text(text: str) -> str:
    """清理文本

    Args:
        text: 原始文本

    Returns:
        str: 清理后的文本
    """
    # 移除多余空格
    text = re.sub(r'\s+', ' ', text)
    # 移除特殊字符（保留中文、英文、数字、常用标点）
    text = re.sub(r'[^一-龥a-zA-Z0-9\s，。！？、；：""''（）【】《》\-\.,!?:;()]', '', text)
    return text.strip()


def chunk_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> list[str]:
    """文本分块

    Args:
        text: 原始文本
        chunk_size: 分块大小
        chunk_overlap: 分块重叠

    Returns:
        list[str]: 分块列表
    """
    if chunk_overlap >= chunk_size:
        chunk_overlap = chunk_size // 2

    chunks: list[str] = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]

        # 尝试在句子边界处切分
        if end < text_length:
            # 查找最近的句号、问号、感叹号
            for delimiter in ['。', '！', '？', '.', '!', '?', '\n']:
                delimiter_pos = chunk.rfind(delimiter)
                if delimiter_pos > chunk_size // 2:
                    chunk = chunk[:delimiter_pos + 1]
                    break

        if chunk.strip():
            chunks.append(chunk.strip())

        start = end - chunk_overlap
        if start >= text_length:
            break

    return chunks


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """格式化日期时间

    Args:
        dt: 日期时间对象
        format_str: 格式字符串

    Returns:
        str: 格式化后的字符串
    """
    return dt.strftime(format_str)


def parse_datetime(dt_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """解析日期时间字符串

    Args:
        dt_str: 日期时间字符串
        format_str: 格式字符串

    Returns:
        datetime: 日期时间对象
    """
    return datetime.strptime(dt_str, format_str)


def get_timestamp() -> int:
    """获取当前时间戳

    Returns:
        int: 时间戳（秒）
    """
    return int(datetime.utcnow().timestamp())


def get_timestamp_ms() -> int:
    """获取当前时间戳（毫秒）

    Returns:
        int: 时间戳（毫秒）
    """
    return int(datetime.utcnow().timestamp() * 1000)


def bytes_to_human(bytes_size: int) -> str:
    """字节转人类可读格式

    Args:
        bytes_size: 字节数

    Returns:
        str: 人类可读格式
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if abs(bytes_size) < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"


def human_to_bytes(human_size: str) -> int:
    """人类可读格式转字节

    Args:
        human_size: 人类可读格式

    Returns:
        int: 字节数
    """
    units = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3, 'TB': 1024**4}
    match = re.match(r'^([\d.]+)\s*([KMGT]?B)$', human_size.upper())
    if not match:
        raise ValueError(f"Invalid size format: {human_size}")

    value = float(match.group(1))
    unit = match.group(2)
    return int(value * units[unit])


def mask_sensitive_data(text: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """脱敏敏感数据

    Args:
        text: 原始文本
        mask_char: 掩码字符
        visible_chars: 可见字符数

    Returns:
        str: 脱敏后的文本
    """
    if not text:
        return text

    if len(text) <= visible_chars * 2:
        return mask_char * len(text)

    start = text[:visible_chars]
    end = text[-visible_chars:]
    masked_length = len(text) - visible_chars * 2
    return f"{start}{mask_char * masked_length}{end}"


def deep_get(data: dict[str, Any], keys: str, default: Any = None) -> Any:
    """深度获取字典值

    Args:
        data: 字典数据
        keys: 键路径，使用点号分隔
        default: 默认值

    Returns:
        Any: 值或默认值
    """
    keys_list = keys.split('.')
    result = data
    for key in keys_list:
        if isinstance(result, dict) and key in result:
            result = result[key]
        else:
            return default
    return result


def deep_set(data: dict[str, Any], keys: str, value: Any) -> None:
    """深度设置字典值

    Args:
        data: 字典数据
        keys: 键路径，使用点号分隔
        value: 值
    """
    keys_list = keys.split('.')
    result = data
    for key in keys_list[:-1]:
        if key not in result:
            result[key] = {}
        result = result[key]
    result[keys_list[-1]] = value