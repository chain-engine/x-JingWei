#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流API接口

API接口层：极薄，只做参数转发，不写业务逻辑
"""

from typing import Any, Optional
from fastapi import APIRouter, Request, Query

from core.logger import logger
from core.response import success_response
from core.container import container
from services.workflow_service import WorkflowService
from schemas.workflow import (
    CreateWorkflowRequest,
    UpdateWorkflowRequest,
    ExecuteWorkflowRequest,
    WorkflowStatus
)

router = APIRouter()


# ==================== 工作流CRUD接口 ====================

@router.post("")
async def create_workflow(request: Request, body: CreateWorkflowRequest) -> dict[str, Any]:
    """创建工作流"""
    request_id = getattr(request.state, "request_id", None)
    logger.info(f"Create workflow requested: {request_id}, name: {body.name}")

    workflow_service = container.resolve(WorkflowService)
    result = await workflow_service.create_workflow(
        name=body.name,
        description=body.description,
        nodes=body.nodes,
        edges=body.edges
    )

    return success_response(data=result, message="工作流创建成功", request_id=request_id)


@router.get("")
async def list_workflows(
    request: Request,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: Optional[WorkflowStatus] = Query(None, description="状态筛选")
) -> dict[str, Any]:
    """获取工作流列表"""
    request_id = getattr(request.state, "request_id", None)
    logger.info(f"List workflows requested: {request_id}, page: {page}, page_size: {page_size}")

    workflow_service = container.resolve(WorkflowService)
    result = await workflow_service.list_workflows(page=page, page_size=page_size, status=status)

    return success_response(data=result, request_id=request_id)


@router.get("/{workflow_id}")
async def get_workflow(request: Request, workflow_id: str) -> dict[str, Any]:
    """获取工作流详情"""
    request_id = getattr(request.state, "request_id", None)
    logger.info(f"Get workflow requested: {request_id}, workflow_id: {workflow_id}")

    workflow_service = container.resolve(WorkflowService)
    result = await workflow_service.get_workflow(workflow_id=workflow_id)

    return success_response(data=result, request_id=request_id)


@router.put("/{workflow_id}")
async def update_workflow(
    request: Request,
    workflow_id: str,
    body: UpdateWorkflowRequest
) -> dict[str, Any]:
    """更新工作流"""
    request_id = getattr(request.state, "request_id", None)
    logger.info(f"Update workflow requested: {request_id}, workflow_id: {workflow_id}")

    workflow_service = container.resolve(WorkflowService)
    result = await workflow_service.update_workflow(
        workflow_id=workflow_id,
        name=body.name,
        description=body.description,
        nodes=body.nodes,
        edges=body.edges,
        status=body.status
    )

    return success_response(data=result, message="工作流更新成功", request_id=request_id)


@router.delete("/{workflow_id}")
async def delete_workflow(request: Request, workflow_id: str) -> dict[str, Any]:
    """删除工作流"""
    request_id = getattr(request.state, "request_id", None)
    logger.info(f"Delete workflow requested: {request_id}, workflow_id: {workflow_id}")

    workflow_service = container.resolve(WorkflowService)
    await workflow_service.delete_workflow(workflow_id=workflow_id)

    return success_response(message="工作流删除成功", request_id=request_id)


# ==================== 工作流执行接口 ====================

@router.post("/{workflow_id}/execute")
async def execute_workflow(
    request: Request,
    workflow_id: str,
    body: ExecuteWorkflowRequest = None
) -> dict[str, Any]:
    """执行工作流"""
    request_id = getattr(request.state, "request_id", None)
    logger.info(f"Execute workflow requested: {request_id}, workflow_id: {workflow_id}")

    workflow_service = container.resolve(WorkflowService)
    result = await workflow_service.execute_workflow(
        workflow_id=workflow_id,
        inputs=body.inputs if body else {}
    )

    return success_response(data=result, message="工作流执行完成", request_id=request_id)


@router.post("/{workflow_id}/validate")
async def validate_workflow(request: Request, workflow_id: str) -> dict[str, Any]:
    """验证工作流"""
    request_id = getattr(request.state, "request_id", None)
    logger.info(f"Validate workflow requested: {request_id}, workflow_id: {workflow_id}")

    workflow_service = container.resolve(WorkflowService)
    result = await workflow_service.validate_workflow(workflow_id=workflow_id)

    if result.get("valid"):
        return success_response(data=result, message="工作流验证通过", request_id=request_id)
    else:
        return success_response(data=result, message="工作流验证失败", request_id=request_id)


@router.get("/{workflow_id}/execution-plan")
async def get_execution_plan(request: Request, workflow_id: str) -> dict[str, Any]:
    """获取工作流执行计划"""
    request_id = getattr(request.state, "request_id", None)
    logger.info(f"Get execution plan requested: {request_id}, workflow_id: {workflow_id}")

    workflow_service = container.resolve(WorkflowService)
    result = await workflow_service.get_execution_plan(workflow_id=workflow_id)

    return success_response(data=result, request_id=request_id)


# ==================== 节点类型接口 ====================

@router.get("/node-types/list")
async def list_node_types(request: Request) -> dict[str, Any]:
    """获取所有支持的节点类型"""
    request_id = getattr(request.state, "request_id", None)
    logger.info(f"List node types requested: {request_id}")

    workflow_service = container.resolve(WorkflowService)
    result = workflow_service.list_node_types()

    return success_response(data=result, request_id=request_id)


@router.get("/node-types/{node_type}")
async def get_node_type(request: Request, node_type: str) -> dict[str, Any]:
    """获取节点类型详情"""
    request_id = getattr(request.state, "request_id", None)
    logger.info(f"Get node type requested: {request_id}, node_type: {node_type}")

    workflow_service = container.resolve(WorkflowService)
    result = workflow_service.get_node_type(node_type=node_type)

    return success_response(data=result, request_id=request_id)


# ==================== 执行记录接口 ====================

@router.get("/executions/list")
async def list_executions(
    request: Request,
    workflow_id: Optional[str] = Query(None, description="工作流ID筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
) -> dict[str, Any]:
    """获取执行记录列表"""
    request_id = getattr(request.state, "request_id", None)
    logger.info(f"List executions requested: {request_id}, workflow_id: {workflow_id}")

    workflow_service = container.resolve(WorkflowService)
    result = await workflow_service.list_executions(
        workflow_id=workflow_id, page=page, page_size=page_size
    )

    return success_response(data=result, request_id=request_id)


@router.get("/executions/{execution_id}")
async def get_execution(request: Request, execution_id: str) -> dict[str, Any]:
    """获取执行记录详情"""
    request_id = getattr(request.state, "request_id", None)
    logger.info(f"Get execution requested: {request_id}, execution_id: {execution_id}")

    workflow_service = container.resolve(WorkflowService)
    result = await workflow_service.get_execution(execution_id=execution_id)

    return success_response(data=result, request_id=request_id)