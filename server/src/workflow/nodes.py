#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
节点类型定义和注册
实现各种工作流节点的具体逻辑
"""

import json
import re
import asyncio
from abc import ABC, abstractmethod
from typing import Any, Optional, Type
from datetime import datetime

from core.logger import logger
from .models import Node, NodeType, NodeStatus, ExecutionResult
from .engine import ExecutionContext


class BaseNode(ABC):
    """节点基类"""
    
    node_type: NodeType = NodeType.CODE
    
    @abstractmethod
    async def execute(self, node: Node, context: ExecutionContext) -> ExecutionResult:
        """
        执行节点逻辑
        
        Args:
            node: 节点实例
            context: 执行上下文
            
        Returns:
            ExecutionResult: 执行结果
        """
        pass
    
    def resolve_inputs(self, node: Node, context: ExecutionContext) -> dict[str, Any]:
        """解析节点输入参数中的模板变量"""
        config = node.data.config.copy()
        return context.resolve_dict(config)
    
    def create_success_result(self, node_id: str, output: Any) -> ExecutionResult:
        """创建成功结果"""
        return ExecutionResult(
            node_id=node_id,
            status=NodeStatus.SUCCESS,
            output=output
        )
    
    def create_error_result(self, node_id: str, error: str) -> ExecutionResult:
        """创建错误结果"""
        return ExecutionResult(
            node_id=node_id,
            status=NodeStatus.FAILED,
            error=error
        )


class StartNode(BaseNode):
    """开始节点"""
    
    node_type = NodeType.START
    
    async def execute(self, node: Node, context: ExecutionContext) -> ExecutionResult:
        """开始节点执行 - 初始化输入变量"""
        logger.info(f"工作流开始执行: {node.data.label}")
        
        # 将工作流输入变量注入上下文
        workflow = context.workflow
        for var in workflow.inputs:
            if var.name in context.variables:
                context.set_variable(var.name, context.variables[var.name])
            elif var.default is not None:
                context.set_variable(var.name, var.default)
        
        return self.create_success_result(node.id, {"started": True, "timestamp": datetime.now().isoformat()})


class EndNode(BaseNode):
    """结束节点"""
    
    node_type = NodeType.END
    
    async def execute(self, node: Node, context: ExecutionContext) -> ExecutionResult:
        """结束节点执行 - 整理输出结果"""
        logger.info(f"工作流执行结束: {node.data.label}")
        
        # 收集输出变量
        outputs = {}
        workflow = context.workflow
        for var in workflow.outputs:
            value = context.get_variable(var.name)
            if value is not None:
                outputs[var.name] = value
        
        return self.create_success_result(node.id, outputs)


class LLMNode(BaseNode):
    """LLM节点 - 调用大语言模型"""
    
    node_type = NodeType.LLM
    
    async def execute(self, node: Node, context: ExecutionContext) -> ExecutionResult:
        """执行LLM调用"""
        try:
            inputs = self.resolve_inputs(node, context)
            
            # 获取配置
            model = inputs.get("model", "deepseek-chat")
            prompt = inputs.get("prompt", "")
            temperature = float(inputs.get("temperature", 0.7))
            max_tokens = int(inputs.get("max_tokens", 2000))
            
            if not prompt:
                return self.create_error_result(node.id, "Prompt不能为空")
            
            logger.info(f"LLM节点执行: model={model}, prompt_length={len(prompt)}")
            
            # 模拟LLM调用(实际项目应调用真实API)
            await asyncio.sleep(0.5)  # 模拟延迟
            
            response = f"这是来自 {model} 的模拟回复。您的问题是: {prompt[:50]}..."
            
            return self.create_success_result(node.id, {
                "content": response,
                "model": model,
                "usage": {
                    "prompt_tokens": len(prompt.split()),
                    "completion_tokens": len(response.split()),
                    "total_tokens": len(prompt.split()) + len(response.split())
                }
            })
            
        except Exception as e:
            logger.error(f"LLM节点执行失败: {e}")
            return self.create_error_result(node.id, str(e))


class CodeNode(BaseNode):
    """代码执行节点"""
    
    node_type = NodeType.CODE
    
    async def execute(self, node: Node, context: ExecutionContext) -> ExecutionResult:
        """执行Python代码"""
        try:
            inputs = self.resolve_inputs(node, context)
            code = inputs.get("code", "")
            
            if not code:
                return self.create_error_result(node.id, "代码不能为空")
            
            logger.info(f"执行代码节点: {node.id}")
            
            # 创建安全的执行环境
            safe_globals = {
                "__builtins__": {
                    "len": len, "range": range, "enumerate": enumerate,
                    "zip": zip, "map": map, "filter": filter,
                    "sum": sum, "min": min, "max": max, "abs": abs,
                    "round": round, "pow": pow, "divmod": divmod,
                    "isinstance": isinstance, "hasattr": hasattr, "getattr": getattr,
                    "list": list, "dict": dict, "str": str, "int": int, "float": float,
                    "bool": bool, "set": set, "tuple": tuple,
                    "json": json, "re": re,
                },
                "input_data": inputs.get("input_data", {}),
                "context": context.variables,
            }
            
            # 执行代码
            exec_globals = {}
            exec(code, safe_globals, exec_globals)
            
            # 获取输出
            output = exec_globals.get("output", exec_globals.get("result", None))
            
            return self.create_success_result(node.id, output)
            
        except Exception as e:
            logger.error(f"代码执行失败: {e}")
            return self.create_error_result(node.id, f"代码执行错误: {str(e)}")


class ConditionNode(BaseNode):
    """条件分支节点"""
    
    node_type = NodeType.CONDITION
    
    async def execute(self, node: Node, context: ExecutionContext) -> ExecutionResult:
        """执行条件判断"""
        try:
            inputs = self.resolve_inputs(node, context)
            condition = inputs.get("condition", "")
            
            if not condition:
                return self.create_error_result(node.id, "条件表达式不能为空")
            
            logger.info(f"执行条件判断: {condition}")
            
            # 创建安全的评估环境
            safe_locals = {"context": context.variables, **context.variables}
            
            # 评估条件
            result = eval(condition, {"__builtins__": {}}, safe_locals)
            
            return self.create_success_result(node.id, {
                "condition": condition,
                "result": bool(result),
                "branch": "true" if result else "false"
            })
            
        except Exception as e:
            logger.error(f"条件判断失败: {e}")
            return self.create_error_result(node.id, str(e))


class HTTPNode(BaseNode):
    """HTTP请求节点"""
    
    node_type = NodeType.HTTP
    
    async def execute(self, node: Node, context: ExecutionContext) -> ExecutionResult:
        """执行HTTP请求"""
        try:
            inputs = self.resolve_inputs(node, context)
            
            url = inputs.get("url", "")
            method = inputs.get("method", "GET").upper()
            headers = inputs.get("headers", {})
            body = inputs.get("body")
            
            if not url:
                return self.create_error_result(node.id, "URL不能为空")
            
            logger.info(f"执行HTTP请求: {method} {url}")
            
            # 模拟HTTP请求(实际项目应使用aiohttp或httpx)
            await asyncio.sleep(0.3)
            
            return self.create_success_result(node.id, {
                "status": 200,
                "headers": {"Content-Type": "application/json"},
                "body": {"message": f"模拟 {method} 请求到 {url} 的响应", "success": True}
            })
            
        except Exception as e:
            logger.error(f"HTTP请求失败: {e}")
            return self.create_error_result(node.id, str(e))


class TransformNode(BaseNode):
    """数据转换节点"""
    
    node_type = NodeType.TRANSFORM
    
    async def execute(self, node: Node, context: ExecutionContext) -> ExecutionResult:
        """执行数据转换"""
        try:
            inputs = self.resolve_inputs(node, context)
            
            transform_type = inputs.get("transform_type", "map")
            input_data = inputs.get("input_data", [])
            
            if not isinstance(input_data, list):
                return self.create_error_result(node.id, "输入数据必须是列表")
            
            logger.info(f"执行数据转换: type={transform_type}")
            
            if transform_type == "map":
                # 映射转换
                field = inputs.get("field", "")
                result = [{"value": item.get(field) if isinstance(item, dict) else item} for item in input_data]
            elif transform_type == "filter":
                # 过滤
                condition = inputs.get("filter_condition", "")
                result = input_data  # 简化处理
            elif transform_type == "reduce":
                # 聚合
                result = {"count": len(input_data), "sum": sum(float(x) for x in input_data if isinstance(x, (int, float)))}
            else:
                result = input_data
            
            return self.create_success_result(node.id, result)
            
        except Exception as e:
            logger.error(f"数据转换失败: {e}")
            return self.create_error_result(node.id, str(e))


class ParallelNode(BaseNode):
    """并行节点 - 触发并行分支"""
    
    node_type = NodeType.PARALLEL
    
    async def execute(self, node: Node, context: ExecutionContext) -> ExecutionResult:
        """并行节点执行"""
        logger.info(f"并行节点: {node.id}")
        
        # 并行节点本身只是标记，实际并行由执行器控制
        return self.create_success_result(node.id, {
            "parallel": True,
            "branches": node.data.config.get("branches", [])
        })


class AggregateNode(BaseNode):
    """聚合节点 - 合并并行分支结果"""
    
    node_type = NodeType.AGGREGATE
    
    async def execute(self, node: Node, context: ExecutionContext) -> ExecutionResult:
        """聚合执行结果"""
        try:
            inputs = self.resolve_inputs(node, context)
            aggregate_type = inputs.get("aggregate_type", "merge")
            
            logger.info(f"聚合节点执行: type={aggregate_type}")
            
            # 从上下文中收集上游节点的输出
            workflow = context.workflow
            incoming_edges = workflow.get_incoming_edges(node.id)
            
            collected_outputs = []
            for edge in incoming_edges:
                output = context.node_outputs.get(edge.source)
                if output is not None:
                    collected_outputs.append({
                        "source": edge.source,
                        "output": output
                    })
            
            result = {
                "collected": collected_outputs,
                "count": len(collected_outputs)
            }
            
            return self.create_success_result(node.id, result)
            
        except Exception as e:
            logger.error(f"聚合失败: {e}")
            return self.create_error_result(node.id, str(e))


class DocumentNode(BaseNode):
    """文档处理节点"""
    
    node_type = NodeType.DOCUMENT
    
    async def execute(self, node: Node, context: ExecutionContext) -> ExecutionResult:
        """处理文档"""
        try:
            inputs = self.resolve_inputs(node, context)
            
            operation = inputs.get("operation", "parse")
            content = inputs.get("content", "")
            
            logger.info(f"文档处理: operation={operation}")
            
            if operation == "parse":
                # 解析文档
                result = {"text": content, "length": len(content)}
            elif operation == "chunk":
                # 分块
                chunk_size = int(inputs.get("chunk_size", 500))
                chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
                result = {"chunks": chunks, "count": len(chunks)}
            elif operation == "summarize":
                # 摘要(模拟)
                result = {"summary": f"这是文档的模拟摘要(原文长度: {len(content)})"}
            else:
                result = {"text": content}
            
            return self.create_success_result(node.id, result)
            
        except Exception as e:
            logger.error(f"文档处理失败: {e}")
            return self.create_error_result(node.id, str(e))


class NodeRegistry:
    """节点注册表"""
    
    _nodes: dict[NodeType, Type[BaseNode]] = {}
    
    @classmethod
    def register(cls, node_class: Type[BaseNode]) -> Type[BaseNode]:
        """注册节点类型"""
        cls._nodes[node_class.node_type] = node_class
        logger.debug(f"注册节点类型: {node_class.node_type}")
        return node_class
    
    @classmethod
    def get(cls, node_type: NodeType) -> Optional[Type[BaseNode]]:
        """获取节点类"""
        return cls._nodes.get(node_type)
    
    @classmethod
    def build(cls, node_type: NodeType) -> Optional[BaseNode]:
        """创建节点实例"""
        node_class = cls.get(node_type)
        if node_class:
            return node_class()
        return None
    
    @classmethod
    def list_types(cls) -> list[NodeType]:
        """列出所有注册的节点类型"""
        return list(cls._nodes.keys())
    
    @classmethod
    def get_node_metadata(cls, node_type: NodeType) -> dict[str, Any]:
        """获取节点元数据(用于前端)"""
        node_class = cls.get(node_type)
        if not node_class:
            return {}
        
        # 根据节点类型返回不同的配置定义
        metadata = {
            NodeType.START: {
                "label": "开始",
                "description": "工作流开始节点",
                "icon": "PlayCircle",
                "color": "#52c41a",
                "inputs": [],
                "outputs": []
            },
            NodeType.END: {
                "label": "结束",
                "description": "工作流结束节点",
                "icon": "StopCircle",
                "color": "#ff4d4f",
                "inputs": [],
                "outputs": []
            },
            NodeType.LLM: {
                "label": "LLM",
                "description": "调用大语言模型",
                "icon": "MessageSquare",
                "color": "#1890ff",
                "inputs": [
                    {"name": "prompt", "type": "string", "required": True, "label": "提示词"},
                    {"name": "model", "type": "string", "required": False, "default": "deepseek-chat", "label": "模型"},
                    {"name": "temperature", "type": "number", "required": False, "default": 0.7, "label": "温度"},
                    {"name": "max_tokens", "type": "number", "required": False, "default": 2000, "label": "最大Token"}
                ],
                "outputs": [
                    {"name": "content", "type": "string", "label": "回复内容"},
                    {"name": "usage", "type": "object", "label": "Token使用"}
                ]
            },
            NodeType.CODE: {
                "label": "代码",
                "description": "执行Python代码",
                "icon": "Code",
                "color": "#722ed1",
                "inputs": [
                    {"name": "code", "type": "string", "required": True, "label": "代码"},
                    {"name": "input_data", "type": "any", "required": False, "label": "输入数据"}
                ],
                "outputs": [
                    {"name": "result", "type": "any", "label": "执行结果"}
                ]
            },
            NodeType.CONDITION: {
                "label": "条件",
                "description": "条件分支判断",
                "icon": "GitBranch",
                "color": "#fa8c16",
                "inputs": [
                    {"name": "condition", "type": "string", "required": True, "label": "条件表达式"}
                ],
                "outputs": [
                    {"name": "result", "type": "boolean", "label": "判断结果"},
                    {"name": "branch", "type": "string", "label": "分支(true/false)"}
                ]
            },
            NodeType.HTTP: {
                "label": "HTTP",
                "description": "发送HTTP请求",
                "icon": "Globe",
                "color": "#13c2c2",
                "inputs": [
                    {"name": "url", "type": "string", "required": True, "label": "URL"},
                    {"name": "method", "type": "string", "required": False, "default": "GET", "label": "方法"},
                    {"name": "headers", "type": "object", "required": False, "label": "请求头"},
                    {"name": "body", "type": "any", "required": False, "label": "请求体"}
                ],
                "outputs": [
                    {"name": "status", "type": "number", "label": "状态码"},
                    {"name": "body", "type": "any", "label": "响应体"}
                ]
            },
            NodeType.TRANSFORM: {
                "label": "转换",
                "description": "数据转换处理",
                "icon": "Shuffle",
                "color": "#eb2f96",
                "inputs": [
                    {"name": "input_data", "type": "array", "required": True, "label": "输入数据"},
                    {"name": "transform_type", "type": "string", "required": False, "default": "map", "label": "转换类型"}
                ],
                "outputs": [
                    {"name": "result", "type": "any", "label": "转换结果"}
                ]
            },
            NodeType.PARALLEL: {
                "label": "并行",
                "description": "并行执行分支",
                "icon": "Split",
                "color": "#2f54eb",
                "inputs": [],
                "outputs": []
            },
            NodeType.AGGREGATE: {
                "label": "聚合",
                "description": "聚合并行结果",
                "icon": "Merge",
                "color": "#614700",
                "inputs": [],
                "outputs": [
                    {"name": "collected", "type": "array", "label": "收集结果"}
                ]
            },
            NodeType.DOCUMENT: {
                "label": "文档",
                "description": "文档处理",
                "icon": "FileText",
                "color": "#595959",
                "inputs": [
                    {"name": "content", "type": "string", "required": True, "label": "内容"},
                    {"name": "operation", "type": "string", "required": False, "default": "parse", "label": "操作类型"}
                ],
                "outputs": [
                    {"name": "result", "type": "any", "label": "处理结果"}
                ]
            },
        }
        
        return metadata.get(node_type, {})


# 注册所有节点类型
NodeRegistry.register(StartNode)
NodeRegistry.register(EndNode)
NodeRegistry.register(LLMNode)
NodeRegistry.register(CodeNode)
NodeRegistry.register(ConditionNode)
NodeRegistry.register(HTTPNode)
NodeRegistry.register(TransformNode)
NodeRegistry.register(ParallelNode)
NodeRegistry.register(AggregateNode)
NodeRegistry.register(DocumentNode)
