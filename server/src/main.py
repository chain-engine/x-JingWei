#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用主入口
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
import uvicorn

from core.logger import logger
from core.config import settings
from core.middleware import setup_middleware
from core.exceptions import (
    BaseException as CoreBaseException,
    BusinessError,
    SystemError,
    ValidationError as CoreValidationError,
    NotFoundError,
    UnauthorizedError,
    ForbiddenError,
    ConflictError,
    RateLimitError,
    DocumentError,
    EmbeddingError,
    VectorStoreError,
    RetrievalError,
    GenerationError,
    DatabaseError,
    ExternalServiceError,
    ConfigurationError
)
from constants.constants import (
    HTTP_STATUS_OK,
    HTTP_STATUS_BAD_REQUEST,
    HTTP_STATUS_UNAUTHORIZED,
    HTTP_STATUS_FORBIDDEN,
    HTTP_STATUS_NOT_FOUND,
    HTTP_STATUS_CONFLICT,
    HTTP_STATUS_TOO_MANY_REQUESTS,
    HTTP_STATUS_INTERNAL_SERVER_ERROR,
    CODE_SUCCESS,
    CODE_VALIDATION_ERROR,
    CODE_UNAUTHORIZED,
    CODE_FORBIDDEN,
    CODE_NOT_FOUND,
    CODE_RATE_LIMIT_EXCEEDED,
    CODE_SERVER_ERROR,
    HEADER_REQUEST_ID
)
from api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理

    Args:
        app: FastAPI应用实例

    Yields:
        None
    """
    logger.info("Application starting up...")

    # 初始化数据库
    try:
        from infra.mysql import async_init_db
        await async_init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    # 初始化依赖注入容器
    from core.container import container

    # 注册服务
    from services.llm_service import LLMService
    from services.document_service import DocumentService
    from services.workflow_service import WorkflowService

    container.register(LLMService, LLMService)
    container.register(DocumentService, DocumentService)
    container.register(WorkflowService, WorkflowService)

    # 注册仓库
    from repositories.document_repository import DocumentRepository
    container.register(DocumentRepository, DocumentRepository)

    logger.info("Dependency injection container initialized")

    yield

    logger.info("Application shutting down...")


def create_app() -> FastAPI:
    """创建FastAPI应用实例

    Returns:
        FastAPI: 应用实例
    """
    app = FastAPI(
        title=settings.api_docs.title,
        description=settings.api_docs.description,
        version=settings.api_docs.version,
        docs_url=settings.api_docs.docs_url if settings.api_docs.enabled else None,
        redoc_url=settings.api_docs.redoc_url if settings.api_docs.enabled else None,
        openapi_url=settings.api_docs.openapi_url if settings.api_docs.enabled else None,
        lifespan=lifespan
    )

    # 配置中间件
    setup_middleware(app)

    # 注册路由
    app.include_router(api_router)

    # 注册异常处理器
    register_exception_handlers(app)

    return app


def register_exception_handlers(app: FastAPI) -> None:
    """注册异常处理器

    Args:
        app: FastAPI应用实例
    """

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError
    ) -> JSONResponse:
        """请求参数校验异常处理

        Args:
            request: 请求对象
            exc: 异常对象

        Returns:
            JSONResponse: 错误响应
        """
        request_id = getattr(request.state, "request_id", None)
        logger.warning(f"Validation error: {exc.errors()}")

        errors = []
        for error in exc.errors():
            errors.append({
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"]
            })

        return JSONResponse(
            status_code=HTTP_STATUS_BAD_REQUEST,
            content={
                "code": CODE_VALIDATION_ERROR,
                "message": "Validation failed",
                "data": {"errors": errors},
                "request_id": request_id
            }
        )

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_exception_handler(
        request: Request,
        exc: RateLimitExceeded
    ) -> JSONResponse:
        """限流异常处理

        Args:
            request: 请求对象
            exc: 异常对象

        Returns:
            JSONResponse: 错误响应
        """
        request_id = getattr(request.state, "request_id", None)
        logger.warning(f"Rate limit exceeded: {exc.detail}")

        return JSONResponse(
            status_code=HTTP_STATUS_TOO_MANY_REQUESTS,
            content={
                "code": CODE_RATE_LIMIT_EXCEEDED,
                "message": "Rate limit exceeded",
                "data": {"detail": exc.detail},
                "request_id": request_id
            }
        )

    @app.exception_handler(CoreValidationError)
    async def core_validation_exception_handler(
        request: Request,
        exc: CoreValidationError
    ) -> JSONResponse:
        """核心校验异常处理

        Args:
            request: 请求对象
            exc: 异常对象

        Returns:
            JSONResponse: 错误响应
        """
        request_id = getattr(request.state, "request_id", None)
        logger.warning(f"Core validation error: {exc.message}")

        return JSONResponse(
            status_code=HTTP_STATUS_BAD_REQUEST,
            content={
                "code": exc.code,
                "message": exc.message,
                "detail": exc.detail,
                "request_id": request_id
            }
        )

    @app.exception_handler(UnauthorizedError)
    async def unauthorized_exception_handler(
        request: Request,
        exc: UnauthorizedError
    ) -> JSONResponse:
        """未授权异常处理

        Args:
            request: 请求对象
            exc: 异常对象

        Returns:
            JSONResponse: 错误响应
        """
        request_id = getattr(request.state, "request_id", None)
        logger.warning(f"Unauthorized error: {exc.message}")

        return JSONResponse(
            status_code=HTTP_STATUS_UNAUTHORIZED,
            content={
                "code": exc.code,
                "message": exc.message,
                "detail": exc.detail,
                "request_id": request_id
            }
        )

    @app.exception_handler(ForbiddenError)
    async def forbidden_exception_handler(
        request: Request,
        exc: ForbiddenError
    ) -> JSONResponse:
        """禁止访问异常处理

        Args:
            request: 请求对象
            exc: 异常对象

        Returns:
            JSONResponse: 错误响应
        """
        request_id = getattr(request.state, "request_id", None)
        logger.warning(f"Forbidden error: {exc.message}")

        return JSONResponse(
            status_code=HTTP_STATUS_FORBIDDEN,
            content={
                "code": exc.code,
                "message": exc.message,
                "detail": exc.detail,
                "request_id": request_id
            }
        )

    @app.exception_handler(NotFoundError)
    async def not_found_exception_handler(
        request: Request,
        exc: NotFoundError
    ) -> JSONResponse:
        """资源未找到异常处理

        Args:
            request: 请求对象
            exc: 异常对象

        Returns:
            JSONResponse: 错误响应
        """
        request_id = getattr(request.state, "request_id", None)
        logger.warning(f"Not found error: {exc.message}")

        return JSONResponse(
            status_code=HTTP_STATUS_NOT_FOUND,
            content={
                "code": exc.code,
                "message": exc.message,
                "detail": exc.detail,
                "request_id": request_id
            }
        )

    @app.exception_handler(ConflictError)
    async def conflict_exception_handler(
        request: Request,
        exc: ConflictError
    ) -> JSONResponse:
        """资源冲突异常处理

        Args:
            request: 请求对象
            exc: 异常对象

        Returns:
            JSONResponse: 错误响应
        """
        request_id = getattr(request.state, "request_id", None)
        logger.warning(f"Conflict error: {exc.message}")

        return JSONResponse(
            status_code=HTTP_STATUS_CONFLICT,
            content={
                "code": exc.code,
                "message": exc.message,
                "detail": exc.detail,
                "request_id": request_id
            }
        )

    @app.exception_handler(RateLimitError)
    async def rate_limit_error_handler(
        request: Request,
        exc: RateLimitError
    ) -> JSONResponse:
        """限流错误异常处理

        Args:
            request: 请求对象
            exc: 异常对象

        Returns:
            JSONResponse: 错误响应
        """
        request_id = getattr(request.state, "request_id", None)
        logger.warning(f"Rate limit error: {exc.message}")

        return JSONResponse(
            status_code=HTTP_STATUS_TOO_MANY_REQUESTS,
            content={
                "code": exc.code,
                "message": exc.message,
                "detail": exc.detail,
                "request_id": request_id
            }
        )

    @app.exception_handler(SystemError)
    async def system_error_handler(
        request: Request,
        exc: SystemError
    ) -> JSONResponse:
        """系统错误异常处理

        Args:
            request: 请求对象
            exc: 异常对象

        Returns:
            JSONResponse: 错误响应
        """
        request_id = getattr(request.state, "request_id", None)
        logger.error(f"System error: {exc.message}", exc_info=True)

        return JSONResponse(
            status_code=HTTP_STATUS_INTERNAL_SERVER_ERROR,
            content={
                "code": exc.code,
                "message": exc.message,
                "detail": exc.detail,
                "request_id": request_id
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request,
        exc: Exception
    ) -> JSONResponse:
        """通用异常处理

        Args:
            request: 请求对象
            exc: 异常对象

        Returns:
            JSONResponse: 错误响应
        """
        request_id = getattr(request.state, "request_id", None)
        logger.error(f"Unexpected error: {exc}", exc_info=True)

        return JSONResponse(
            status_code=HTTP_STATUS_INTERNAL_SERVER_ERROR,
            content={
                "code": CODE_SERVER_ERROR,
                "message": "Internal server error",
                "detail": str(exc) if settings.app_debug else None,
                "request_id": request_id
            }
        )


app = create_app()


def main() -> None:
    """主函数"""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.app_environment}")
    logger.info(f"Debug mode: {settings.app_debug}")
    logger.info(f"Server: {settings.server.host}:{settings.server.port}")

    uvicorn.run(
        "src.main:app",
        host=settings.server.host,
        port=settings.server.port,
        workers=settings.server.workers,
        reload=settings.server.reload if settings.app_debug else False,
        log_level=settings.logging.level.lower()
    )


if __name__ == "__main__":
    main()
