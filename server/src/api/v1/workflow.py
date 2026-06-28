#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流API接口
提供工作流的CRUD和执行接口
"""

from typing import Any, Optional, List
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger import logger
from core.response import success_response, error_response
from core.exceptions import BusinessError, ValidationError
from src.infra.mysql import get_async_db as get_db_session
from workflow import Workflow, Node, Edge, NodeType, WorkflowStatus, NodeStatus
from workflow import WorkflowExecutor, NodeRegistry
from workflow.models import WorkflowVariable, WorkflowMetadata, Position, NodeData
from models.workflow import Workflow as DBWorkflow, WorkflowNode, WorkflowEdge, WorkflowExecution as DBWorkflowExecution
from repositories.workflow_repository import (
    WorkflowRepository,
    WorkflowNodeRepository,
    WorkflowEdgeRepository,
    WorkflowExecutionRepository
)

router = APIRouter()

# 全局执行器
_executor = WorkflowExecutor(max_workers=10)


# ==================== 请求/响应模型 ====================

class CreateWorkflowRequest(BaseModel):
    """创建工作流请求"""
    name: str = Field(..., min_length=1, max_length=100, description="工作流名称")
    description: Optional[str] = Field(default=None, description="工作流描述")
    nodes: list[dict] = Field(default_factory=list, description="节点列表")
    edges: list[dict] = Field(default_factory=list, description="边列表")


class UpdateWorkflowRequest(BaseModel):
    """更新工作流请求"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None)
    nodes: Optional[list[dict]] = Field(default=None)
    edges: Optional[list[dict]] = Field(default=None)
    status: Optional[WorkflowStatus] = Field(default=None)


class ExecuteWorkflowRequest(BaseModel):
    """执行工作流请求"""
    inputs: dict[str, Any] = Field(default_factory=dict, description="输入参数")


class NodeTypeInfo(BaseModel):
    """节点类型信息"""
    type: str = Field(..., description="节点类型")
    label: str = Field(..., description="显示名称")
    description: str = Field(..., description="描述")
    icon: str = Field(..., description="图标")
    color: str = Field(..., description="颜色")
    inputs: list[dict] = Field(default_factory=list, description="输入定义")
    outputs: list[dict] = Field(default_factory=list, description="输出定义")


# ==================== 工作流CRUD接口 ====================

