#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流数据访问层
"""

from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from infra.mysql.models import Workflow, WorkflowNode, WorkflowEdge, WorkflowExecution, WorkflowStatus, NodeStatus
from schemas.workflow import Node as WorkflowNodeModel, Edge as WorkflowEdgeModel


class WorkflowRepository:
    """工作流数据访问类"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, workflow: Workflow) -> Workflow:
        """创建工作流"""
        self.session.add(workflow)
        await self.session.commit()
        await self.session.refresh(workflow)
        return workflow
    
    async def get(self, workflow_id: str) -> Optional[Workflow]:
        """获取工作流"""
        result = await self.session.execute(
            select(Workflow)
            .options(selectinload(Workflow.nodes), selectinload(Workflow.edges))
            .filter(Workflow.id == workflow_id)
        )
        return result.scalar_one_or_none()
    
    async def list(self, status: Optional[WorkflowStatus] = None, page: int = 1, page_size: int = 20) -> tuple[List[Workflow], int]:
        """获取工作流列表"""
        query = select(Workflow)
        
        if status:
            query = query.filter(Workflow.status == status)
        
        # 总数
        count_stmt = select(func.count()).select_from(query.subquery())
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar()
        
        # 分页（预加载节点和边，避免懒加载异常）
        data_query = (
            select(Workflow)
            .options(selectinload(Workflow.nodes), selectinload(Workflow.edges))
        )
        if status:
            data_query = data_query.filter(Workflow.status == status)
        data_query = data_query.offset((page - 1) * page_size).limit(page_size)
        result = await self.session.execute(data_query)
        workflows = result.scalars().unique().all()
        
        return workflows, total
    
    async def update(self, workflow: Workflow) -> Workflow:
        """更新工作流"""
        self.session.add(workflow)
        await self.session.commit()
        await self.session.refresh(workflow)
        return workflow
    
    async def delete(self, workflow_id: str) -> bool:
        """删除工作流"""
        workflow = await self.get(workflow_id)
        if not workflow:
            return False
        
        await self.session.delete(workflow)
        await self.session.commit()
        return True
    
    async def exists(self, workflow_id: str) -> bool:
        """检查工作流是否存在"""
        result = await self.session.execute(
            select(Workflow.id).filter(Workflow.id == workflow_id)
        )
        return result.scalar() is not None


class WorkflowNodeRepository:
    """工作流节点数据访问类"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_nodes(self, workflow_id: str, nodes: List[WorkflowNodeModel]):
        """批量创建节点"""
        db_nodes = []
        for node in nodes:
            db_node = WorkflowNode(
                id=node.id,
                workflow_id=workflow_id,
                type=node.type,
                data=node.data.model_dump(exclude_none=True) if hasattr(node.data, 'model_dump') else dict(node.data),
                position_x=node.position.x,
                position_y=node.position.y,
            )
            db_nodes.append(db_node)
        
        self.session.add_all(db_nodes)
        await self.session.commit()


class WorkflowEdgeRepository:
    """工作流边数据访问类"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_edges(self, workflow_id: str, edges: List[WorkflowEdgeModel]):
        """批量创建边"""
        db_edges = []
        for edge in edges:
            db_edge = WorkflowEdge(
                id=edge.id,
                workflow_id=workflow_id,
                source=edge.source,
                target=edge.target,
                source_handle=edge.source_handle,
                target_handle=edge.target_handle,
            )
            db_edges.append(db_edge)
        
        self.session.add_all(db_edges)
        await self.session.commit()


class WorkflowExecutionRepository:
    """工作流执行记录数据访问类"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, execution: WorkflowExecution) -> WorkflowExecution:
        """创建执行记录"""
        self.session.add(execution)
        await self.session.commit()
        await self.session.refresh(execution)
        return execution
    
    async def get(self, execution_id: str) -> Optional[WorkflowExecution]:
        """获取执行记录"""
        result = await self.session.execute(
            select(WorkflowExecution).filter(WorkflowExecution.id == execution_id)
        )
        return result.scalar_one_or_none()
    
    async def list(self, workflow_id: Optional[str] = None, page: int = 1, page_size: int = 20) -> tuple[List[WorkflowExecution], int]:
        """获取执行记录列表"""
        query = select(WorkflowExecution).order_by(WorkflowExecution.start_time.desc())
        
        if workflow_id:
            query = query.filter(WorkflowExecution.workflow_id == workflow_id)
        
        # 总数
        count_stmt = select(func.count()).select_from(query.subquery())
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar()
        
        # 分页
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.session.execute(query)
        executions = result.scalars().all()
        
        return executions, total
    
    async def update(self, execution: WorkflowExecution) -> WorkflowExecution:
        """更新执行记录"""
        self.session.add(execution)
        await self.session.commit()
        await self.session.refresh(execution)
        return execution
