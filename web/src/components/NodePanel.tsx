/**
 * 节点面板 - 可拖拽的节点类型列表
 */

import React, { useEffect } from 'react';
import { Card, List, Tag, Empty, Spin } from 'antd';
import {
  PlayCircleOutlined,
  StopOutlined,
  MessageOutlined,
  CodeOutlined,
  BranchesOutlined,
  GlobalOutlined,
  FileTextOutlined,
  SplitCellsOutlined,
  MergeCellsOutlined,
  SwapOutlined,
} from '@ant-design/icons';
import useWorkflowStore from '@/stores/workflowStore';
import { workflowApi } from '@/utils/api';

// 图标映射
const iconMap: Record<string, React.ReactNode> = {
  PlayCircle: <PlayCircleOutlined />,
  StopCircle: <StopOutlined />,
  MessageSquare: <MessageOutlined />,
  Code: <CodeOutlined />,
  GitBranch: <BranchesOutlined />,
  Globe: <GlobalOutlined />,
  FileText: <FileTextOutlined />,
  Split: <SplitCellsOutlined />,
  Merge: <MergeCellsOutlined />,
  Shuffle: <SwapOutlined />,
};

const NodePanel: React.FC = () => {
  const { nodeTypes, setNodeTypes, loading, setLoading } = useWorkflowStore();

  // 加载节点类型
  useEffect(() => {
    const loadNodeTypes = async () => {
      setLoading(true);
      try {
        const types = await workflowApi.listNodeTypes();
        setNodeTypes(types);
      } catch (error) {
        console.error('加载节点类型失败:', error);
      } finally {
        setLoading(false);
      }
    };

    loadNodeTypes();
  }, [setNodeTypes, setLoading]);

  // 开始拖拽
  const onDragStart = (event: React.DragEvent, nodeType: string) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.effectAllowed = 'move';
  };

  // 按分类分组
  const groupedTypes = nodeTypes.reduce((acc, type) => {
    let category = '其他';
    if (['start', 'end'].includes(type.type)) category = '控制';
    else if (['llm', 'code', 'transform'].includes(type.type)) category = '处理';
    else if (['condition', 'parallel', 'aggregate'].includes(type.type)) category = '流程';
    else if (['http', 'document'].includes(type.type)) category = '工具';

    if (!acc[category]) acc[category] = [];
    acc[category].push(type);
    return acc;
  }, {} as Record<string, typeof nodeTypes>);

  if (loading) {
    return (
      <Card title="节点组件" size="small" style={{ height: '100%' }}>
        <div style={{ display: 'flex', justifyContent: 'center', padding: 40 }}>
          <Spin />
        </div>
      </Card>
    );
  }

  return (
    <Card 
      title="节点组件" 
      size="small" 
      style={{ height: '100%', overflow: 'auto' }}
      bodyStyle={{ padding: 8 }}
    >
      {nodeTypes.length === 0 ? (
        <Empty description="暂无节点类型" />
      ) : (
        Object.entries(groupedTypes).map(([category, types]) => (
          <div key={category} style={{ marginBottom: 16 }}>
            <Tag color="blue" style={{ marginBottom: 8 }}>
              {category}
            </Tag>
            <List
              size="small"
              dataSource={types}
              renderItem={(type) => (
                <List.Item
                  draggable
                  onDragStart={(e) => onDragStart(e, type.type)}
                  style={{
                    cursor: 'move',
                    borderRadius: 4,
                    marginBottom: 4,
                    padding: '8px 12px',
                    background: '#fafafa',
                    border: `1px solid ${type.color}30`,
                    transition: 'all 0.2s',
                  }}
                  className="node-item"
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = `${type.color}10`;
                    e.currentTarget.style.borderColor = type.color;
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = '#fafafa';
                    e.currentTarget.style.borderColor = `${type.color}30`;
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ color: type.color, fontSize: 16 }}>
                      {iconMap[type.icon] || <CodeOutlined />}
                    </span>
                    <div>
                      <div style={{ fontSize: 13, fontWeight: 500 }}>{type.label}</div>
                      <div style={{ fontSize: 11, color: '#999' }}>{type.description}</div>
                    </div>
                  </div>
                </List.Item>
              )}
            />
          </div>
        ))
      )}
    </Card>
  );
};

export default NodePanel;
