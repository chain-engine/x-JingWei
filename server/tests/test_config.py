#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置测试
"""

import pytest
from core.config import settings, Environment


class TestSettings:
    """配置测试"""

    def test_app_name(self) -> None:
        """测试应用名称"""
        assert settings.app_name == "x-jingwei"

    def test_app_version(self) -> None:
        """测试应用版本"""
        assert settings.app_version == "0.1.0"

    def test_app_environment(self) -> None:
        """测试应用环境"""
        assert settings.app_environment in [
            Environment.DEVELOPMENT,
            Environment.TESTING,
            Environment.PRODUCTION
        ]

    def test_server_config(self) -> None:
        """测试服务器配置"""
        assert settings.server.host
        assert settings.server.port > 0
        assert settings.server.port <= 65535

    def test_logging_config(self) -> None:
        """测试日志配置"""
        assert settings.logging.level
        assert settings.logging.file_path

    def test_llm_config(self) -> None:
        """测试LLM配置"""
        assert settings.llm.default_provider
        assert settings.llm.temperature >= 0.0
        assert settings.llm.temperature <= 2.0
        assert settings.llm.max_tokens > 0

    def test_is_development(self) -> None:
        """测试开发环境判断"""
        is_dev = settings.app_environment == Environment.DEVELOPMENT
        assert settings.is_development == is_dev

    def test_document_config(self) -> None:
        """测试文档配置"""
        assert settings.document.chunk_size > 0
        assert settings.document.chunk_overlap >= 0
        assert settings.document.chunk_overlap < settings.document.chunk_size