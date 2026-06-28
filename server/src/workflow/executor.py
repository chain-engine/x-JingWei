#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流执行器
整合DAG引擎和节点执行，提供完整的工作流执行能力
"""

import uuid
import asyncio
from typing import Any, Optional, Callable
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from core.logger import logger
from .models import (
    Workflow, Node, Edge, NodeType, NodeStatus, WorkflowStatus,
    ExecutionResult, WorkflowExecution
)
from .engine import DAGEngine, ExecutionContext, ExecutionGraph
from .nodes import NodeRegistry, BaseNode


class WorkflowExecutor:
    """
    工作流执行器
    
    负责执行完整的工作流，支持串行和并行执行模式
    """
    
    def __init__(self, max_workers: int = 10):
        """
        初始化执行器
        
        Args:
            max_workers: 最大并行执行线程数
        """
        self.engine = DAGEngine(max_workers=max_workers)
        self.max_workers = max_workers
        self._running_executions: dict[str, WorkflowExecution] = {}
        
    async def execute(
        self,
        workflow: Workflow,
        inputs: Optional[dict[str, Any]] = None,
        execution_id: Optional[str] = None,
        on_node_start: Optional[Callable[[str], None]] = None,
        on_node_complete: Optional[Callable[[str, ExecutionResult], None]] = None,
        on_node_error: Optional[Callable[[str, str], None]] = None
    ) -> WorkflowExecution:
        """
        执行工作流
        
        Args:
            workflow: 工作流对象
            inputs: 输入参数
            execution_id: 执行ID(自动生成如果不提供)
            on_node_start: 节点开始回调
            on_node_complete: 节点完成回调
            on_node_error: 节点错误回调
            
        Returns:
            WorkflowExecution: 执行结果
        """
        # 验证工作流
        valid, error = self.engine.validate_workflow(workflow)
        if not valid:
            raise ValueError(f"工作流验证失败: {error}")
        
        # 创建执行记录
        execution_id = execution_id or str(uuid.uuid4())
        execution = WorkflowExecution(
            id=execution_id,
            workflow_id=workflow.id or "unknown",
            status=WorkflowStatus.RUNNING,
            inputs=inputs or {},
            start_time=datetime.now()
        )
        
        self._running_executions[execution_id] = execution
        
        try:
            logger.info(f"开始执行工作流: {workflow.name} (执行ID: {execution_id})")
            
            # 创建执行图
            graph = ExecutionGraph(workflow, self.engine)
            graph.context.execution_id = execution_id
            
            # 注入输入变量
            if inputs:
                for key, value in inputs.items():
                    graph.context.set_variable(key, value)
            
            # 执行工作流
            await self._execute_graph(
                graph,
                on_node_start=on_node_start,
                on_node_complete=on_node_complete,
                on_node_error=on_node_error
            )
            
            # 收集结果
            execution.node_results = graph.results
            execution.outputs = self._collect_outputs(workflow, graph.context)
            
            # 检查是否有失败
            if graph.has_failed():
                execution.status = WorkflowStatus.FAILED
                failed_nodes = [
                    node_id for node_id, result in graph.results.items()
                    if result.status == NodeStatus.FAILED
                ]
                execution.error = f"以下节点执行失败: {failed_nodes}"
            else:
                execution.status = WorkflowStatus.COMPLETED
            
            execution.end_time = datetime.now()
            execution.duration_ms = (execution.end_time - execution.start_time).total_seconds() * 1000
            
            logger.info(f"工作流执行完成: {workflow.name}, 状态: {execution.status}, 耗时: {execution.duration_ms:.2f}ms")
            
        except Exception as e:
            logger.error(f"工作流执行异常: {e}")
            execution.status = WorkflowStatus.FAILED
            execution.error = str(e)
            execution.end_time = datetime.now()
            if execution.start_time:
                execution.duration_ms = (execution.end_time - execution.start_time).total_seconds() * 1000
        finally:
            if execution_id in self._running_executions:
                del self._running_executions[execution_id]
        
        return execution
    
    async def _execute_graph(
        self,
        graph: ExecutionGraph,
        on_node_start: Optional[Callable[[str], None]] = None,
        on_node_complete: Optional[Callable[[str, ExecutionResult], None]] = None,
        on_node_error: Optional[Callable[[str, str], None]] = None
    ) -> None:
        """
        执行工作流图
        
        支持并行执行就绪的节点
        """
        workflow = graph.workflow
        
        while not graph.is_completed():
            # 获取准备就绪的节点
            ready_nodes = graph.get_ready_nodes()
            
            if not ready_nodes:
                # 检查是否有节点正在运行
                running_nodes = [
                    node for node in workflow.nodes
                    if node.status == NodeStatus.RUNNING
                ]
                if not running_nodes:
                    # 没有就绪节点也没有运行中的节点，但还没完成，说明有问题
                    break
                # 等待一小段时间再检查
                await asyncio.sleep(0.1)
                continue
            
            # 并行执行所有就绪节点
            tasks = []
            for node_id in ready_nodes:
                task = self._execute_node_with_callbacks(
                    graph, node_id,
                    on_node_start=on_node_start,
                    on_node_complete=on_node_complete,
                    on_node_error=on_node_error
                )
                tasks.append(task)
            
            # 等待所有就绪节点执行完成
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _execute_node_with_callbacks(
        self,
        graph: ExecutionGraph,
        node_id: str,
        on_node_start: Optional[Callable[[str], None]] = None,
        on_node_complete: Optional[Callable[[str, ExecutionResult], None]] = None,
        on_node_error: Optional[Callable[[str, str], None]] = None
    ) -> ExecutionResult:
        """执行节点并触发回调"""
        node = graph.workflow.get_node(node_id)
        
        if on_node_start:
            try:
                on_node_start(node_id)
            except Exception as e:
                logger.warning(f"节点开始回调异常: {e}")
        
        result = await graph.execute_node(node_id, self)
        
        if result.status == NodeStatus.SUCCESS:
            if on_node_complete:
                try:
                    on_node_complete(node_id, result)
                except Exception as e:
                    logger.warning(f"节点完成回调异常: {e}")
        else:
            if on_node_error:
                try:
                    on_node_error(node_id, result.error or "未知错误")
                except Exception as e:
                    logger.warning(f"节点错误回调异常: {e}")
        
        return result
    
    async def execute_node_instance(self, node: Node, context: ExecutionContext) -> ExecutionResult:
        """
        执行单个节点实例
        
        这是ExecutionGraph.execute_node的回调接口
        
        Args:
            node: 节点实例
            context: 执行上下文
            
        Returns:
            ExecutionResult: 执行结果
        """
        # 获取节点处理器
        node_handler = NodeRegistry.build(node.type)
        
        if not node_handler:
            return ExecutionResult(
                node_id=node.id,
                status=NodeStatus.FAILED,
                error=f"未知的节点类型: {node.type}"
            )
        
        # 执行节点
        try:
            return await node_handler.execute(node, context)
        except Exception as e:
            logger.error(f"节点执行异常: {node.id}, 错误: {e}")
            return ExecutionResult(
                node_id=node.id,
                status=NodeStatus.FAILED,
                error=str(e)
            )
    
    def _collect_outputs(self, workflow: Workflow, context: ExecutionContext) -> dict[str, Any]:
        """收集工作流输出"""
        outputs = {}
        
        # 收集定义的输出变量
        for var in workflow.outputs:
            value = context.get_variable(var.name)
            if value is not None:
                outputs[var.name] = value
        
        # 收集结束节点的输出
        end_nodes = workflow.get_end_nodes()
        for end_node in end_nodes:
            end_output = context.node_outputs.get(end_node.id)
            if isinstance(end_output, dict):
                outputs.update(end_output)
        
        return outputs
    
    async def execute_step_by_step(
        self,
        workflow: Workflow,
        inputs: Optional[dict[str, Any]] = None
    ) -> WorkflowExecution:
        """
        逐步执行工作流(用于调试)
        
        按拓扑顺序逐个执行节点，便于观察和调试
        """
        execution_id = str(uuid.uuid4())
        execution = WorkflowExecution(
            id=execution_id,
            workflow_id=workflow.id or "unknown",
            status=WorkflowStatus.RUNNING,
            inputs=inputs or {},
            start_time=datetime.now()
        )
        
        try:
            # 验证工作流
            valid, error = self.engine.validate_workflow(workflow)
            if not valid:
                raise ValueError(f"工作流验证失败: {error}")
            
            # 拓扑排序
            sorted_nodes = self.engine.topological_sort(workflow)
            
            # 创建上下文
            context = ExecutionContext(workflow=workflow, execution_id=execution_id)
            if inputs:
                for key, value in inputs.items():
                    context.set_variable(key, value)
            
            # 逐个执行节点
            for node_id in sorted_nodes:
                node = workflow.get_node(node_id)
                if not node:
                    continue
                
                # 获取节点处理器
                node_handler = NodeRegistry.build(node.type)
                if not node_handler:
                    result = ExecutionResult(
                        node_id=node_id,
                        status=NodeStatus.FAILED,
                        error=f"未知的节点类型: {node.type}"
                    )
                else:
                    result = await node_handler.execute(node, context)
                
                execution.node_results[node_id] = result
                
                # 保存输出
                if result.status == NodeStatus.SUCCESS and result.output is not None:
                    context.set_node_output(node_id, result.output)
                
                # 如果节点失败，中断执行
                if result.status == NodeStatus.FAILED:
                    execution.status = WorkflowStatus.FAILED
                    execution.error = f"节点 {node_id} 执行失败: {result.error}"
                    break
            
            if execution.status != WorkflowStatus.FAILED:
                execution.status = WorkflowStatus.COMPLETED
                execution.outputs = self._collect_outputs(workflow, context)
            
            execution.end_time = datetime.now()
            execution.duration_ms = (execution.end_time - execution.start_time).total_seconds() * 1000
            
        except Exception as e:
            logger.error(f"工作流执行异常: {e}")
            execution.status = WorkflowStatus.FAILED
            execution.error = str(e)
            execution.end_time = datetime.now()
        
        return execution
    
    def get_execution_plan(self, workflow: Workflow) -> dict[str, Any]:
        """获取工作流执行计划"""
        return self.engine.get_execution_plan(workflow)
    
    def validate_workflow(self, workflow: Workflow) -> tuple[bool, Optional[str]]:
        """验证工作流"""
        return self.engine.validate_workflow(workflow)
    
    def get_running_executions(self) -> list[WorkflowExecution]:
        """获取正在执行的列表"""
        return list(self._running_executions.values())
