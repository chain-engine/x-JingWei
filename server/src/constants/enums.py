# -*- coding: utf-8 -*-
"""
开发相关常量

本模块定义了开发过程中常用的常量，包括：
- HTTP 内容类型
- 加密算法（哈希、对称、非对称）
- 工作模式
- 填充方式
- 编码方式
- 日志配置
"""

from enum import Enum


class DescribedEnum(Enum):
    """
    可描述的枚举类基建
    mark: int        唯一标识
    desc: str        描述信息
    """

    def __init__(self, mark: int, desc: str) -> None:
        self._mark = mark
        self._desc = desc

    @property
    def mark(self) -> int:
        return self._mark

    @property
    def desc(self) -> str:
        return self._desc

    @classmethod
    def get_all_marks(cls) -> list[int]:
        return [described_enum.mark for described_enum in cls]

    @classmethod
    def get_all_descs(cls) -> list[str]:
        return [described_enum.desc for described_enum in cls]

    @classmethod
    def get_choices(cls) -> tuple[tuple[int, str], ...]:
        return tuple((described_enum.mark, described_enum.desc) for described_enum in cls)



# ── HTTP 内容类型 ──────────────────────────────────────────────

class HttpMediaType(str, DescribedEnum):
    """HTTP 内容类型"""
    JSON = 1, "application/json"
    FILE = 2, "application/octet-stream"
    FORM_URL_ENCODED = 3, "application/x-www-form-urlencoded"
    MULTIPART_FORM_DATA = 4, "multipart/form-data"


# ── 加密算法 ───────────────────────────────────────────────────

class HashAlgo(str, DescribedEnum):
    """单向加密算法（哈希算法）"""
    MD5 = 1, "MD5"
    SHA1 = 2, "SHA1"
    SHA256 = 3, "SHA256"
    SHA512 = 4, "SHA512"
    SM3 = 5, "SM3"


class SymmetricCipher(str, DescribedEnum):
    """对称加密算法"""
    AES = 1, "AES"
    SM4 = 2, "SM4"
    DES = 3, "DES"
    THREE_DES = 4, "3DES"
    CHACHA20 = 5, "ChaCha20"
    RC4 = 6, "RC4"


class AsymmetricCipher(str, DescribedEnum):
    """非对称加密算法"""
    RSA = 1, "RSA"
    ECC = 2, "ECC"
    DSA = 3, "DSA"
    SM2 = 4, "SM2"


# ── 工作模式 ───────────────────────────────────────────────────

class CipherMode(str, DescribedEnum):
    """加密工作模式"""
    ECB = 1, "ECB"
    CBC = 2, "CBC"
    GCM = 3, "GCM"


# ── 填充方式 ───────────────────────────────────────────────────

class BlockCipherPadding(str, DescribedEnum):
    """对称加密中的块加密填充方式"""
    PKCS7 = 1, "PKCS7"
    ISO10126 = 2, "ISO10126"
    NO_PADDING = 3, "NoPadding"
    ZERO_PADDING = 4, "ZeroPadding"


class AsymmetricPaddingScheme(str, DescribedEnum):
    """非对称加密填充方式"""
    PKCS1V15 = 1, "PKCS1v15"
    OAEP = 2, "OAEP"


# ── 编码方式 ───────────────────────────────────────────────────

class TextEncoding(str, DescribedEnum):
    """编码方式"""
    BASE64 = 1, "base64"
    HEX = 2, "hex"


# ── 日志配置 ───────────────────────────────────────────────────

class LogLevel(str, DescribedEnum):
    """日志级别"""
    DEBUG = 1, "DEBUG"
    INFO = 2, "INFO"
    WARNING = 3, "WARNING"
    ERROR = 4, "ERROR"
    CRITICAL = 5, "CRITICAL"


class LogSink(str, DescribedEnum):
    """日志输出目标"""
    STDERR = 1, "stderr"
    FILE = 2, "file"
    BOTH = 3, "both"
