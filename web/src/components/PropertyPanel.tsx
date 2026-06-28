/**
 * 属性面板 - 编辑选中节点的配置
 */

import React, { useEffect, useState } from 'react';
import { Card, Form, Input, InputNumber, Switch, Button, Space, Empty, Tabs } from 'antd';
import { DeleteOutlined, CloseOutlined } from '@ant-design/icons';
import useWorkflowStore from '@/stores/workflowStore';
const { TextArea } = Input;
const { TabPane } = Tabs;

const PropertyPanel: React.FC = () => {
  const {
    selectedNodeId,
    nodes,
    updateNode,
    removeNode,
    setSelectedNode,
    nodeTypes,
  } = useWorkflowStore();

  const [form] = Form.useForm();
  const [nodeType, setNodeType] = useState<any>(null);

  const selectedNode = nodes.find((n) => n.id === selectedNodeId);

  // 加载节点类型信息
  useEffect(() => {
    if (selectedNode) {
      const type = nodeTypes.find((t) => t.type === selectedNode.data.nodeType);
      setNodeType(type);

      // 设置表单初始值
      form.setFieldsValue({
        label: selectedNode.data.label,
        description: selectedNode.data.description,
        ...selectedNode.data.config,
      });
    }
  }, [selectedNode, nodeTypes, form]);

  // 表单值变化时更新节点
  const handleValuesChange = (changedValues: any) => {
    if (selectedNodeId) {
      const updates: any = {};

      if (changedValues.label !== undefined) {
        updates.label = changedValues.label;
      }
      if (changedValues.description !== undefined) {
        updates.description = changedValues.description;
      }

      // 其他配置项
      const configKeys = Object.keys(changedValues).filter(
        (k) => !['label', 'description'].includes(k)
      );
      if (configKeys.length > 0) {
        updates.config = {
          ...selectedNode?.data.config,
          ...configKeys.reduce((acc, key) => {
            acc[key] = changedValues[key];
            return acc;
          }, {} as any),
        };
      }

      updateNode(selectedNodeId, updates);
    }
  };

  // 删除节点
  const handleDelete = () => {
    if (selectedNodeId) {
      removeNode(selectedNodeId);
    }
  };

  // 关闭面板
  const handleClose = () => {
    setSelectedNode(null);
  };

  if (!selectedNode) {
    return (
      <Card title="属性面板" size="small" style={{ height: '100%' }}>
        <Empty description="请选择一个节点" style={{ marginTop: 40 }} />
      </Card>
    );
  }

  return (
    <Card
      title={
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>节点配置</span>
          <Space>
            <Button
              type="text"
              size="small"
              icon={<DeleteOutlined />}
              danger
              onClick={handleDelete}
            >
              删除
            </Button>
            <Button
              type="text"
              size="small"
              icon={<CloseOutlined />}
              onClick={handleClose}
            />
          </Space>
        </div>
      }
      size="small"
      style={{ height: '100%', overflow: 'auto' }}
    >
      <Form
        form={form}
        layout="vertical"
        onValuesChange={handleValuesChange}
        size="small"
      >
        <Form.Item name="label" label="节点名称" rules={[{ required: true }]}>
          <Input placeholder="输入节点名称" />
        </Form.Item>

        <Form.Item name="description" label="节点描述">
          <TextArea rows={2} placeholder="输入节点描述" />
        </Form.Item>

        {nodeType?.inputs?.length > 0 && (
          <Tabs size="small">
            <TabPane tab="配置" key="config">
              {nodeType.inputs.map((input: any) => (
                <Form.Item
                  key={input.name}
                  name={input.name}
                  label={input.label}
                  rules={input.required ? [{ required: true }] : []}
                >
                  {renderInput(input)}
                </Form.Item>
              ))}
            </TabPane>
          </Tabs>
        )}

        <div style={{ marginTop: 16, padding: 12, background: '#f5f5f5', borderRadius: 4 }}>
          <div style={{ fontSize: 12, color: '#666', marginBottom: 8 }}>节点信息</div>
          <div style={{ fontSize: 11, color: '#999' }}>
            <div>ID: {selectedNode.id}</div>
            <div>类型: {nodeType?.label || selectedNode.data.nodeType}</div>
            <div>
              位置: ({Math.round(selectedNode.position.x)},{' '}
              {Math.round(selectedNode.position.y)})
            </div>
          </div>
        </div>
      </Form>
    </Card>
  );
};

// 根据输入类型渲染对应的表单组件
function renderInput(input: any) {
  switch (input.type) {
    case 'string':
      if (input.name === 'prompt' || input.name === 'code' || input.name === 'condition') {
        return <TextArea rows={4} placeholder={`输入${input.label}`} />;
      }
      return <Input placeholder={`输入${input.label}`} />;

    case 'number':
      return (
        <InputNumber
          style={{ width: '100%' }}
          min={input.min}
          max={input.max}
          step={input.step || 0.1}
        />
      );

    case 'boolean':
      return <Switch />;

    case 'array':
    case 'object':
      return <TextArea rows={4} placeholder={`输入JSON格式的${input.label}`} />;

    default:
      return <Input placeholder={`输入${input.label}`} />;
  }
}

export default PropertyPanel;
