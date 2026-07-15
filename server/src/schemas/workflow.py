#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流 Schema 定义

包含工作流引擎的 API 请求入参和响应数据结构。
"""

from typing import Any, Optional, Literal
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

from .common import BaseSchema


class NodeType(str, Enum):
    START = "start"
    END = "end"
    LLM = "llm"
    CODE = "code"
    TRANSFORM = "transform"
    CONDITION = "condition"
    PARALLEL = "parallel"
    AGGREGATE = "aggregate"
    HTTP = "http"
    DOCUMENT = "document"
    DATABASE = "database"
    WEBSEARCH = "websearch"


class NodeStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"


class WorkflowStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    DISABLED = "disabled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class Position(BaseSchema):
    x: float = Field(default=0, description="X坐标")
    y: float = Field(default=0, description="Y坐标")

    model_config = ConfigDict(extra="allow")


class NodeData(BaseSchema):
    label: str = Field(default="", description="节点显示名称")
    description: Optional[str] = Field(default=None, description="节点描述")
    config: dict[str, Any] = Field(default_factory=dict, description="节点配置参数")
    inputs: dict[str, Any] = Field(default_factory=dict, description="输入变量定义")
    outputs: dict[str, Any] = Field(default_factory=dict, description="输出变量定义")

    model_config = ConfigDict(extra="allow")


class Node(BaseSchema):
    id: str = Field(..., description="节点唯一标识")
    type: NodeType = Field(..., description="节点类型")
    position: Position = Field(default_factory=Position, description="节点位置")
    data: NodeData = Field(default_factory=NodeData, description="节点数据")

    status: Optional[NodeStatus] = Field(default=None, exclude=True)
    output: Optional[Any] = Field(default=None, exclude=True)
    error: Optional[str] = Field(default=None, exclude=True)
    start_time: Optional[datetime] = Field(default=None, exclude=True)
    end_time: Optional[datetime] = Field(default=None, exclude=True)

    model_config = ConfigDict(extra="allow")

    def get_input_variables(self) -> list[str]:
        import re
        variables = set()
        config_str = str(self.data.config)
        pattern = r'\{\{([^{}]+)\}\}'
        matches = re.findall(pattern, config_str)
        for match in matches:
            variables.add(match.strip())
        return list(variables)


class Edge(BaseSchema):
    id: str = Field(..., description="边唯一标识")
    source: str = Field(..., description="源节点ID")
    target: str = Field(..., description="目标节点ID")
    source_handle: Optional[str] = Field(default=None, description="源节点连接点")
    target_handle: Optional[str] = Field(default=None, description="目标节点连接点")
    label: Optional[str] = Field(default=None, description="边标签")
    condition: Optional[str] = Field(default=None, description="条件表达式")
    data_mapping: Optional[dict[str, str]] = Field(default=None, description="数据映射配置")

    model_config = ConfigDict(extra="allow")

    def is_conditional(self) -> bool:
        return self.condition is not None or self.label in ["true", "false", "yes", "no"]


class WorkflowVariable(BaseSchema):
    name: str = Field(..., description="变量名")
    type: Literal["string", "number", "boolean", "array", "object", "any"] = Field(
        default="string", description="变量类型"
    )
    default: Optional[Any] = Field(default=None, description="默认值")
    description: Optional[str] = Field(default=None, description="变量描述")
    required: bool = Field(default=False, description="是否必填")

    model_config = ConfigDict(extra="allow")


class WorkflowMetadata(BaseSchema):
    author: Optional[str] = Field(default=None, description="作者")
    tags: list[str] = Field(default_factory=list, description="标签")
    category: Optional[str] = Field(default=None, description="分类")
    icon: Optional[str] = Field(default=None, description="图标")
    color: Optional[str] = Field(default=None, description="主题色")

    model_config = ConfigDict(extra="allow")


class Workflow(BaseSchema):
    id: Optional[str] = Field(default=None, description="工作流ID")
    name: str = Field(..., description="工作流名称")
    description: Optional[str] = Field(default=None, description="工作流描述")
    version: str = Field(default="1.0.0", description="版本号")

    nodes: list[Node] = Field(default_factory=list, description="节点列表")
    edges: list[Edge] = Field(default_factory=list, description="边列表")

    inputs: list[WorkflowVariable] = Field(default_factory=list, description="输入变量定义")
    outputs: list[WorkflowVariable] = Field(default_factory=list, description="输出变量定义")

    metadata: WorkflowMetadata = Field(default_factory=WorkflowMetadata, description="元数据")
    settings: dict[str, Any] = Field(default_factory=dict, description="执行配置")

    status: WorkflowStatus = Field(default=WorkflowStatus.DRAFT, description="状态")

    created_at: Optional[datetime] = Field(default=None, description="创建时间")
    updated_at: Optional[datetime] = Field(default=None, description="更新时间")

    model_config = ConfigDict(extra="allow")

    def get_start_nodes(self) -> list[Node]:
        target_ids = {edge.target for edge in self.edges}
        return [node for node in self.nodes if node.id not in target_ids]

    def get_end_nodes(self) -> list[Node]:
        source_ids = {edge.source for edge in self.edges}
        return [node for node in self.nodes if node.id not in source_ids]

    def get_node(self, node_id: str) -> Optional[Node]:
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    def get_outgoing_edges(self, node_id: str) -> list[Edge]:
        return [edge for edge in self.edges if edge.source == node_id]

    def get_incoming_edges(self, node_id: str) -> list[Edge]:
        return [edge for edge in self.edges if edge.target == node_id]

    def get_neighbors(self, node_id: str) -> list[str]:
        return [edge.target for edge in self.get_outgoing_edges(node_id)]

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(exclude_none=True)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Workflow":
        return cls.model_validate(data)


class ExecutionResult(BaseSchema):
    node_id: str = Field(..., description="节点ID")
    status: NodeStatus = Field(..., description="执行状态")
    output: Optional[Any] = Field(default=None, description="输出数据")
    error: Optional[str] = Field(default=None, description="错误信息")
    start_time: Optional[datetime] = Field(default=None, description="开始时间")
    end_time: Optional[datetime] = Field(default=None, description="结束时间")
    duration_ms: Optional[float] = Field(default=None, description="执行耗时(ms)")

    model_config = ConfigDict(extra="allow")


class WorkflowExecution(BaseSchema):
    id: Optional[str] = Field(default=None, description="执行ID")
    workflow_id: str = Field(..., description="工作流ID")
    status: WorkflowStatus = Field(..., description="执行状态")
    inputs: dict[str, Any] = Field(default_factory=dict, description="输入数据")
    outputs: dict[str, Any] = Field(default_factory=dict, description="输出数据")
    node_results: dict[str, ExecutionResult] = Field(default_factory=dict, description="节点执行结果")
    error: Optional[str] = Field(default=None, description="错误信息")
    start_time: Optional[datetime] = Field(default=None, description="开始时间")
    end_time: Optional[datetime] = Field(default=None, description="结束时间")
    duration_ms: Optional[float] = Field(default=None, description="总耗时(ms)")

    model_config = ConfigDict(extra="allow")