@router.post("", response_model=dict)
async def create_workflow(
    request: CreateWorkflowRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """
    创建工作流
    
    - **name**: 工作流名称
    - **description**: 工作流描述
    - **nodes**: 节点列表(可选，可后续编辑)
    - **edges**: 边列表(可选，可后续编辑)
    """
    try:
        workflow_id = f"wf_{datetime.now().strftime('%Y%m%d%H%M%S')}_{id(request) % 10000}"
        
        # 解析节点和边
        nodes = [Node.model_validate(n) for n in request.nodes] if request.nodes else []
        edges = [Edge.model_validate(e) for e in request.edges] if request.edges else []
        
        workflow = Workflow(
            id=workflow_id,
            name=request.name,
            description=request.description,
            nodes=nodes,
            edges=edges,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # 验证工作流
        valid, error = _executor.validate_workflow(workflow)
        if not valid:
            raise ValidationError(f"工作流验证失败: {error}")
        
        # 保存到数据库
        workflow_repo = WorkflowRepository(session)
        node_repo = WorkflowNodeRepository(session)
        edge_repo = WorkflowEdgeRepository(session)
        
        # 创建工作流
        db_workflow = DBWorkflow(
            id=workflow_id,
            name=request.name,
            description=request.description,
            status=WorkflowStatus.DRAFT,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        await workflow_repo.create(db_workflow)
        
        # 创建节点
        if nodes:
            await node_repo.create_nodes(workflow_id, nodes)
        
        # 创建边
        if edges:
            await edge_repo.create_edges(workflow_id, edges)
        
        logger.info(f"创建工作流: {workflow_id}, 名称: {request.name}")
        
        return success_response(
            data=workflow.to_dict(),
            message="工作流创建成功"
        )
        
    except ValidationError as e:
        raise e
    except Exception as e:
        logger.error(f"创建工作流失败: {e}")
        raise BusinessError(f"创建工作流失败: {str(e)}")


@router.get("", response_model=dict)
async def list_workflows(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: Optional[WorkflowStatus] = Query(None, description="状态筛选"),
    session: AsyncSession = Depends(get_db_session)
):
    """获取工作流列表"""
    try:
        workflow_repo = WorkflowRepository(session)
        workflows, total = await workflow_repo.list(status=status, page=page, page_size=page_size)
        
        return success_response(
            data={
                "items": [w.to_dict() for w in workflows],
                "total": total,
                "page": page,
                "page_size": page_size
            }
        )
        
    except Exception as e:
        logger.error(f"获取工作流列表失败: {e}")
        raise BusinessError(f"获取工作流列表失败: {str(e)}")


@router.get("/{workflow_id}", response_model=dict)
async def get_workflow(
    workflow_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """获取工作流详情"""
    try:
        workflow_repo = WorkflowRepository(session)
        workflow = await workflow_repo.get(workflow_id)
        
        if not workflow:
            raise BusinessError(f"工作流不存在: {workflow_id}", code=404)
        
        return success_response(data=workflow.to_dict())
        
    except BusinessError:
        raise
    except Exception as e:
        logger.error(f"获取工作流失败: {e}")
        raise BusinessError(f"获取工作流失败: {str(e)}")


@router.put("/{workflow_id}", response_model=dict)
async def update_workflow(
    workflow_id: str,
    request: UpdateWorkflowRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """更新工作流"""
    try:
        workflow_repo = WorkflowRepository(session)
        workflow = await workflow_repo.get(workflow_id)
        
        if not workflow:
            raise BusinessError(f"工作流不存在: {workflow_id}", code=404)
        
        # 更新字段
        if request.name is not None:
            workflow.name = request.name
        if request.description is not None:
            workflow.description = request.description
        if request.status is not None:
            workflow.status = request.status
        
        workflow.updated_at = datetime.now()
        
        # 重新验证（如果更新了节点或边）
        if request.nodes is not None or request.edges is not None:
            # 构建临时工作流对象用于验证
            temp_nodes = [Node.model_validate(n) for n in request.nodes] if request.nodes else workflow.nodes
            temp_edges = [Edge.model_validate(e) for e in request.edges] if request.edges else workflow.edges
            
            temp_workflow = Workflow(
                id=workflow_id,
                name=workflow.name,
                description=workflow.description,
                nodes=temp_nodes,
                edges=temp_edges,
                created_at=workflow.created_at,
                updated_at=workflow.updated_at
            )
            
            valid, error = _executor.validate_workflow(temp_workflow)
            if not valid:
                raise ValidationError(f"工作流验证失败: {error}")
        
        await workflow_repo.update(workflow)
        
        logger.info(f"更新工作流: {workflow_id}")
        
        return success_response(
            data=workflow.to_dict(),
            message="工作流更新成功"
        )
        
    except (BusinessError, ValidationError):
        raise
    except Exception as e:
        logger.error(f"更新工作流失败: {e}")
        raise BusinessError(f"更新工作流失败: {str(e)}")


@router.delete("/{workflow_id}", response_model=dict)
async def delete_workflow(
    workflow_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """删除工作流"""
    try:
        workflow_repo = WorkflowRepository(session)
        success = await workflow_repo.delete(workflow_id)
        
        if not success:
            raise BusinessError(f"工作流不存在: {workflow_id}", code=404)
        
        logger.info(f"删除工作流: {workflow_id}")
        
        return success_response(message="工作流删除成功")
        
    except BusinessError:
        raise
    except Exception as e:
        logger.error(f"删除工作流失败: {e}")
        raise BusinessError(f"删除工作流失败: {str(e)}")


# ==================== 工作流执行接口 ====================

@router.post("/{workflow_id}/execute", response_model=dict)
async def execute_workflow(
    workflow_id: str,
    request: ExecuteWorkflowRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """
    执行工作流
    
    - **inputs**: 输入参数，键值对形式
    """
    try:
        workflow_repo = WorkflowRepository(session)
        execution_repo = WorkflowExecutionRepository(session)
        
        # 获取工作流
        db_workflow = await workflow_repo.get(workflow_id)
        if not db_workflow:
            raise BusinessError(f"工作流不存在: {workflow_id}", code=404)
        
        # 检查状态
        if db_workflow.status == WorkflowStatus.DISABLED:
            raise BusinessError("工作流已禁用，无法执行")
        
        # 构建工作流对象
        workflow = Workflow(
            id=db_workflow.id,
            name=db_workflow.name,
            description=db_workflow.description,
            nodes=[
                Node(
                    id=node.id,
                    type=node.type,
                    data=NodeData(**node.data),
                    position=Position(x=node.position_x, y=node.position_y)
                )
                for node in db_workflow.nodes
            ],
            edges=[
                Edge(
                    id=edge.id,
                    source=edge.source,
                    target=edge.target,
                    source_handle=edge.source_handle,
                    target_handle=edge.target_handle
                )
                for edge in db_workflow.edges
            ],
            status=db_workflow.status,
            created_at=db_workflow.created_at,
            updated_at=db_workflow.updated_at
        )
        
        logger.info(f"执行工作流: {workflow_id}, 输入: {request.inputs}")
        
        # 执行工作流
        execution = await _executor.execute(
            workflow=workflow,
            inputs=request.inputs
        )
        
        # 序列化节点结果为 JSON 安全的字典
        serialized_results = {
            k: v.model_dump(mode="json", exclude_none=True)
            if hasattr(v, "model_dump") else v
            for k, v in execution.node_results.items()
        }
        
        # 保存执行记录
        db_execution = DBWorkflowExecution(
            id=execution.id,
            workflow_id=workflow_id,
            status=execution.status,
            inputs=execution.inputs,
            outputs=execution.outputs,
            node_results=serialized_results,
            error=execution.error,
            start_time=execution.start_time,
            end_time=execution.end_time,
            duration_ms=execution.duration_ms
        )
        
        await execution_repo.create(db_execution)
        
        return success_response(
            data={
                "execution_id": execution.id,
                "status": execution.status,
                "inputs": execution.inputs,
                "outputs": execution.outputs,
                "node_results": serialized_results,
                "error": execution.error,
                "start_time": execution.start_time.isoformat() if execution.start_time else None,
                "end_time": execution.end_time.isoformat() if execution.end_time else None,
                "duration_ms": execution.duration_ms
            },
            message="工作流执行完成"
        )
        
    except BusinessError:
        raise
    except Exception as e:
        logger.error(f"执行工作流失败: {e}")
        raise BusinessError(f"执行工作流失败: {str(e)}")


@router.post("/{workflow_id}/validate", response_model=dict)
async def validate_workflow(
    workflow_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """验证工作流"""
    try:
        workflow_repo = WorkflowRepository(session)
        db_workflow = await workflow_repo.get(workflow_id)
        
        if not db_workflow:
            raise BusinessError(f"工作流不存在: {workflow_id}", code=404)
        
        # 构建工作流对象
        workflow = Workflow(
            id=db_workflow.id,
            name=db_workflow.name,
            description=db_workflow.description,
            nodes=[
                Node(
                    id=node.id,
                    type=node.type,
                    data=NodeData(**node.data),
                    position=Position(x=node.position_x, y=node.position_y)
                )
                for node in db_workflow.nodes
            ],
            edges=[
                Edge(
                    id=edge.id,
                    source=edge.source,
                    target=edge.target,
                    source_handle=edge.source_handle,
                    target_handle=edge.target_handle
                )
                for edge in db_workflow.edges
            ],
            status=db_workflow.status,
            created_at=db_workflow.created_at,
            updated_at=db_workflow.updated_at
        )
        
        valid, error = _executor.validate_workflow(workflow)
        
        if valid:
            # 生成执行计划
            plan = _executor.get_execution_plan(workflow)
            return success_response(
                data={
                    "valid": True,
                    "execution_plan": plan
                },
                message="工作流验证通过"
            )
        else:
            return success_response(
                data={
                    "valid": False,
                    "error": error
                },
                message="工作流验证失败"
            )
        
    except BusinessError:
        raise
    except Exception as e:
        logger.error(f"验证工作流失败: {e}")
        raise BusinessError(f"验证工作流失败: {str(e)}")


@router.get("/{workflow_id}/execution-plan", response_model=dict)
async def get_execution_plan(
    workflow_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """获取工作流执行计划"""
    try:
        workflow_repo = WorkflowRepository(session)
        db_workflow = await workflow_repo.get(workflow_id)
        
        if not db_workflow:
            raise BusinessError(f"工作流不存在: {workflow_id}", code=404)
        
        # 构建工作流对象
        workflow = Workflow(
            id=db_workflow.id,
            name=db_workflow.name,
            description=db_workflow.description,
            nodes=[
                Node(
                    id=node.id,
                    type=node.type,
                    data=NodeData(**node.data),
                    position=Position(x=node.position_x, y=node.position_y)
                )
                for node in db_workflow.nodes
            ],
            edges=[
                Edge(
                    id=edge.id,
                    source=edge.source,
                    target=edge.target,
                    source_handle=edge.source_handle,
                    target_handle=edge.target_handle
                )
                for edge in db_workflow.edges
            ],
            status=db_workflow.status,
            created_at=db_workflow.created_at,
            updated_at=db_workflow.updated_at
        )
        
        plan = _executor.get_execution_plan(workflow)
        
        return success_response(data=plan)
        
    except BusinessError:
        raise
    except Exception as e:
        logger.error(f"获取执行计划失败: {e}")
        raise BusinessError(f"获取执行计划失败: {str(e)}")


# ==================== 节点类型接口 ====================

@router.get("/node-types/list", response_model=dict)
async def list_node_types():
    """获取所有支持的节点类型"""
    try:
        node_types = []
        for node_type in NodeType:
            metadata = NodeRegistry.get_node_metadata(node_type)
            if metadata:
                node_types.append({
                    "type": node_type.value,
                    **metadata
                })
        
        return success_response(data=node_types)
        
    except Exception as e:
        logger.error(f"获取节点类型失败: {e}")
        raise BusinessError(f"获取节点类型失败: {str(e)}")


@router.get("/node-types/{node_type}", response_model=dict)
async def get_node_type(node_type: str):
    """获取节点类型详情"""
    try:
        try:
            nt = NodeType(node_type)
        except ValueError:
            raise BusinessError(f"未知的节点类型: {node_type}", code=404)
        
        metadata = NodeRegistry.get_node_metadata(nt)
        if not metadata:
            raise BusinessError(f"节点类型信息不存在: {node_type}", code=404)
        
        return success_response(data={
            "type": node_type,
            **metadata
        })
        
    except BusinessError:
        raise
    except Exception as e:
        logger.error(f"获取节点类型失败: {e}")
        raise BusinessError(f"获取节点类型失败: {str(e)}")


# ==================== 执行记录接口 ====================

@router.get("/executions/list", response_model=dict)
async def list_executions(
    workflow_id: Optional[str] = Query(None, description="工作流ID筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session)
):
    """获取执行记录列表"""
    try:
        execution_repo = WorkflowExecutionRepository(session)
        executions, total = await execution_repo.list(workflow_id=workflow_id, page=page, page_size=page_size)
        
        return success_response(
            data={
                "items": [
                    {
                        "execution_id": e.id,
                        "workflow_id": e.workflow_id,
                        "status": e.status.value if e.status else None,
                        "start_time": e.start_time.isoformat() if e.start_time else None,
                        "end_time": e.end_time.isoformat() if e.end_time else None,
                        "duration_ms": e.duration_ms,
                        "error": e.error
                    }
                    for e in executions
                ],
                "total": total,
                "page": page,
                "page_size": page_size
            }
        )
        
    except Exception as e:
        logger.error(f"获取执行记录失败: {e}")
        raise BusinessError(f"获取执行记录失败: {str(e)}")


@router.get("/executions/{execution_id}", response_model=dict)
async def get_execution(
    execution_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """获取执行记录详情"""
    try:
        execution_repo = WorkflowExecutionRepository(session)
        execution = await execution_repo.get(execution_id)
        
        if not execution:
            raise BusinessError(f"执行记录不存在: {execution_id}", code=404)
        
        return success_response(
            data={
                "execution_id": execution.id,
                "workflow_id": execution.workflow_id,
                "status": execution.status.value if execution.status else None,
                "inputs": execution.inputs,
                "outputs": execution.outputs,
                "node_results": execution.node_results,
                "error": execution.error,
                "start_time": execution.start_time.isoformat() if execution.start_time else None,
                "end_time": execution.end_time.isoformat() if execution.end_time else None,
                "duration_ms": execution.duration_ms
            }
        )
        
    except BusinessError:
        raise
    except Exception as e:
        logger.error(f"获取执行记录失败: {e}")
        raise BusinessError(f"获取执行记录失败: {str(e)}")
