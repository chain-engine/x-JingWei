#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理示例
展示如何使用配置系统
"""

from core.config import settings
from core.logger import logger


def config_example() -> None:
    """配置示例"""
    # 应用信息
    print(f"应用名称: {settings.app_name}")
    print(f"应用版本: {settings.app_version}")
    print(f"应用环境: {settings.app_environment}")
    print(f"调试模式: {settings.app_debug}")

    # 服务器配置
    print(f"服务器地址: {settings.server.host}:{settings.server.port}")

    # 日志配置
    print(f"日志级别: {settings.logging.level}")
    print(f"日志文件: {settings.logging.file_path}")

    # LLM配置
    print(f"默认提供商: {settings.llm.default_provider}")
    print(f"可用提供商: {list(settings.llm.providers.keys())}")

    # 环境判断
    if settings.is_development:
        print("当前运行环境: 开发环境")
    elif settings.is_testing:
        print("当前运行环境: 测试环境")
    elif settings.is_production:
        print("当前运行环境: 生产环境")


if __name__ == "__main__":
    config_example()