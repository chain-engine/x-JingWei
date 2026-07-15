#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证器模块
"""

from typing import Any
from pydantic import validator


class FileSizeValidator:
    """文件大小验证器"""

    def __init__(self, max_size: int) -> None:
        """初始化验证器

        Args:
            max_size: 最大文件大小（字节）
        """
        self.max_size = max_size

    def __call__(self, value: int) -> int:
        """验证文件大小

        Args:
            value: 文件大小

        Returns:
            int: 验证后的文件大小

        Raises:
            ValueError: 验证失败
        """
        if value > self.max_size:
            raise ValueError(f"File size exceeds maximum allowed size of {self.max_size} bytes")
        if value < 0:
            raise ValueError("File size cannot be negative")
        return value


class TemperatureValidator:
    """温度参数验证器"""

    def __init__(self, min_temp: float = 0.0, max_temp: float = 2.0) -> None:
        """初始化验证器

        Args:
            min_temp: 最小温度
            max_temp: 最大温度
        """
        self.min_temp = min_temp
        self.max_temp = max_temp

    def __call__(self, value: float) -> float:
        """验证温度参数

        Args:
            value: 温度值

        Returns:
            float: 验证后的温度值

        Raises:
            ValueError: 验证失败
        """
        if value < self.min_temp or value > self.max_temp:
            raise ValueError(f"Temperature must be between {self.min_temp} and {self.max_temp}")
        return value


class PaginationValidator:
    """分页参数验证器"""

    def __init__(
        self,
        min_page: int = 1,
        max_page_size: int = 100,
        min_page_size: int = 1
    ) -> None:
        """初始化验证器

        Args:
            min_page: 最小页码
            max_page_size: 最大每页记录数
            min_page_size: 最小每页记录数
        """
        self.min_page = min_page
        self.max_page_size = max_page_size
        self.min_page_size = min_page_size

    def validate_page(self, value: int) -> int:
        """验证页码

        Args:
            value: 页码

        Returns:
            int: 验证后的页码
        """
        return max(self.min_page, value)

    def validate_page_size(self, value: int) -> int:
        """验证每页记录数

        Args:
            value: 每页记录数

        Returns:
            int: 验证后的每页记录数
        """
        return max(self.min_page_size, min(self.max_page_size, value))


def validate_required_fields(data: dict[str, Any], required_fields: list[str]) -> list[str]:
    """验证必填字段

    Args:
        data: 数据字典
        required_fields: 必填字段列表

    Returns:
        list[str]: 缺失的字段列表
    """
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == "":
            missing_fields.append(field)
    return missing_fields


def validate_enum(value: Any, enum_values: list[Any], field_name: str = "field") -> Any:
    """验证枚举值

    Args:
        value: 值
        enum_values: 枚举值列表
        field_name: 字段名称

    Returns:
        Any: 验证后的值

    Raises:
        ValueError: 验证失败
    """
    if value not in enum_values:
        raise ValueError(f"{field_name} must be one of {enum_values}, got {value}")
    return value