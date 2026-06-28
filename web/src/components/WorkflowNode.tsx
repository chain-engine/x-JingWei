/**
 * 自定义工作流节点组件
 */

import React, { memo } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { Card, Tag, Tooltip } from 'antd';
import {
  PlayCircleOutlined,
  StopOutlined,
  MessageOutlined,
  CodeOutlined,
  BranchesOutlined,
  GlobalOutlined,
  FileTextOutlined,
  LoadingOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
} from '@ant-design/icons';
import useWorkflowStore from '@/stores/workflowStore';

// 节点类型图标映射
const nodeIcons: Record<string, React.ReactNode> = {
  start: <PlayCircleOutlined />,
  end: <StopOutlined />,
  llm: <MessageOutlined />,
  code: <CodeOutlined />,
  condition: <BranchesOutlined />,
  http: <GlobalOutlined />,
  transform: <CodeOutlined />,
  parallel: <BranchesOutlined />,
  aggregate: <CodeOutlined />,
  document: <FileTextOutlined />,
};

// 节点类型颜色映射
const nodeColors: Record<string, string> = {
  start: '#52c41a',
  end: '#ff4d4f',
  llm: '#1890ff',
  code: '#722ed1',
  condition: '#fa8c16',
  http: '#13c2c2',
  transform: '#eb2f96',
  parallel: '#2f54eb',
  aggregate: '#614700',
  document: '#595959',
};

// 状态图标
const statusIcons: Record<string, React.ReactNode> = {
  pending: null,
  running: <LoadingOutlined spin />,
  success: <CheckCircleOutlined style={{ color: '#52c41a' }} />,
  failed: <CloseCircleOutlined style={{ color: '#ff4d4f' }} />,
};

const WorkflowNode: React.FC<NodeProps> = ({ id, data, selected }) => {
  const { selectedNodeId, setSelectedNode, nodeTypes } = useWorkflowStore();
  const isSelected = selectedNodeId === id || selected;
  
  const nodeType = nodeTypes.find((t) => t.type === data.nodeType);
  const color = nodeColors[data.nodeType] || '#1890ff';
  const icon = nodeIcons[data.nodeType] || <CodeOutlined />;
  const statusIcon = data.status ? statusIcons[data.status] : null;

  const handleClick = () => {
    setSelectedNode(id);
  };

  return (
    <div onClick={handleClick}>
      {/* 输入连接点 */}
      {data.nodeType !== 'start' && (
        <Handle
          type="target"
          position={Position.Left}
          style={{ background: color, width: 10, height: 10 }}
        />
      )}

      <Card
        size="small"
        style={{
          width: 180,
          borderColor: isSelected ? color : undefined,
          borderWidth: isSelected ? 2 : 1,
          boxShadow: isSelected ? `0 0 10px ${color}40` : undefined,
        }}
        title={
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ color, fontSize: 16 }}>{icon}</span>
            <span style={{ fontSize: 12, fontWeight: 500 }}>{data.label}</span>
            {statusIcon && <span style={{ marginLeft: 'auto' }}>{statusIcon}</span>}
          </div>
        }
        headStyle={{
          background: `${color}10`,
          borderBottom: `1px solid ${color}20`,
          padding: '4px 12px',
        }}
        bodyStyle={{ padding: '8px 12px' }}
      >
        <Tooltip title={data.description}>
          <div
            style={{
              fontSize: 11,
              color: '#666',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
          >
            {data.description || nodeType?.description || '暂无描述'}
          </div>
        </Tooltip>

        {/* 显示配置摘要 */}
        {data.config && Object.keys(data.config).length > 0 && (
          <div style={{ marginTop: 4 }}>
            {Object.entries(data.config).slice(0, 2).map(([key, value]) => (
              <Tag key={key} style={{ fontSize: 10, margin: 2 }}>
                {key}: {String(value).slice(0, 10)}
              </Tag>
            ))}
          </div>
        )}
      </Card>

      {/* 输出连接点 */}
      {data.nodeType !== 'end' && (
        <Handle
          type="source"
          position={Position.Right}
          style={{ background: color, width: 10, height: 10 }}
        />
      )}

      {/* 条件分支的连接点 */}
      {data.nodeType === 'condition' && (
        <>
          <Handle
            type="source"
            position={Position.Bottom}
            id="true"
            style={{ background: '#52c41a', width: 10, height: 10, left: '30%' }}
          />
          <Handle
            type="source"
            position={Position.Bottom}
            id="false"
            style={{ background: '#ff4d4f', width: 10, height: 10, left: '70%' }}
          />
        </>
      )}
    </div>
  );
};

export default memo(WorkflowNode);
