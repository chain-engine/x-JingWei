#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流 ORM 实体模型

纯数据表映射模型，仅定义字段、表关联关系，无任何查询、业务逻辑。
"""

from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, String, Text, Integer, DateTime, Enum, JSON, ForeignKey
from sqlalchemy.orm import relationship

from models.base import Base


class WorkflowStatus(PyEnum):
    """工作流状态枚举"""

    DRAFT = "draft"
    ACTIVE = "active"
    DISABLED = "disabled"


class NodeType(PyEnum):
    """节点类型枚举"""

    START = "start"
    END = "end"
    LLM = "llm"
    CODE = "code"
    CONDITION = "condition"
    HTTP = "http"
    TRANSFORM = "transform"
    PARALLEL = "parallel"
    AGGREGATE = "aggregate"
    DOCUMENT = "document"
    DATABASE = "database"


class NodeStatus(PyEnum):
    """节点状态枚举"""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class Workflow(Base):
    """工作流模型"""

    __tablename__ = "workflows"

    id = Column(String(64), primary_key=True, index=True, comment="工作流ID")
    name = Column(String(100), nullable=False, comment="工作流名称")
    description = Column(Text, nullable=True, comment="工作流描述")
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.DRAFT, comment="工作流状态")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    nodes = relationship("WorkflowNode", back_populates="workflow", cascade="all, delete-orphan")
    edges = relationship("WorkflowEdge", back_populates="workflow", cascade="all, delete-orphan")
    executions = relationship("WorkflowExecution", back_populates="workflow")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value if self.status else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
        }


class WorkflowNode(Base):
    """工作流节点模型"""

    __tablename__ = "workflow_nodes"

    id = Column(String(64), primary_key=True, index=True, comment="节点ID")
    workflow_id = Column(String(64), ForeignKey("workflows.id"), nullable=False, comment="所属工作流ID")
    type = Column(Enum(NodeType), nullable=False, comment="节点类型")
    data = Column(JSON, nullable=False, comment="节点数据")
    position_x = Column(Integer, nullable=False, default=0, comment="位置X")
    position_y = Column(Integer, nullable=False, default=0, comment="位置Y")

    workflow = relationship("Workflow", back_populates="nodes")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "type": self.type.value if self.type else None,
            "data": self.data,
            "position": {"x": self.position_x, "y": self.position_y},
        }


class WorkflowEdge(Base):
    """工作流边模型"""

    __tablename__ = "workflow_edges"

    id = Column(String(64), primary_key=True, index=True, comment="边ID")
    workflow_id = Column(String(64), ForeignKey("workflows.id"), nullable=False, comment="所属工作流ID")
    source = Column(String(64), nullable=False, comment="源节点ID")
    target = Column(String(64), nullable=False, comment="目标节点ID")
    source_handle = Column(String(32), nullable=True, comment="源节点输出端口")
    target_handle = Column(String(32), nullable=True, comment="目标节点输入端口")

    workflow = relationship("Workflow", back_populates="edges")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "source": self.source,
            "target": self.target,
            "sourceHandle": self.source_handle,
            "targetHandle": self.target_handle,
        }


class WorkflowExecution(Base):
    """工作流执行记录模型"""

    __tablename__ = "workflow_executions"

    id = Column(String(64), primary_key=True, index=True, comment="执行记录ID")
    workflow_id = Column(String(64), ForeignKey("workflows.id"), nullable=False, comment="工作流ID")
    status = Column(Enum(NodeStatus), default=NodeStatus.PENDING, comment="执行状态")
    inputs = Column(JSON, nullable=False, default=dict, comment="输入参数")
    outputs = Column(JSON, nullable=True, comment="输出结果")
    node_results = Column(JSON, nullable=True, comment="各节点执行结果")
    error = Column(Text, nullable=True, comment="错误信息")
    start_time = Column(DateTime, nullable=True, comment="开始时间")
    end_time = Column(DateTime, nullable=True, comment="结束时间")
    duration_ms = Column(Integer, nullable=True, comment="执行耗时(毫秒)")

    workflow = relationship("Workflow", back_populates="executions")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "workflow_id": self.workflow_id,
            "status": self.status.value if self.status else None,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "node_results": self.node_results,
            "error": self.error,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": self.duration_ms,
        }