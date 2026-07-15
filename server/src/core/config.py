#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用配置管理
支持从环境变量和YAML配置文件读取配置
"""

import os
from typing import Final, Any, TypeVar, Type
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict

T = TypeVar("T", bound=BaseSettings)


class Environment(str, Enum):
    """应用环境枚举"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


@dataclass
class ServerConfig:
    """服务器配置"""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    reload: bool = True


@dataclass
class LoggingConfig:
    """日志配置"""
    level: str = "INFO"
    format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    file_path: str = "logs/x-jingwei-{time:YYYYMMDDHH}.log"
    rotation: str = "1 hour"
    retention: str = "7 days"
    compression: str = "zip"
    console_output: bool = True


@dataclass
class CORSConfig:
    """CORS配置"""
    enabled: bool = True
    allow_origins: str = "*"
    allow_credentials: bool = True
    allow_methods: list[str] = field(default_factory=lambda: ["*"])
    allow_headers: list[str] = field(default_factory=lambda: ["*"])


@dataclass
class RateLimitConfig:
    """限流配置"""
    enabled: bool = True
    requests_per_minute: int = 60
    requests_per_hour: int = 1000


@dataclass
class DatabaseConfig:
    """数据库配置"""
    enabled: bool = True  # 修改为默认启用
    url: str = "mysql+pymysql://root:123456@localhost:3306/jingwei?charset=utf8mb4"  # 同步数据库连接 URL
    url_async: str = "mysql+aiomysql://root:123456@localhost:3306/jingwei?charset=utf8mb4"  # 异步数据库连接 URL
    host: str = "localhost"
    port: int = 3306
    user: str = "root"
    password: str = ""
    database: str = "jingwei"
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False


@dataclass
class RedisConfig:
    """Redis配置"""
    enabled: bool = False
    url: str = "redis://localhost:6379/0"
    pool_size: int = 10
    max_connections: int = 50
    decode_responses: bool = True
    socket_timeout: int = 5


@dataclass
class LLMProviderConfig:
    """LLM提供商配置"""
    api_key: str = ""
    api_base: str = ""
    model_name: str = ""


@dataclass
class LLMConfig:
    """LLM配置"""
    default_provider: str = "deepseek"
    temperature: float = 0.0
    max_tokens: int = 2000
    timeout: int = 60
    providers: dict[str, LLMProviderConfig] = field(default_factory=dict)


@dataclass
class VectorStoreConfig:
    """向量数据库配置"""
    enabled: bool = False
    type: str = "chromadb"
    persist_directory: str = "./data/vector_store"
    collection_name: str = "x-jingwei"
    chromadb_host: str = "localhost"
    chromadb_port: int = 8001


@dataclass
class DocumentConfig:
    """文档处理配置"""
    max_file_size: int = 10485760  # 10MB
    supported_formats: list[str] = field(default_factory=lambda: [".txt", ".md", ".pdf", ".docx", ".doc"])
    chunk_size: int = 500
    chunk_overlap: int = 50


@dataclass
class SecurityConfig:
    """安全配置"""
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7


@dataclass
class ApiDocsConfig:
    """API文档配置"""
    enabled: bool = True
    title: str = "经纬 API"
    description: str = "JingWei Learning and Training Project API Documentation"
    version: str = "0.1.0"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"


