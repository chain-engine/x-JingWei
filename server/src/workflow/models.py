#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流数据模型
定义Node、Edge、Workflow等核心数据结构
"""

from typing import Any, Optional, Literal
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class NodeType(str, Enum):
    """节点类型枚举"""


    START = "start"              # 开始节点
    END = "end"                  # 结束节点

    LLM = "llm"                  # LLM节点
    CODE = "code"                # 代码执行节点
    TRANSFORM = "transform"      # 数据转换节点

    CONDITION = "condition"      # 条件分支节点
    PARALLEL = "parallel"        # 并行节点
    AGGREGATE = "aggregate"      # 聚合节点

    HTTP = "http"                # HTTP请求节点
    DOCUMENT = "document"        # 文档处理节点

    DATABASE = "database"        # 数据库节点
    WEBSEARCH = "websearch"      # 网络搜索节点



class NodeStatus(str, Enum):
    """节点执行状态"""
    PENDING = "pending"          # 等待执行
    RUNNING = "running"          # 执行中
    SUCCESS = "success"          # 执行成功
    FAILED = "failed"            # 执行失败
    SKIPPED = "skipped"          # 被跳过
    TIMEOUT = "timeout"          # 执行超时


class WorkflowStatus(str, Enum):
    """工作流执行状态"""
    DRAFT = "draft"              # 草稿
    ACTIVE = "active"            # 已激活
    DISABLED = "disabled"        # 已禁用
    RUNNING = "running"          # 执行中
    COMPLETED = "completed"      # 执行完成
    FAILED = "failed"            # 执行失败
    PAUSED = "paused"            # 已暂停


class Position(BaseModel):
    """节点位置信息(用于前端画布)"""
    x: float = Field(default=0, description="X坐标")
    y: float = Field(default=0, description="Y坐标")
    
    model_config = ConfigDict(extra="allow")


class NodeData(BaseModel):
    """节点数据配置"""
    label: str = Field(default="", description="节点显示名称")
    description: Optional[str] = Field(default=None, description="节点描述")
    config: dict[str, Any] = Field(default_factory=dict, description="节点配置参数")
    inputs: dict[str, Any] = Field(default_factory=dict, description="输入变量定义")
    outputs: dict[str, Any] = Field(default_factory=dict, description="输出变量定义")
    
    model_config = ConfigDict(extra="allow")


class Node(BaseModel):
    """
    工作流节点模型
    
    对应前端画布上的一个节点，包含节点类型、配置和位置信息
    """
    id: str = Field(..., description="节点唯一标识")
    type: NodeType = Field(..., description="节点类型")
    position: Position = Field(default_factory=Position, description="节点位置")
    data: NodeData = Field(default_factory=NodeData, description="节点数据")
    
    # 运行时状态(非持久化)
    status: Optional[NodeStatus] = Field(default=None, exclude=True)
    output: Optional[Any] = Field(default=None, exclude=True)
    error: Optional[str] = Field(default=None, exclude=True)
    start_time: Optional[datetime] = Field(default=None, exclude=True)
    end_time: Optional[datetime] = Field(default=None, exclude=True)
    
    model_config = ConfigDict(extra="allow")
    
    def get_input_variables(self) -> list[str]:
        """获取节点输入变量列表(从模板中提取 {{var}} 格式)"""
        import re
        variables = set()
        config_str = str(self.data.config)
        # 匹配 {{variable}} 或 {{node_id.field}} 格式
        pattern = r'\{\{([^{}]+)\}\}'
        matches = re.findall(pattern, config_str)
        for match in matches:
            variables.add(match.strip())
        return list(variables)


class Edge(BaseModel):
    """
    工作流边模型(连接)
    
    定义节点之间的连接关系和数据流向
    """
    id: str = Field(..., description="边唯一标识")
    source: str = Field(..., description="源节点ID")
    target: str = Field(..., description="目标节点ID")
    source_handle: Optional[str] = Field(default=None, description="源节点连接点")
    target_handle: Optional[str] = Field(default=None, description="目标节点连接点")
    label: Optional[str] = Field(default=None, description="边标签(用于条件分支)")
    condition: Optional[str] = Field(default=None, description="条件表达式")
    data_mapping: Optional[dict[str, str]] = Field(default=None, description="数据映射配置")
    
    model_config = ConfigDict(extra="allow")
    
    def is_conditional(self) -> bool:
        """是否为条件边"""
        return self.condition is not None or self.label in ["true", "false", "yes", "no"]


class WorkflowVariable(BaseModel):
    """工作流变量定义"""
    name: str = Field(..., description="变量名")
    type: Literal["string", "number", "boolean", "array", "object", "any"] = Field(
        default="string", description="变量类型"
    )
    default: Optional[Any] = Field(default=None, description="默认值")
    description: Optional[str] = Field(default=None, description="变量描述")
    required: bool = Field(default=False, description="是否必填")
    
    model_config = ConfigDict(extra="allow")


class WorkflowMetadata(BaseModel):
    """工作流元数据"""
    author: Optional[str] = Field(default=None, description="作者")
    tags: list[str] = Field(default_factory=list, description="标签")
    category: Optional[str] = Field(default=None, description="分类")
    icon: Optional[str] = Field(default=None, description="图标")
    color: Optional[str] = Field(default=None, description="主题色")
    
    model_config = ConfigDict(extra="allow")


class Workflow(BaseModel):
    """
    工作流模型
    
    完整的工作流定义，包含节点、边和配置
    """
    id: Optional[str] = Field(default=None, description="工作流ID")
    name: str = Field(..., description="工作流名称")
    description: Optional[str] = Field(default=None, description="工作流描述")
    version: str = Field(default="1.0.0", description="版本号")
    
    # 核心结构
    nodes: list[Node] = Field(default_factory=list, description="节点列表")
    edges: list[Edge] = Field(default_factory=list, description="边列表")
    
    # 输入输出定义
    inputs: list[WorkflowVariable] = Field(default_factory=list, description="输入变量定义")
    outputs: list[WorkflowVariable] = Field(default_factory=list, description="输出变量定义")
    
    # 配置
    metadata: WorkflowMetadata = Field(default_factory=WorkflowMetadata, description="元数据")
    settings: dict[str, Any] = Field(default_factory=dict, description="执行配置")
    
    # 状态
    status: WorkflowStatus = Field(default=WorkflowStatus.DRAFT, description="状态")
    
    # 时间戳
    created_at: Optional[datetime] = Field(default=None, description="创建时间")
    updated_at: Optional[datetime] = Field(default=None, description="更新时间")
    
    model_config = ConfigDict(extra="allow")
    
    def get_start_nodes(self) -> list[Node]:
        """获取开始节点(入度为0的节点)"""
        target_ids = {edge.target for edge in self.edges}
        return [node for node in self.nodes if node.id not in target_ids]
    
    def get_end_nodes(self) -> list[Node]:
        """获取结束节点(出度为0的节点)"""
        source_ids = {edge.source for edge in self.edges}
        return [node for node in self.nodes if node.id not in source_ids]
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """根据ID获取节点"""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None
    
    def get_outgoing_edges(self, node_id: str) -> list[Edge]:
        """获取节点的出边"""
        return [edge for edge in self.edges if edge.source == node_id]
    
    def get_incoming_edges(self, node_id: str) -> list[Edge]:
        """获取节点的入边"""
        return [edge for edge in self.edges if edge.target == node_id]
    
    def get_neighbors(self, node_id: str) -> list[str]:
        """获取相邻节点ID列表"""
        return [edge.target for edge in self.get_outgoing_edges(node_id)]
    
    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式(用于前端)"""
        return self.model_dump(exclude_none=True)
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Workflow":
        """从字典创建工作流"""
        return cls.model_validate(data)


class ExecutionResult(BaseModel):
    """节点执行结果"""
    node_id: str = Field(..., description="节点ID")
    status: NodeStatus = Field(..., description="执行状态")
    output: Optional[Any] = Field(default=None, description="输出数据")
    error: Optional[str] = Field(default=None, description="错误信息")
    start_time: Optional[datetime] = Field(default=None, description="开始时间")
    end_time: Optional[datetime] = Field(default=None, description="结束时间")
    duration_ms: Optional[float] = Field(default=None, description="执行耗时(ms)")
    
    model_config = ConfigDict(extra="allow")


class WorkflowExecution(BaseModel):
    """工作流执行记录"""
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
