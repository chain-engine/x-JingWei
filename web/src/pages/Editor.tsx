/**
 * 工作流编辑器页面
 */

import React, { useEffect } from 'react';
import { Layout, Row, Col, Input, Button, Space, message } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';

import NodePanel from '@/components/NodePanel';
import WorkflowCanvas from '@/components/WorkflowCanvas';
import PropertyPanel from '@/components/PropertyPanel';
import useWorkflowStore from '@/stores/workflowStore';
import { workflowApi } from '@/utils/api';

const { Header, Content } = Layout;

const Editor: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  
  const {
    currentWorkflow,
    setCurrentWorkflow,
    setLoading,
  } = useWorkflowStore();

  // 加载工作流
  useEffect(() => {
    if (id) {
      const loadWorkflow = async () => {
        setLoading(true);
        try {
          const workflow = await workflowApi.get(id);
          setCurrentWorkflow(workflow);
        } catch (error: any) {
          message.error(`加载工作流失败: ${error.message}`);
          navigate('/');
        } finally {
          setLoading(false);
        }
      };

      loadWorkflow();
    } else {
      // 新建工作流
      setCurrentWorkflow({
        name: '未命名工作流',
        description: '',
        version: '1.0.0',
        nodes: [],
        edges: [],
        inputs: [],
        outputs: [],
        metadata: { tags: [] },
        settings: {},
        status: 'draft',
      });
    }

    return () => {
      setCurrentWorkflow(null);
    };
  }, [id, setCurrentWorkflow, setLoading, navigate]);

  // 更新工作流名称
  const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (currentWorkflow) {
      setCurrentWorkflow({
        ...currentWorkflow,
        name: e.target.value,
      });
    }
  };

  // 更新工作流描述
  const handleDescriptionChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (currentWorkflow) {
      setCurrentWorkflow({
        ...currentWorkflow,
        description: e.target.value,
      });
    }
  };

  return (
    <Layout style={{ height: '100vh' }}>
      <Header style={{ background: '#fff', borderBottom: '1px solid #f0f0f0', padding: '0 24px' }}>
        <Row align="middle" justify="space-between">
          <Col>
            <Space>
              <Button
                type="text"
                icon={<ArrowLeftOutlined />}
                onClick={() => navigate('/')}
              >
                返回
              </Button>
              <Input
                value={currentWorkflow?.name || ''}
                onChange={handleNameChange}
                placeholder="工作流名称"
                style={{ width: 200, fontWeight: 500 }}
                variant="borderless"
              />
              <Input
                value={currentWorkflow?.description || ''}
                onChange={handleDescriptionChange}
                placeholder="工作流描述"
                style={{ width: 300 }}
                variant="borderless"
              />
            </Space>
          </Col>
          <Col>
            <Space>
              <span style={{ color: '#999', fontSize: 12 }}>
                {id ? '编辑模式' : '新建模式'}
              </span>
            </Space>
          </Col>
        </Row>
      </Header>

      <Content style={{ padding: 0, height: 'calc(100vh - 64px)' }}>
        <Row style={{ height: '100%' }} gutter={0}>
          {/* 左侧节点面板 */}
          <Col span={4} style={{ height: '100%', borderRight: '1px solid #f0f0f0' }}>
            <NodePanel />
          </Col>

          {/* 中间画布 */}
          <Col span={16} style={{ height: '100%' }}>
            <WorkflowCanvas workflowId={id} />
          </Col>

          {/* 右侧属性面板 */}
          <Col span={4} style={{ height: '100%', borderLeft: '1px solid #f0f0f0' }}>
            <PropertyPanel />
          </Col>
        </Row>
      </Content>
    </Layout>
  );
};

export default Editor;
