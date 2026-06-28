/**
 * 工作流画布 - React Flow 编辑器
 */

import React, { useCallback, useRef, useState } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  ReactFlowProvider,
  Panel,
  Connection,
  ReactFlowInstance,
  BackgroundVariant,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Button, Space, message, Modal } from 'antd';
import {
  PlayCircleOutlined,
  SaveOutlined,
  CheckCircleOutlined,
  // EyeOutlined,
  DownloadOutlined,
  UploadOutlined,
} from '@ant-design/icons';

import WorkflowNode from './WorkflowNode';
import useWorkflowStore from '@/stores/workflowStore';
import { workflowApi } from '@/utils/api';
import { Workflow } from '@/types/workflow';

// 节点类型定义
const nodeTypes = {
  custom: WorkflowNode,
};

interface WorkflowCanvasProps {
  workflowId?: string;
}

const WorkflowCanvasInner: React.FC<WorkflowCanvasProps> = (_props) => {
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const [reactFlowInstance, setReactFlowInstance] = useState<ReactFlowInstance | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionModalVisible, setExecutionModalVisible] = useState(false);
  const [executionResult, setExecutionResult] = useState<any>(null);

  const {
    nodes,
    edges,
    addNode,
    addEdge,
    onNodesChange,
    onEdgesChange,
    setSelectedNode,
    currentWorkflow,
    setCurrentWorkflow,
    reactFlowToWorkflow,
    setExecuting: setStoreExecuting,
  } = useWorkflowStore();

  // 处理节点变化
  const handleNodesChange = useCallback(
    (changes: any[]) => {
      onNodesChange(changes);
    },
    [onNodesChange]
  );

  // 处理边变化
  const handleEdgesChange = useCallback(
    (changes: any[]) => {
      onEdgesChange(changes);
    },
    [onEdgesChange]
  );

  // 处理连接
  const onConnect = useCallback(
    (connection: Connection) => {
      addEdge(connection);
    },
    [addEdge]
  );

  // 处理拖拽放置
  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();

      const type = event.dataTransfer.getData('application/reactflow');

      if (typeof type === 'undefined' || !type) {
        return;
      }

      const reactFlowBounds = reactFlowWrapper.current?.getBoundingClientRect();
      if (!reactFlowBounds || !reactFlowInstance) return;

      const position = reactFlowInstance.project({
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top,
      });

      addNode(type, position);
    },
    [reactFlowInstance, addNode]
  );

  // 保存工作流
  const handleSave = async () => {
    try {
      const workflow = reactFlowToWorkflow();
      
      if (!workflow.name) {
        message.error('请先设置工作流名称');
        return;
      }

      if (currentWorkflow?.id) {
        // 更新
        await workflowApi.update(currentWorkflow.id, workflow);
        message.success('工作流已更新');
      } else {
        // 创建
        const created = await workflowApi.create(workflow);
        setCurrentWorkflow(created);
        message.success('工作流已创建');
      }
    } catch (error: any) {
      message.error(`保存失败: ${error.message}`);
    }
  };

  // 验证工作流
  const handleValidate = async () => {
    try {
      const workflow = reactFlowToWorkflow();
      if (!currentWorkflow?.id) {
        message.warning('请先保存工作流');
        return;
      }

      // 先保存当前状态
      await workflowApi.update(currentWorkflow.id, workflow);
      
      const result = await workflowApi.validate(currentWorkflow.id);
      if (result.valid) {
        message.success('工作流验证通过');
        Modal.info({
          title: '执行计划',
          content: (
            <div style={{ maxHeight: 400, overflow: 'auto' }}>
              <pre>{JSON.stringify(result.execution_plan, null, 2)}</pre>
            </div>
          ),
          width: 600,
        });
      } else {
        message.error(`验证失败: ${result.error}`);
      }
    } catch (error: any) {
      message.error(`验证失败: ${error.message}`);
    }
  };

  // 执行工作流
  const handleExecute = async () => {
    try {
      setIsExecuting(true);
      setStoreExecuting(true);

      const workflow = reactFlowToWorkflow();
      if (!currentWorkflow?.id) {
        message.warning('请先保存工作流');
        return;
      }

      // 先保存
      await workflowApi.update(currentWorkflow.id, workflow);

      // 执行
      const result = await workflowApi.execute(currentWorkflow.id, {});
      setExecutionResult(result);
      setExecutionModalVisible(true);

      if (result.status === 'completed') {
        message.success('工作流执行成功');
      } else {
        message.error(`执行失败: ${result.error}`);
      }
    } catch (error: any) {
      message.error(`执行失败: ${error.message}`);
    } finally {
      setIsExecuting(false);
      setStoreExecuting(false);
    }
  };

  // 导出 JSON
  const handleExport = () => {
    const workflow = reactFlowToWorkflow();
    const dataStr = JSON.stringify(workflow, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `${workflow.name || 'workflow'}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  // 导入 JSON
  const handleImport = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const workflow: Workflow = JSON.parse(e.target?.result as string);
        setCurrentWorkflow(workflow);
        message.success('工作流导入成功');
      } catch (error) {
        message.error('导入失败: 无效的 JSON 格式');
      }
    };
    reader.readAsText(file);
    
    // 重置 input
    event.target.value = '';
  };

  return (
    <div style={{ width: '100%', height: '100%' }} ref={reactFlowWrapper}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={handleNodesChange}
        onEdgesChange={handleEdgesChange}
        onConnect={onConnect}
        onInit={setReactFlowInstance}
        onDrop={onDrop}
        onDragOver={onDragOver}
        onNodeClick={(_, node) => setSelectedNode(node.id)}
        onPaneClick={() => setSelectedNode(null)}
        nodeTypes={nodeTypes}
        fitView
        attributionPosition="bottom-left"
      >
        <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
        <Controls />
        <MiniMap
          nodeStrokeWidth={3}
          zoomable
          pannable
        />
        
        {/* 顶部工具栏 */}
        <Panel position="top-center">
          <Space>
            <Button
              type="primary"
              icon={<SaveOutlined />}
              onClick={handleSave}
            >
              保存
            </Button>
            <Button
              icon={<CheckCircleOutlined />}
              onClick={handleValidate}
            >
              验证
            </Button>
            <Button
              type="primary"
              icon={<PlayCircleOutlined />}
              loading={isExecuting}
              onClick={handleExecute}
            >
              执行
            </Button>
            <Button
              icon={<DownloadOutlined />}
              onClick={handleExport}
            >
              导出
            </Button>
            <Button
              icon={<UploadOutlined />}
              onClick={() => document.getElementById('import-file')?.click()}
            >
              导入
            </Button>
            <input
              id="import-file"
              type="file"
              accept=".json"
              style={{ display: 'none' }}
              onChange={handleImport}
            />
          </Space>
        </Panel>
      </ReactFlow>

      {/* 执行结果弹窗 */}
      <Modal
        title="执行结果"
        open={executionModalVisible}
        onOk={() => setExecutionModalVisible(false)}
        onCancel={() => setExecutionModalVisible(false)}
        width={800}
      >
        {executionResult && (
          <div style={{ maxHeight: 500, overflow: 'auto' }}>
            <div style={{ marginBottom: 16 }}>
              <strong>状态:</strong>{' '}
              <span style={{ color: executionResult.status === 'completed' ? '#52c41a' : '#ff4d4f' }}>
                {executionResult.status}
              </span>
            </div>
            <div style={{ marginBottom: 16 }}>
              <strong>耗时:</strong> {executionResult.duration_ms?.toFixed(2)}ms
            </div>
            {executionResult.outputs && (
              <div style={{ marginBottom: 16 }}>
                <strong>输出:</strong>
                <pre style={{ background: '#f5f5f5', padding: 12, borderRadius: 4 }}>
                  {JSON.stringify(executionResult.outputs, null, 2)}
                </pre>
              </div>
            )}
            {executionResult.node_results && (
              <div>
                <strong>节点执行结果:</strong>
                <pre style={{ background: '#f5f5f5', padding: 12, borderRadius: 4 }}>
                  {JSON.stringify(executionResult.node_results, null, 2)}
                </pre>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

const WorkflowCanvas: React.FC<WorkflowCanvasProps> = (props) => {
  return (
    <ReactFlowProvider>
      <WorkflowCanvasInner {...props} />
    </ReactFlowProvider>
  );
};

export default WorkflowCanvas;
