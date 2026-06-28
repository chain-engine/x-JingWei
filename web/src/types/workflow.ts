/**
 * 工作流类型定义
 */

// 节点类型
export type NodeType = 
  | 'start' 
  | 'end' 
  | 'llm' 
  | 'code' 
  | 'condition' 
  | 'http' 
  | 'database' 
  | 'transform' 
  | 'parallel' 
  | 'aggregate' 
  | 'websearch' 
  | 'document';

// 节点状态
export type NodeStatus = 
  | 'pending' 
  | 'running' 
  | 'success' 
  | 'failed' 
  | 'skipped' 
  | 'timeout';

// 工作流状态
export type WorkflowStatus = 
  | 'draft' 
  | 'active' 
  | 'disabled' 
  | 'running' 
  | 'completed' 
  | 'failed' 
  | 'paused';

// 位置
export interface Position {
  x: number;
  y: number;
}

// 节点数据
export interface NodeData {
  label: string;
  description?: string;
  config: Record<string, any>;
  inputs: Record<string, any>;
  outputs: Record<string, any>;
}

// 工作流节点
export interface WorkflowNode {
  id: string;
  type: NodeType;
  position: Position;
  data: NodeData;
  status?: NodeStatus;
  output?: any;
  error?: string;
  start_time?: string;
  end_time?: string;
}

// 工作流边
export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  source_handle?: string;
  target_handle?: string;
  label?: string;
  condition?: string;
  data_mapping?: Record<string, string>;
}

// 工作流变量
export interface WorkflowVariable {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'array' | 'object' | 'any';
  default?: any;
  description?: string;
  required: boolean;
}

// 工作流元数据
export interface WorkflowMetadata {
  author?: string;
  tags: string[];
  category?: string;
  icon?: string;
  color?: string;
}

// 工作流
export interface Workflow {
  id?: string;
  name: string;
  description?: string;
  version: string;
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  inputs: WorkflowVariable[];
  outputs: WorkflowVariable[];
  metadata: WorkflowMetadata;
  settings: Record<string, any>;
  status: WorkflowStatus;
  created_at?: string;
  updated_at?: string;
}

// 节点类型信息
export interface NodeTypeInfo {
  type: NodeType;
  label: string;
  description: string;
  icon: string;
  color: string;
  inputs: Array<{
    name: string;
    type: string;
    required: boolean;
    default?: any;
    label: string;
  }>;
  outputs: Array<{
    name: string;
    type: string;
    label: string;
  }>;
}

// 执行结果
export interface ExecutionResult {
  node_id: string;
  status: NodeStatus;
  output?: any;
  error?: string;
  start_time?: string;
  end_time?: string;
  duration_ms?: number;
}

// 工作流执行
export interface WorkflowExecution {
  id?: string;
  workflow_id: string;
  status: WorkflowStatus;
  inputs: Record<string, any>;
  outputs: Record<string, any>;
  node_results: Record<string, ExecutionResult>;
  error?: string;
  start_time?: string;
  end_time?: string;
  duration_ms?: number;
}

// 执行计划
export interface ExecutionPlan {
  valid: boolean;
  sorted_order?: string[];
  execution_levels?: string[][];
  parallel_groups?: string[][];
  dependencies?: Record<string, string[]>;
  start_nodes?: string[];
  end_nodes?: string[];
  total_nodes?: number;
  total_edges?: number;
  estimated_parallelism?: number;
  error?: string;
}