class Settings:
    """应用配置类

    支持从环境变量和YAML配置文件读取配置
    优先级：环境变量 > YAML配置文件 > 默认配置
    """

    # 配置文件路径
    CONFIG_FILE_PATH: Final[str] = 'config.yaml'
    ENV_FILE_PATH: Final[str] = '.env'

    def __init__(self) -> None:
        """初始化配置"""
        # 先加载 .env 文件到环境变量
        self._load_env_file()
        self._config: dict[str, Any] = self._load_config()
        self._parse_config()

    def _load_env_file(self) -> None:
        """从 .env 文件加载环境变量"""
        env_file: Path = Path(self.ENV_FILE_PATH)
        if not env_file.exists():
            return
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#') or '=' not in line:
                        continue
                    key, _, value = line.partition('=')
                    key, value = key.strip(), value.strip().strip('"').strip("'")
                    if not os.environ.get(key):
                        os.environ[key] = value
        except Exception as e:
            print(f"警告: 无法加载 .env 文件 {self.ENV_FILE_PATH}: {e}")

    def _load_config(self) -> dict[str, Any]:
        """加载配置

        优先级：环境变量 > YAML配置文件 > 默认配置

        Returns:
            dict[str, Any]: 合并后的配置
        """
        
        # 获取默认配置
        config: dict[str, Any] = self._get_default_config()

        # 从YAML文件加载配置
        self._load_from_file(config)

        # 从环境变量加载配置（优先级最高）
        self._load_from_env(config)

        return config

    def _get_default_config(self) -> dict[str, Any]:
        """获取默认配置

        Returns:
            dict[str, Any]: 默认配置字典
        """
        return {
            'app': {
                'name': 'x-jingwei',
                'version': '0.1.0',
                'description': 'X-JingWei 经纬 - Production Grade LLM Application Development Platform',
                'environment': 'development',
                'debug': True,
                'timezone': 'Asia/Shanghai',
                'locale': 'zh_CN'
            },
            'server': {
                'host': '0.0.0.0',
                'port': 8000,
                'workers': 1,
                'reload': True
            },
            'logging': {
                'level': 'INFO',
                'format': '{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}',
                'file_path': 'logs/x-jingwei-{time:YYYYMMDDHH}.log',
                'rotation': '1 hour',
                'retention': '7 days',
                'compression': 'zip',
                'console_output': True
            },
            'cors': {
                'enabled': True,
                'allow_origins': '*',
                'allow_credentials': True,
                'allow_methods': ['*'],
                'allow_headers': ['*']
            },
            'rate_limit': {
                'enabled': True,
                'requests_per_minute': 60,
                'requests_per_hour': 1000
            },
            'database': {
                'enabled': True,
                'url': 'mysql+pymysql://root:123456@localhost:3306/jingwei?charset=utf8mb4',
                'url_async': 'mysql+aiomysql://root:123456@localhost:3306/jingwei?charset=utf8mb4',
                'host': 'localhost',
                'port': 3306,
                'user': 'root',
                'password': '',
                'database': 'jingwei',
                'pool_size': 10,
                'max_overflow': 20,
                'pool_timeout': 30,
                'pool_recycle': 3600,
                'echo': False
            },
            'redis': {
                'enabled': False,
                'url': 'redis://localhost:6379/0',
                'pool_size': 10,
                'max_connections': 50,
                'decode_responses': True,
                'socket_timeout': 5
            },
            'llm': {
                'default_provider': 'deepseek',
                'temperature': 0.0,
                'max_tokens': 2000,
                'timeout': 60,
                'providers': {}
            },
            'vector_store': {
                'enabled': False,
                'type': 'chromadb',
                'persist_directory': './data/vector_store',
                'collection_name': 'x-jingwei',
                'chromadb': {
                    'host': 'localhost',
                    'port': 8001
                }
            },
            'document': {
                'max_file_size': 10485760,
                'supported_formats': ['.txt', '.md', '.pdf', '.docx', '.doc'],
                'chunk_size': 500,
                'chunk_overlap': 50
            },
            'security': {
                'secret_key': 'your-secret-key-here',
                'algorithm': 'HS256',
                'access_token_expire_minutes': 30,
                'refresh_token_expire_days': 7
            },
            'api_docs': {
                'enabled': True,
                'title': 'X-JingWei 经纬 API',
                'description': 'X-JingWei 经纬 API Documentation',
                'version': '0.1.0',
                'docs_url': '/docs',
                'redoc_url': '/redoc',
                'openapi_url': '/openapi.json'
            }
        }

    def _merge_config(self, base: dict[str, Any], override: dict[str, Any]) -> None:
        """递归合并配置

        Args:
            base: 基础配置字典
            override: 要覆盖的配置字典
        """
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value

    def _load_from_file(self, config: dict[str, Any]) -> None:
        """从YAML文件加载配置

        Args:
            config: 配置字典
        """
        config_file: Path = Path(self.CONFIG_FILE_PATH)
        if not config_file.exists():
            return

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                file_config: dict[str, Any] = yaml.safe_load(f) or {}
            self._merge_config(config, file_config)
        except Exception as e:
            print(f"警告: 无法加载配置文件 {self.CONFIG_FILE_PATH}: {e}")

    def _load_from_env(self, config: dict[str, Any]) -> None:
        """从环境变量加载配置

        Args:
            config: 配置字典
        """
        # 应用配置
        if os.environ.get('APP_NAME'):
            config['app']['name'] = os.environ.get('APP_NAME')
        if os.environ.get('APP_VERSION'):
            config['app']['version'] = os.environ.get('APP_VERSION')
        if os.environ.get('APP_ENVIRONMENT'):
            config['app']['environment'] = os.environ.get('APP_ENVIRONMENT')
        if os.environ.get('APP_DEBUG'):
            config['app']['debug'] = os.environ.get('APP_DEBUG').lower() == 'true'

        # 服务器配置
        if os.environ.get('SERVER_HOST'):
            config['server']['host'] = os.environ.get('SERVER_HOST')
        if os.environ.get('SERVER_PORT'):
            config['server']['port'] = int(os.environ.get('SERVER_PORT'))
        if os.environ.get('SERVER_WORKERS'):
            config['server']['workers'] = int(os.environ.get('SERVER_WORKERS'))
        if os.environ.get('SERVER_RELOAD'):
            config['server']['reload'] = os.environ.get('SERVER_RELOAD').lower() == 'true'

        # 日志配置
        if os.environ.get('LOG_LEVEL'):
            config['logging']['level'] = os.environ.get('LOG_LEVEL')
        if os.environ.get('LOG_FILE_PATH'):
            config['logging']['file_path'] = os.environ.get('LOG_FILE_PATH')
        if os.environ.get('LOG_ROTATION'):
            config['logging']['rotation'] = os.environ.get('LOG_ROTATION')
        if os.environ.get('LOG_RETENTION'):
            config['logging']['retention'] = os.environ.get('LOG_RETENTION')
        if os.environ.get('LOG_COMPRESSION'):
            config['logging']['compression'] = os.environ.get('LOG_COMPRESSION')
        if os.environ.get('LOG_CONSOLE_OUTPUT'):
            config['logging']['console_output'] = os.environ.get('LOG_CONSOLE_OUTPUT').lower() == 'true'

        # CORS配置
        if os.environ.get('CORS_ENABLED'):
            config['cors']['enabled'] = os.environ.get('CORS_ENABLED').lower() == 'true'
        if os.environ.get('CORS_ALLOW_ORIGINS'):
            config['cors']['allow_origins'] = os.environ.get('CORS_ALLOW_ORIGINS')
        if os.environ.get('CORS_ALLOW_CREDENTIALS'):
            config['cors']['allow_credentials'] = os.environ.get('CORS_ALLOW_CREDENTIALS').lower() == 'true'
        if os.environ.get('CORS_ALLOW_METHODS'):
            config['cors']['allow_methods'] = os.environ.get('CORS_ALLOW_METHODS').split(',')
        if os.environ.get('CORS_ALLOW_HEADERS'):
            config['cors']['allow_headers'] = os.environ.get('CORS_ALLOW_HEADERS').split(',')

        # 限流配置
        if os.environ.get('RATE_LIMIT_ENABLED'):
            config['rate_limit']['enabled'] = os.environ.get('RATE_LIMIT_ENABLED').lower() == 'true'
        if os.environ.get('RATE_LIMIT_REQUESTS_PER_MINUTE'):
            config['rate_limit']['requests_per_minute'] = int(os.environ.get('RATE_LIMIT_REQUESTS_PER_MINUTE'))
        if os.environ.get('RATE_LIMIT_REQUESTS_PER_HOUR'):
            config['rate_limit']['requests_per_hour'] = int(os.environ.get('RATE_LIMIT_REQUESTS_PER_HOUR'))

        # 数据库配置
        if os.environ.get('DATABASE_ENABLED'):
            config['database']['enabled'] = os.environ.get('DATABASE_ENABLED').lower() == 'true'
        if os.environ.get('DATABASE_URL'):
            config['database']['url'] = os.environ.get('DATABASE_URL')
        if os.environ.get('ASYNC_DATABASE_URL'):
            config['database']['url_async'] = os.environ.get('ASYNC_DATABASE_URL')
        if os.environ.get('DB_HOST'):
            config['database']['host'] = os.environ.get('DB_HOST')
        if os.environ.get('DB_PORT'):
            config['database']['port'] = int(os.environ.get('DB_PORT'))
        if os.environ.get('DB_USER'):
            config['database']['user'] = os.environ.get('DB_USER')
        if os.environ.get('DB_PASSWORD'):
            config['database']['password'] = os.environ.get('DB_PASSWORD')
        if os.environ.get('DB_NAME'):
            config['database']['database'] = os.environ.get('DB_NAME')
        if os.environ.get('DATABASE_POOL_SIZE'):
            config['database']['pool_size'] = int(os.environ.get('DATABASE_POOL_SIZE'))
        if os.environ.get('DATABASE_MAX_OVERFLOW'):
            config['database']['max_overflow'] = int(os.environ.get('DATABASE_MAX_OVERFLOW'))
        if os.environ.get('DATABASE_POOL_TIMEOUT'):
            config['database']['pool_timeout'] = int(os.environ.get('DATABASE_POOL_TIMEOUT'))
        if os.environ.get('DATABASE_POOL_RECYCLE'):
            config['database']['pool_recycle'] = int(os.environ.get('DATABASE_POOL_RECYCLE'))
        if os.environ.get('DATABASE_ECHO'):
            config['database']['echo'] = os.environ.get('DATABASE_ECHO').lower() == 'true'

        # Redis配置
        if os.environ.get('REDIS_ENABLED'):
            config['redis']['enabled'] = os.environ.get('REDIS_ENABLED').lower() == 'true'
        if os.environ.get('REDIS_URL'):
            config['redis']['url'] = os.environ.get('REDIS_URL')
        if os.environ.get('REDIS_POOL_SIZE'):
            config['redis']['pool_size'] = int(os.environ.get('REDIS_POOL_SIZE'))
        if os.environ.get('REDIS_MAX_CONNECTIONS'):
            config['redis']['max_connections'] = int(os.environ.get('REDIS_MAX_CONNECTIONS'))
        if os.environ.get('REDIS_DECODE_RESPONSES'):
            config['redis']['decode_responses'] = os.environ.get('REDIS_DECODE_RESPONSES').lower() == 'true'
        if os.environ.get('REDIS_SOCKET_TIMEOUT'):
            config['redis']['socket_timeout'] = int(os.environ.get('REDIS_SOCKET_TIMEOUT'))

        # LLM配置
        if os.environ.get('LLM_DEFAULT_PROVIDER'):
            config['llm']['default_provider'] = os.environ.get('LLM_DEFAULT_PROVIDER')
        if os.environ.get('LLM_TEMPERATURE'):
            config['llm']['temperature'] = float(os.environ.get('LLM_TEMPERATURE'))
        if os.environ.get('LLM_MAX_TOKENS'):
            config['llm']['max_tokens'] = int(os.environ.get('LLM_MAX_TOKENS'))
        if os.environ.get('LLM_TIMEOUT'):
            config['llm']['timeout'] = int(os.environ.get('LLM_TIMEOUT'))

        # DeepSeek配置
        if os.environ.get('DEEPSEEK_API_KEY'):
            config['llm']['providers']['deepseek'] = {
                'api_key': os.environ.get('DEEPSEEK_API_KEY'),
                'api_base': os.environ.get('DEEPSEEK_API_BASE', 'https://api.deepseek.com/v1'),
                'model_name': os.environ.get('DEEPSEEK_MODEL_NAME', 'deepseek-chat')
            }

        # Doubao配置
        if os.environ.get('DOUBAO_API_KEY'):
            config['llm']['providers']['doubao'] = {
                'api_key': os.environ.get('DOUBAO_API_KEY'),
                'api_base': os.environ.get('DOUBAO_API_BASE', 'https://ark.cn-beijing.volces.com/api/v3'),
                'model_name': os.environ.get('DOUBAO_MODEL_NAME', 'doubao-pro')
            }

        # Aliyun配置
        if os.environ.get('ALIYUN_API_KEY'):
            config['llm']['providers']['aliyun'] = {
                'api_key': os.environ.get('ALIYUN_API_KEY'),
                'api_base': os.environ.get('ALIYUN_API_BASE', 'https://dashscope.aliyuncs.com/compatible-mode/v1'),
                'model_name': os.environ.get('ALIYUN_MODEL_NAME', 'qwen-plus')
            }

        # 向量数据库配置
        if os.environ.get('VECTOR_STORE_ENABLED'):
            config['vector_store']['enabled'] = os.environ.get('VECTOR_STORE_ENABLED').lower() == 'true'
        if os.environ.get('VECTOR_STORE_TYPE'):
            config['vector_store']['type'] = os.environ.get('VECTOR_STORE_TYPE')
        if os.environ.get('VECTOR_STORE_PERSIST_DIRECTORY'):
            config['vector_store']['persist_directory'] = os.environ.get('VECTOR_STORE_PERSIST_DIRECTORY')
        if os.environ.get('VECTOR_STORE_COLLECTION_NAME'):
            config['vector_store']['collection_name'] = os.environ.get('VECTOR_STORE_COLLECTION_NAME')
        if os.environ.get('CHROMADB_HOST'):
            if 'chromadb' not in config['vector_store']:
                config['vector_store']['chromadb'] = {}
            config['vector_store']['chromadb']['host'] = os.environ.get('CHROMADB_HOST')
        if os.environ.get('CHROMADB_PORT'):
            if 'chromadb' not in config['vector_store']:
                config['vector_store']['chromadb'] = {}
            config['vector_store']['chromadb']['port'] = int(os.environ.get('CHROMADB_PORT'))

        # 文档配置
        if os.environ.get('DOCUMENT_MAX_FILE_SIZE'):
            config['document']['max_file_size'] = int(os.environ.get('DOCUMENT_MAX_FILE_SIZE'))
        if os.environ.get('DOCUMENT_CHUNK_SIZE'):
            config['document']['chunk_size'] = int(os.environ.get('DOCUMENT_CHUNK_SIZE'))
        if os.environ.get('DOCUMENT_CHUNK_OVERLAP'):
            config['document']['chunk_overlap'] = int(os.environ.get('DOCUMENT_CHUNK_OVERLAP'))

        # 安全配置
        if os.environ.get('SECRET_KEY'):
            config['security']['secret_key'] = os.environ.get('SECRET_KEY')
        if os.environ.get('SECURITY_ALGORITHM'):
            config['security']['algorithm'] = os.environ.get('SECURITY_ALGORITHM')
        if os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES'):
            config['security']['access_token_expire_minutes'] = int(os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES'))
        if os.environ.get('REFRESH_TOKEN_EXPIRE_DAYS'):
            config['security']['refresh_token_expire_days'] = int(os.environ.get('REFRESH_TOKEN_EXPIRE_DAYS'))

        # API文档配置
        if os.environ.get('API_DOCS_ENABLED'):
            config['api_docs']['enabled'] = os.environ.get('API_DOCS_ENABLED').lower() == 'true'

    def _parse_config(self) -> None:
        """解析配置到具体配置对象"""
        self.app_name: str = self._config['app']['name']
        self.app_version: str = self._config['app']['version']
        self.app_description: str = self._config['app'].get('description', 'JingWei Learning and Training Project')
        self.app_environment: str = self._config['app']['environment']
        self.app_debug: bool = self._config['app']['debug']
        self.app_timezone: str = self._config['app'].get('timezone', 'Asia/Shanghai')
        self.app_locale: str = self._config['app'].get('locale', 'zh_CN')

        self.server = ServerConfig(**self._config['server'])
        self.logging = LoggingConfig(**self._config['logging'])
        self.cors = CORSConfig(**self._config['cors'])
        self.rate_limit = RateLimitConfig(**self._config['rate_limit'])
        self.database = DatabaseConfig(**self._config['database'])
        self.redis = RedisConfig(**self._config['redis'])
        self.vector_store = VectorStoreConfig(**{k: v for k, v in self._config['vector_store'].items()
                                                 if k != 'chromadb'})
        self.vector_store.chromadb_host = self._config['vector_store'].get('chromadb', {}).get('host', 'localhost')
        self.vector_store.chromadb_port = self._config['vector_store'].get('chromadb', {}).get('port', 8001)
        self.document = DocumentConfig(**self._config['document'])
        self.security = SecurityConfig(**self._config['security'])
        self.api_docs = ApiDocsConfig(**self._config['api_docs'])

        self.llm = LLMConfig(
            default_provider=self._config['llm']['default_provider'],
            temperature=self._config['llm']['temperature'],
            max_tokens=self._config['llm']['max_tokens'],
            timeout=self._config['llm']['timeout'],
            providers={
                provider: LLMProviderConfig(**config)
                for provider, config in self._config['llm'].get('providers', {}).items()
            }
        )

    @property
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.app_environment == Environment.DEVELOPMENT

    @property
    def is_testing(self) -> bool:
        """是否为测试环境"""
        return self.app_environment == Environment.TESTING

    @property
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.app_environment == Environment.PRODUCTION

    def reload(self) -> None:
        """重新加载配置"""
        self._config = self._load_config()
        self._parse_config()


# 创建全局配置实例
settings: Final[Settings] = Settings()