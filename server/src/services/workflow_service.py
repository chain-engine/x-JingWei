#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流业务服务

核心业务逻辑层：处理工作流规则、事务编排、多仓储联动
"""

from typing import Any, Optional, List, Dict
from datetime import datetime

from core.logger import logger
from core.exceptions import BusinessError, ValidationError
from infras.mysql import get_async_db
from workflow import Workflow, Node, Edge, WorkflowExecutor, NodeRegistry
from workflow import NodeType, WorkflowStatus, NodeStatus
from schemas.workflow import WorkflowVariable, WorkflowMetadata, Position, NodeData
from models.workflow import (
    Workflow as DBWorkflow,
    WorkflowNode,
    WorkflowEdge,
    WorkflowExecution as DBWorkflowExecution,
    WorkflowStatus as DBWorkflowStatus,
    NodeStatus as DBNodeStatus
)
from repositories.workflow_repository import (
    WorkflowRepository,
    WorkflowNodeRepository,
    WorkflowEdgeRepository,
    WorkflowExecutionRepository
)


class WorkflowService:
    """工作流业务服务"""

    def __init__(self) -> None:
        """初始化工作流服务"""
        self._executor = WorkflowExecutor(max_workers=10)
        logger.info("Workflow service initialized")

    async def create_workflow(
        self,
        name: str,
        description: Optional[str] = None,
        nodes: Optional[List[Dict[str, Any]]] = None,
        edges: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """创建工作流

        Args:
            name: 工作流名称
            description: 工作流描述
            nodes: 节点列表
            edges: 边列表

        Returns:
            Dict[str, Any]: 创建结果

        Raises:
            ValidationError: 参数校验失败
            BusinessError: 业务错误
        """
        async with get_async_db() as session:
            workflow_id = f"wf_{datetime.now().strftime('%Y%m%d%H%M%S')}_{id(self) % 10000}"

            parsed_nodes = [Node.model_validate(n) for n in nodes] if nodes else []
            parsed_edges = [Edge.model_validate(e) for e in edges] if edges else []

            workflow = Workflow(
                id=workflow_id,
                name=name,
                description=description,
                nodes=parsed_nodes,
                edges=parsed_edges,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

            valid, error = self._executor.validate_workflow(workflow)
            if not valid:
                raise ValidationError(f"工作流验证失败: {error}")

            workflow_repo = WorkflowRepository(session)
            node_repo = WorkflowNodeRepository(session)
            edge_repo = WorkflowEdgeRepository(session)

            db_workflow = DBWorkflow(
                id=workflow_id,
                name=name,
                description=description,
                status=DBWorkflowStatus.DRAFT,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

            await workflow_repo.create(db_workflow)

            if parsed_nodes:
                await node_repo.create_nodes(workflow_id, parsed_nodes)

            if parsed_edges:
                await edge_repo.create_edges(workflow_id, parsed_edges)

            logger.info(f"创建工作流: {workflow_id}, 名称: {name}")

            return workflow.to_dict()

    async def list_workflows(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[WorkflowStatus] = None
    ) -> Dict[str, Any]:
        """获取工作流列表

        Args:
            page: 页码
            page_size: 每页数量
            status: 状态筛选

        Returns:
            Dict[str, Any]: 工作流列表
        """
        async with get_async_db() as session:
            workflow_repo = WorkflowRepository(session)
            workflows, total = await workflow_repo.list(status=status, page=page, page_size=page_size)

            return {
                "items": [w.to_dict() for w in workflows],
                "total": total,
                "page": page,
                "page_size": page_size
            }

    async def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """获取工作流详情

        Args:
            workflow_id: 工作流ID

        Returns:
            Dict[str, Any]: 工作流详情

        Raises:
            BusinessError: 工作流不存在
        """
        async with get_async_db() as session:
            workflow_repo = WorkflowRepository(session)
            workflow = await workflow_repo.get(workflow_id)

            if not workflow:
                raise BusinessError(f"工作流不存在: {workflow_id}", code=404)

            return workflow.to_dict()

    async def update_workflow(
        self,
        workflow_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        nodes: Optional[List[Dict[str, Any]]] = None,
        edges: Optional[List[Dict[str, Any]]] = None,
        status: Optional[DBWorkflowStatus] = None
    ) -> Dict[str, Any]:
        """更新工作流

        Args:
            workflow_id: 工作流ID
            name: 工作流名称
            description: 工作流描述
            nodes: 节点列表
            edges: 边列表
            status: 工作流状态

        Returns:
            Dict[str, Any]: 更新结果

        Raises:
            BusinessError: 工作流不存在
            ValidationError: 参数校验失败
        """
        async with get_async_db() as session:
            workflow_repo = WorkflowRepository(session)
            workflow = await workflow_repo.get(workflow_id)

            if not workflow:
                raise BusinessError(f"工作流不存在: {workflow_id}", code=404)

            if name is not None:
                workflow.name = name
            if description is not None:
                workflow.description = description
            if status is not None:
                workflow.status = status

            workflow.updated_at = datetime.now()

            if nodes is not None or edges is not None:
                temp_nodes = [Node.model_validate(n) for n in nodes] if nodes else workflow.nodes
                temp_edges = [Edge.model_validate(e) for e in edges] if edges else workflow.edges

                temp_workflow = Workflow(
                    id=workflow_id,
                    name=workflow.name,
                    description=workflow.description,
                    nodes=temp_nodes,
                    edges=temp_edges,
                    created_at=workflow.created_at,
                    updated_at=workflow.updated_at
                )

                valid, error = self._executor.validate_workflow(temp_workflow)
                if not valid:
                    raise ValidationError(f"工作流验证失败: {error}")

            await workflow_repo.update(workflow)

            logger.info(f"更新工作流: {workflow_id}")

            return workflow.to_dict()

    async def delete_workflow(self, workflow_id: str) -> None:
        """删除工作流

        Args:
            workflow_id: 工作流ID

        Raises:
            BusinessError: 工作流不存在
        """
        async with get_async_db() as session:
            workflow_repo = WorkflowRepository(session)
            success = await workflow_repo.delete(workflow_id)

            if not success:
                raise BusinessError(f"工作流不存在: {workflow_id}", code=404)

            logger.info(f"删除工作流: {workflow_id}")

    async def execute_workflow(self, workflow_id: str, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行工作流

        Args:
            workflow_id: 工作流ID
            inputs: 输入参数

        Returns:
            Dict[str, Any]: 执行结果

        Raises:
            BusinessError: 工作流不存在或已禁用
        """
        async with get_async_db() as session:
            workflow_repo = WorkflowRepository(session)
            execution_repo = WorkflowExecutionRepository(session)

            db_workflow = await workflow_repo.get(workflow_id)
            if not db_workflow:
                raise BusinessError(f"工作流不存在: {workflow_id}", code=404)

            if db_workflow.status == DBWorkflowStatus.DISABLED:
                raise BusinessError("工作流已禁用，无法执行")

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

            logger.info(f"执行工作流: {workflow_id}, 输入: {inputs}")

            execution = await self._executor.execute(
                workflow=workflow,
                inputs=inputs or {}
            )

            serialized_results = {
                k: v.model_dump(mode="json", exclude_none=True)
                if hasattr(v, "model_dump") else v
                for k, v in execution.node_results.items()
            }

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

            return {
                "execution_id": execution.id,
                "status": execution.status,
                "inputs": execution.inputs,
                "outputs": execution.outputs,
                "node_results": serialized_results,
                "error": execution.error,
                "start_time": execution.start_time.isoformat() if execution.start_time else None,
                "end_time": execution.end_time.isoformat() if execution.end_time else None,
                "duration_ms": execution.duration_ms
            }

    async def validate_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """验证工作流

        Args:
            workflow_id: 工作流ID

        Returns:
            Dict[str, Any]: 验证结果

        Raises:
            BusinessError: 工作流不存在
        """
        async with get_async_db() as session:
            workflow_repo = WorkflowRepository(session)
            db_workflow = await workflow_repo.get(workflow_id)

            if not db_workflow:
                raise BusinessError(f"工作流不存在: {workflow_id}", code=404)

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

            valid, error = self._executor.validate_workflow(workflow)

            if valid:
                plan = self._executor.get_execution_plan(workflow)
                return {
                    "valid": True,
                    "execution_plan": plan
                }
            else:
                return {
                    "valid": False,
                    "error": error
                }

    async def get_execution_plan(self, workflow_id: str) -> Dict[str, Any]:
        """获取工作流执行计划

        Args:
            workflow_id: 工作流ID

        Returns:
            Dict[str, Any]: 执行计划

        Raises:
            BusinessError: 工作流不存在
        """
        async with get_async_db() as session:
            workflow_repo = WorkflowRepository(session)
            db_workflow = await workflow_repo.get(workflow_id)

            if not db_workflow:
                raise BusinessError(f"工作流不存在: {workflow_id}", code=404)

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

            return self._executor.get_execution_plan(workflow)

    def list_node_types(self) -> List[Dict[str, Any]]:
        """获取所有支持的节点类型

        Returns:
            List[Dict[str, Any]]: 节点类型列表
        """
        node_types = []
        for node_type in NodeType:
            metadata = NodeRegistry.get_node_metadata(node_type)
            if metadata:
                node_types.append({
                    "type": node_type.value,
                    **metadata
                })
        return node_types

    def get_node_type(self, node_type: str) -> Dict[str, Any]:
        """获取节点类型详情

        Args:
            node_type: 节点类型

        Returns:
            Dict[str, Any]: 节点类型详情

        Raises:
            BusinessError: 未知的节点类型
        """
        try:
            nt = NodeType(node_type)
        except ValueError:
            raise BusinessError(f"未知的节点类型: {node_type}", code=404)

        metadata = NodeRegistry.get_node_metadata(nt)
        if not metadata:
            raise BusinessError(f"节点类型信息不存在: {node_type}", code=404)

        return {
            "type": node_type,
            **metadata
        }

    async def list_executions(
        self,
        workflow_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """获取执行记录列表

        Args:
            workflow_id: 工作流ID筛选
            page: 页码
            page_size: 每页数量

        Returns:
            Dict[str, Any]: 执行记录列表
        """
        async with get_async_db() as session:
            execution_repo = WorkflowExecutionRepository(session)
            executions, total = await execution_repo.list(
                workflow_id=workflow_id, page=page, page_size=page_size
            )

            return {
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

    async def get_execution(self, execution_id: str) -> Dict[str, Any]:
        """获取执行记录详情

        Args:
            execution_id: 执行记录ID

        Returns:
            Dict[str, Any]: 执行记录详情

        Raises:
            BusinessError: 执行记录不存在
        """
        async with get_async_db() as session:
            execution_repo = WorkflowExecutionRepository(session)
            execution = await execution_repo.get(execution_id)

            if not execution:
                raise BusinessError(f"执行记录不存在: {execution_id}", code=404)

            return {
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