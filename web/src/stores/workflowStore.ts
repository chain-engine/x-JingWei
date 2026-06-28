/**
 * 工作流状态管理
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import {
  Workflow,
  WorkflowNode,
  WorkflowEdge,
  NodeTypeInfo,
  ExecutionPlan,
  WorkflowExecution,
} from '@/types/workflow';

// React Flow 类型
import { Node as ReactFlowNode, Edge as ReactFlowEdge, Connection, NodeChange, EdgeChange, applyNodeChanges, applyEdgeChanges } from 'reactflow';

interface WorkflowState {
  // 当前工作流
  currentWorkflow: Workflow | null;
  // React Flow 节点和边
  nodes: ReactFlowNode[];
  edges: ReactFlowEdge[];
  // 选中状态
  selectedNodeId: string | null;
  selectedEdgeId: string | null;
  // 节点类型列表
  nodeTypes: NodeTypeInfo[];
  // 执行计划
  executionPlan: ExecutionPlan | null;
  // 当前执行
  currentExecution: WorkflowExecution | null;
  // 加载状态
  loading: boolean;
  saving: boolean;
  executing: boolean;
  
  // Actions
  setCurrentWorkflow: (workflow: Workflow | null) => void;
  setNodes: (nodes: ReactFlowNode[] | ((prev: ReactFlowNode[]) => ReactFlowNode[])) => void;
  setEdges: (edges: ReactFlowEdge[] | ((prev: ReactFlowEdge[]) => ReactFlowEdge[])) => void;
  onNodesChange: (changes: NodeChange[]) => void;
  onEdgesChange: (changes: EdgeChange[]) => void;
  addNode: (type: string, position: { x: number; y: number }) => void;
  updateNode: (nodeId: string, data: Partial<WorkflowNode['data']>) => void;
  removeNode: (nodeId: string) => void;
  addEdge: (connection: Connection) => void;
  removeEdge: (edgeId: string) => void;
  setSelectedNode: (nodeId: string | null) => void;
  setSelectedEdge: (edgeId: string | null) => void;
  setNodeTypes: (types: NodeTypeInfo[]) => void;
  setExecutionPlan: (plan: ExecutionPlan | null) => void;
  setCurrentExecution: (execution: WorkflowExecution | null) => void;
  setLoading: (loading: boolean) => void;
  setSaving: (saving: boolean) => void;
  setExecuting: (executing: boolean) => void;
  
  // 工作流转换
  workflowToReactFlow: (workflow: Workflow) => void;
  reactFlowToWorkflow: () => Workflow;
  
  // 重置
  reset: () => void;
}

// 生成唯一ID
const generateId = (prefix: string = 'node') => `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

export const useWorkflowStore = create<WorkflowState>()(
  devtools(
    (set, get) => ({
      // 初始状态
      currentWorkflow: null,
      nodes: [],
      edges: [],
      selectedNodeId: null,
      selectedEdgeId: null,
      nodeTypes: [],
      executionPlan: null,
      currentExecution: null,
      loading: false,
      saving: false,
      executing: false,

      // Actions
      setCurrentWorkflow: (workflow) => {
        set({ currentWorkflow: workflow });
        if (workflow) {
          get().workflowToReactFlow(workflow);
        }
      },

      setNodes: (nodes) => {
        if (typeof nodes === 'function') {
          set((state) => ({ nodes: nodes(state.nodes) }));
        } else {
          set({ nodes });
        }
      },

      setEdges: (edges) => {
        if (typeof edges === 'function') {
          set((state) => ({ edges: edges(state.edges) }));
        } else {
          set({ edges });
        }
      },

      onNodesChange: (changes) => {
        set((state) => ({
          nodes: applyNodeChanges(changes, state.nodes),
        }));
      },

      onEdgesChange: (changes) => {
        set((state) => ({
          edges: applyEdgeChanges(changes, state.edges),
        }));
      },

      addNode: (type, position) => {
        const nodeType = get().nodeTypes.find((t) => t.type === type);
        const newNode: ReactFlowNode = {
          id: generateId('node'),
          type: 'custom',
          position,
          data: {
            label: nodeType?.label || type,
            description: nodeType?.description || '',
            nodeType: type,
            config: {},
            inputs: {},
            outputs: {},
          },
        };
        set((state) => ({ nodes: [...state.nodes, newNode] }));
      },

      updateNode: (nodeId, data) => {
        set((state) => ({
          nodes: state.nodes.map((node) =>
            node.id === nodeId ? { ...node, data: { ...node.data, ...data } } : node
          ),
        }));
      },

      removeNode: (nodeId) => {
        set((state) => ({
          nodes: state.nodes.filter((node) => node.id !== nodeId),
          edges: state.edges.filter(
            (edge) => edge.source !== nodeId && edge.target !== nodeId
          ),
          selectedNodeId: state.selectedNodeId === nodeId ? null : state.selectedNodeId,
        }));
      },

      addEdge: (connection) => {
        if (!connection.source || !connection.target) return;
        
        const newEdge: ReactFlowEdge = {
          id: generateId('edge'),
          source: connection.source,
          target: connection.target,
          sourceHandle: connection.sourceHandle || undefined,
          targetHandle: connection.targetHandle || undefined,
          type: 'custom',
          data: {},
        };
        set((state) => ({ edges: [...state.edges, newEdge] }));
      },

      removeEdge: (edgeId) => {
        set((state) => ({
          edges: state.edges.filter((edge) => edge.id !== edgeId),
          selectedEdgeId: state.selectedEdgeId === edgeId ? null : state.selectedEdgeId,
        }));
      },

      setSelectedNode: (nodeId) => set({ selectedNodeId: nodeId }),
      setSelectedEdge: (edgeId) => set({ selectedEdgeId: edgeId }),
      setNodeTypes: (types) => set({ nodeTypes: types }),
      setExecutionPlan: (plan) => set({ executionPlan: plan }),
      setCurrentExecution: (execution) => set({ currentExecution: execution }),
      setLoading: (loading) => set({ loading }),
      setSaving: (saving) => set({ saving }),
      setExecuting: (executing) => set({ executing }),

      workflowToReactFlow: (workflow) => {
        const nodes: ReactFlowNode[] = workflow.nodes.map((node) => ({
          id: node.id,
          type: 'custom',
          position: node.position,
          data: {
            label: node.data.label,
            description: node.data.description,
            nodeType: node.type,
            config: node.data.config,
            inputs: node.data.inputs,
            outputs: node.data.outputs,
            status: node.status,
            error: node.error,
          },
        }));

        const edges: ReactFlowEdge[] = workflow.edges.map((edge) => ({
          id: edge.id,
          source: edge.source,
          target: edge.target,
          sourceHandle: edge.source_handle,
          targetHandle: edge.target_handle,
          type: 'custom',
          label: edge.label,
          data: {
            condition: edge.condition,
            dataMapping: edge.data_mapping,
          },
        }));

        set({ nodes, edges, currentWorkflow: workflow });
      },

      reactFlowToWorkflow: () => {
        const { nodes, edges, currentWorkflow } = get();
        
        const workflowNodes: WorkflowNode[] = nodes.map((node) => ({
          id: node.id,
          type: node.data.nodeType as any,
          position: node.position,
          data: {
            label: node.data.label,
            description: node.data.description,
            config: node.data.config || {},
            inputs: node.data.inputs || {},
            outputs: node.data.outputs || {},
          },
        }));

        const workflowEdges: WorkflowEdge[] = edges.map((edge) => ({
          id: edge.id,
          source: edge.source,
          target: edge.target,
          source_handle: edge.sourceHandle ?? undefined,
          target_handle: edge.targetHandle ?? undefined,
          label: edge.label as string | undefined,
          condition: edge.data?.condition,
          data_mapping: edge.data?.dataMapping,
        }));

        return {
          ...(currentWorkflow || {}),
          nodes: workflowNodes,
          edges: workflowEdges,
        } as Workflow;
      },

      reset: () => {
        set({
          currentWorkflow: null,
          nodes: [],
          edges: [],
          selectedNodeId: null,
          selectedEdgeId: null,
          executionPlan: null,
          currentExecution: null,
          loading: false,
          saving: false,
          executing: false,
        });
      },
    }),
    { name: 'workflow-store' }
  )
);

export default useWorkflowStore;
