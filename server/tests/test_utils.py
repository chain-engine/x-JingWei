#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具函数测试
"""

import pytest
from src.utils.helpers import (
    generate_uuid,
    generate_short_uuid,
    hash_string,
    is_valid_email,
    is_valid_phone,
    is_valid_url,
    is_valid_uuid,
    truncate_text,
    clean_text,
    chunk_text,
    bytes_to_human,
    human_to_bytes,
    mask_sensitive_data,
    deep_get,
    deep_set
)


class TestHelpers:
    """工具函数测试"""

    def test_generate_uuid(self) -> None:
        """测试生成UUID"""
        uuid_str = generate_uuid()
        assert uuid_str
        assert is_valid_uuid(uuid_str)

    def test_generate_short_uuid(self) -> None:
        """测试生成短UUID"""
        short_uuid = generate_short_uuid()
        assert short_uuid
        assert len(short_uuid) == 16

    def test_hash_string(self) -> None:
        """测试字符串哈希"""
        text = "hello"
        md5_hash = hash_string(text, "md5")
        sha256_hash = hash_string(text, "sha256")

        assert md5_hash
        assert sha256_hash
        assert md5_hash != sha256_hash
        assert len(md5_hash) == 32
        assert len(sha256_hash) == 64

    def test_is_valid_email(self) -> None:
        """测试邮箱验证"""
        assert is_valid_email("user@example.com")
        assert is_valid_email("test.user+tag@example.co.uk")
        assert not is_valid_email("invalid")
        assert not is_valid_email("invalid@")
        assert not is_valid_email("@example.com")

    def test_is_valid_phone(self) -> None:
        """测试手机号验证"""
        assert is_valid_phone("13800138000")
        assert is_valid_phone("15012345678")
        assert not is_valid_phone("12345678901")
        assert not is_valid_phone("1380013800")
        assert not is_valid_phone("138001380000")

    def test_is_valid_url(self) -> None:
        """测试URL验证"""
        assert is_valid_url("https://example.com")
        assert is_valid_url("http://example.com/path?query=value")
        assert not is_valid_url("example.com")
        assert not is_valid_url("ftp://example.com")

    def test_is_valid_uuid(self) -> None:
        """测试UUID验证"""
        assert is_valid_uuid("123e4567-e89b-12d3-a456-426614174000")
        assert not is_valid_uuid("123e4567")
        assert not is_valid_uuid("123e4567-e89b-12d3-a456-42661417400g")

    def test_truncate_text(self) -> None:
        """测试文本截断"""
        text = "This is a long text that needs to be truncated"
        truncated = truncate_text(text, 20)
        assert len(truncated) <= 23  # 20 + len("...")
        assert truncated.endswith("...")

    def test_clean_text(self) -> None:
        """测试文本清理"""
        text = "Hello   World!  \n\nTest"
        cleaned = clean_text(text)
        assert cleaned == "Hello World! Test"

    def test_chunk_text(self) -> None:
        """测试文本分块"""
        text = "This is a test text. It has multiple sentences. We want to chunk it."
        chunks = chunk_text(text, chunk_size=20, chunk_overlap=5)
        assert len(chunks) > 0
        assert all(len(chunk) > 0 for chunk in chunks)

    def test_bytes_to_human(self) -> None:
        """测试字节转人类可读格式"""
        assert bytes_to_human(1024) == "1.00 KB"
        assert bytes_to_human(1024 * 1024) == "1.00 MB"
        assert bytes_to_human(1024 * 1024 * 1024) == "1.00 GB"

    def test_human_to_bytes(self) -> None:
        """测试人类可读格式转字节"""
        assert human_to_bytes("1 KB") == 1024
        assert human_to_bytes("1 MB") == 1024 * 1024
        assert human_to_bytes("1 GB") == 1024 * 1024 * 1024

    def test_mask_sensitive_data(self) -> None:
        """测试敏感数据脱敏"""
        data = "13800138000"
        masked = mask_sensitive_data(data, visible_chars=3)
        assert masked.startswith("138")
        assert masked.endswith("000")
        assert "*" in masked

    def test_deep_get(self) -> None:
        """测试深度获取字典值"""
        data = {"a": {"b": {"c": "value"}}}
        assert deep_get(data, "a.b.c") == "value"
        assert deep_get(data, "a.b.d") is None
        assert deep_get(data, "a.b.d", "default") == "default"

    def test_deep_set(self) -> None:
        """测试深度设置字典值"""
        data = {}
        deep_set(data, "a.b.c", "value")
        assert data["a"]["b"]["c"] == "value"