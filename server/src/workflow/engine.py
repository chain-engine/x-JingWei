#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DAG执行引擎
实现拓扑排序、并行执行、依赖解析等核心功能
"""

import asyncio
from typing import Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict, deque
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import json

from core.logger import logger
from schemas.workflow import (
    Workflow, Node, Edge, NodeType, NodeStatus, WorkflowStatus,
    ExecutionResult, WorkflowExecution
)


@dataclass
class ExecutionContext:
    """执行上下文"""
    workflow: Workflow
    variables: dict[str, Any] = field(default_factory=dict)
    node_outputs: dict[str, Any] = field(default_factory=dict)
    execution_id: Optional[str] = None
    
    def get_variable(self, name: str) -> Any:
        """获取变量值"""
        # 支持 {{node_id.output}} 和 {{variable}} 两种格式
        if "." in name:
            parts = name.split(".")
            node_id = parts[0]
            field_name = ".".join(parts[1:])
            if node_id in self.node_outputs:
                output = self.node_outputs[node_id]
                if isinstance(output, dict):
                    return output.get(field_name)
                elif hasattr(output, field_name):
                    return getattr(output, field_name)
        return self.variables.get(name)
    
    def set_variable(self, name: str, value: Any) -> None:
        """设置变量值"""
        self.variables[name] = value
    
    def set_node_output(self, node_id: str, output: Any) -> None:
        """设置节点输出"""
        self.node_outputs[node_id] = output
    
    def resolve_template(self, template: str) -> str:
        """解析模板中的变量引用 {{variable}}"""
        import re
        
        def replace_var(match):
            var_name = match.group(1).strip()
            value = self.get_variable(var_name)
            if value is None:
                return match.group(0)  # 保持原样
            return str(value)
        
        pattern = r'\{\{([^{}]+)\}\}'
        return re.sub(pattern, replace_var, template)
    
    def resolve_dict(self, data: dict[str, Any]) -> dict[str, Any]:
        """递归解析字典中的模板变量"""
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = self.resolve_template(value)
            elif isinstance(value, dict):
                result[key] = self.resolve_dict(value)
            elif isinstance(value, list):
                result[key] = [self.resolve_template(v) if isinstance(v, str) else v for v in value]
            else:
                result[key] = value
        return result


class DAGEngine:
    """
    DAG执行引擎
    
    负责工作流的拓扑排序、依赖分析和执行调度
    """
    
    def __init__(self, max_workers: int = 10):
        """
        初始化DAG引擎
        
        Args:
            max_workers: 最大并行执行线程数
        """
        self.max_workers = max_workers
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        
    def topological_sort(self, workflow: Workflow) -> list[str]:
        """
        拓扑排序
        
        使用Kahn算法对工作流节点进行拓扑排序，确保依赖节点先执行
        
        Args:
            workflow: 工作流对象
            
        Returns:
            list[str]: 排序后的节点ID列表
            
        Raises:
            ValueError: 如果存在循环依赖
        """
        # 构建入度表和邻接表
        in_degree = {node.id: 0 for node in workflow.nodes}
        adjacency = defaultdict(list)
        
        for edge in workflow.edges:
            adjacency[edge.source].append(edge.target)
            in_degree[edge.target] += 1
        
        # 找到所有入度为0的节点
        queue = deque([node_id for node_id, degree in in_degree.items() if degree == 0])
        result = []
        
        while queue:
            node_id = queue.popleft()
            result.append(node_id)
            
            # 减少相邻节点的入度
            for neighbor in adjacency[node_id]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # 检查是否存在循环依赖
        if len(result) != len(workflow.nodes):
            # 找出循环中的节点
            remaining = [node_id for node_id, degree in in_degree.items() if degree > 0]
            raise ValueError(f"工作流存在循环依赖，涉及节点: {remaining}")
        
        return result
    
    def get_execution_levels(self, workflow: Workflow) -> list[list[str]]:
        """
        获取执行层级
        
        将节点按执行层级分组，同层级节点可以并行执行
        
        Args:
            workflow: 工作流对象
            
        Returns:
            list[list[str]]: 每层级的节点ID列表
        """
        in_degree = {node.id: 0 for node in workflow.nodes}
        adjacency = defaultdict(list)
        
        for edge in workflow.edges:
            adjacency[edge.source].append(edge.target)
            in_degree[edge.target] += 1
        
        levels = []
        current_level = [node_id for node_id, degree in in_degree.items() if degree == 0]
        
        while current_level:
            levels.append(current_level)
            next_level = []
            
            for node_id in current_level:
                for neighbor in adjacency[node_id]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        next_level.append(neighbor)
            
            current_level = next_level
        
        return levels
    
    def get_parallel_groups(self, workflow: Workflow) -> list[set[str]]:
        """
        获取可并行执行的节点组
        
        分析工作流，返回可以并行执行的节点组
        
        Args:
            workflow: 工作流对象
            
        Returns:
            list[set[str]]: 可并行执行的节点ID组
        """
        return self.get_execution_levels(workflow)
    
    def validate_workflow(self, workflow: Workflow) -> tuple[bool, Optional[str]]:
        """
        验证工作流有效性
        
        检查:
        1. 是否有开始节点
        2. 是否有结束节点
        3. 是否存在循环依赖
        4. 节点ID是否唯一
        5. 边的连接是否有效
        
        Args:
            workflow: 工作流对象
            
        Returns:
            tuple[bool, Optional[str]]: (是否有效, 错误信息)
        """
        # 检查节点ID唯一性
        node_ids = [node.id for node in workflow.nodes]
        if len(node_ids) != len(set(node_ids)):
            duplicates = [nid for nid in node_ids if node_ids.count(nid) > 1]
            return False, f"存在重复的节点ID: {duplicates}"
        
        # 检查是否有开始节点
        start_nodes = workflow.get_start_nodes()
        if not start_nodes:
            return False, "工作流缺少开始节点(入度为0的节点)"
        
        # 检查是否有结束节点
        end_nodes = workflow.get_end_nodes()
        if not end_nodes:
            return False, "工作流缺少结束节点(出度为0的节点)"
        
        # 检查边的有效性
        for edge in workflow.edges:
            if edge.source not in node_ids:
                return False, f"边引用了不存在的源节点: {edge.source}"
            if edge.target not in node_ids:
                return False, f"边引用了不存在的目标节点: {edge.target}"
        
        # 检查循环依赖
        try:
            self.topological_sort(workflow)
        except ValueError as e:
            return False, str(e)
        
        return True, None
    
    def analyze_dependencies(self, workflow: Workflow) -> dict[str, list[str]]:
        """
        分析节点依赖关系
        
        Args:
            workflow: 工作流对象
            
        Returns:
            dict[str, list[str]]: 每个节点的依赖列表
        """
        dependencies = defaultdict(list)
        
        for edge in workflow.edges:
            dependencies[edge.target].append(edge.source)
        
        return dict(dependencies)
    
    def get_execution_plan(self, workflow: Workflow) -> dict[str, Any]:
        """
        生成执行计划
        
        Args:
            workflow: 工作流对象
            
        Returns:
            dict: 执行计划详情
        """
        try:
            sorted_nodes = self.topological_sort(workflow)
            levels = self.get_execution_levels(workflow)
            dependencies = self.analyze_dependencies(workflow)
            parallel_groups = self.get_parallel_groups(workflow)
            
            return {
                "valid": True,
                "sorted_order": sorted_nodes,
                "execution_levels": levels,
                "parallel_groups": [list(group) for group in parallel_groups],
                "dependencies": dependencies,
                "start_nodes": [n.id for n in workflow.get_start_nodes()],
                "end_nodes": [n.id for n in workflow.get_end_nodes()],
                "total_nodes": len(workflow.nodes),
                "total_edges": len(workflow.edges),
                "estimated_parallelism": max(len(group) for group in levels) if levels else 0
            }
        except ValueError as e:
            return {
                "valid": False,
                "error": str(e)
            }
    
    def find_critical_path(self, workflow: Workflow, node_weights: Optional[dict[str, float]] = None) -> list[str]:
        """
        查找关键路径
        
        找出工作流中耗时最长的执行路径
        
        Args:
            workflow: 工作流对象
            node_weights: 节点权重(执行时间)，默认为1
            
        Returns:
            list[str]: 关键路径上的节点ID列表
        """
        if node_weights is None:
            node_weights = {node.id: 1.0 for node in workflow.nodes}
        
        sorted_nodes = self.topological_sort(workflow)
        
        # 计算到每个节点的最长路径
        longest_path = {node_id: 0.0 for node_id in sorted_nodes}
        predecessors = {node_id: None for node_id in sorted_nodes}
        
        for node_id in sorted_nodes:
            incoming_edges = workflow.get_incoming_edges(node_id)
            for edge in incoming_edges:
                source = edge.source
                new_weight = longest_path[source] + node_weights.get(source, 1.0)
                if new_weight > longest_path[node_id]:
                    longest_path[node_id] = new_weight
                    predecessors[node_id] = source
        
        # 找到最长路径的终点
        end_node = max(longest_path, key=longest_path.get)
        
        # 回溯构建路径
        path = []
        current = end_node
        while current is not None:
            path.append(current)
            current = predecessors[current]
        
        return list(reversed(path))


class ExecutionGraph:
    """执行图"""
    
    def __init__(self, workflow: Workflow, engine: DAGEngine):
        self.workflow = workflow
        self.engine = engine
        self.context = ExecutionContext(workflow=workflow)
        self.results: dict[str, ExecutionResult] = {}
        self._lock = asyncio.Lock()
        
    async def execute_node(self, node_id: str, executor) -> ExecutionResult:
        """执行单个节点"""
        node = self.workflow.get_node(node_id)
        if not node:
            return ExecutionResult(
                node_id=node_id,
                status=NodeStatus.FAILED,
                error=f"节点不存在: {node_id}"
            )
        
        start_time = datetime.now()
        
        try:
            # 更新节点状态
            node.status = NodeStatus.RUNNING
            node.start_time = start_time
            
            logger.info(f"开始执行节点: {node_id} (类型: {node.type})")
            
            # 执行节点
            result = await executor.execute_node_instance(node, self.context)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds() * 1000
            
            # 更新结果
            result.start_time = start_time
            result.end_time = end_time
            result.duration_ms = duration
            
            # 保存输出到上下文
            if result.status == NodeStatus.SUCCESS and result.output is not None:
                self.context.set_node_output(node_id, result.output)
            
            node.status = result.status
            node.output = result.output
            node.end_time = end_time
            
            async with self._lock:
                self.results[node_id] = result
            
            logger.info(f"节点执行完成: {node_id}, 状态: {result.status}, 耗时: {duration:.2f}ms")
            
            return result
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds() * 1000
            
            error_result = ExecutionResult(
                node_id=node_id,
                status=NodeStatus.FAILED,
                error=str(e),
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration
            )
            
            node.status = NodeStatus.FAILED
            node.error = str(e)
            node.end_time = end_time
            
            async with self._lock:
                self.results[node_id] = error_result
            
            logger.error(f"节点执行失败: {node_id}, 错误: {e}")
            
            return error_result
    
    def get_ready_nodes(self) -> list[str]:
        """获取准备就绪的节点(所有依赖已执行完成)"""
        ready = []
        
        for node in self.workflow.nodes:
            if node.id in self.results:
                continue  # 已执行
            
            # 检查所有依赖是否已完成
            incoming = self.workflow.get_incoming_edges(node.id)
            dependencies_completed = all(
                self.results.get(edge.source, ExecutionResult(node_id=edge.source, status=NodeStatus.PENDING)).status == NodeStatus.SUCCESS
                for edge in incoming
            )
            
            if dependencies_completed:
                ready.append(node.id)
        
        return ready
    
    def is_completed(self) -> bool:
        """检查是否所有节点都已执行完成"""
        return len(self.results) == len(self.workflow.nodes)
    
    def has_failed(self) -> bool:
        """检查是否有节点执行失败"""
        return any(
            result.status == NodeStatus.FAILED 
            for result in self.results.values()
        )
