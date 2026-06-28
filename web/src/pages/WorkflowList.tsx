/**
 * 工作流列表页面
 */

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Layout,
  Card,
  Table,
  Button,
  Space,
  Tag,
  Popconfirm,
  message,
  Input,
  Row,
  Col,
} from 'antd';
import {
  PlusOutlined,
  PlayCircleOutlined,
  EditOutlined,
  DeleteOutlined,
  CopyOutlined,
} from '@ant-design/icons';
import { workflowApi } from '@/utils/api';
import { Workflow, WorkflowStatus } from '@/types/workflow';

const { Header, Content } = Layout;

const statusColors: Record<WorkflowStatus, string> = {
  draft: 'default',
  active: 'success',
  disabled: 'error',
  running: 'processing',
  completed: 'success',
  failed: 'error',
  paused: 'warning',
};

const statusLabels: Record<WorkflowStatus, string> = {
  draft: '草稿',
  active: '已激活',
  disabled: '已禁用',
  running: '运行中',
  completed: '已完成',
  failed: '失败',
  paused: '已暂停',
};

const WorkflowList: React.FC = () => {
  const navigate = useNavigate();
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');

  // 加载工作流列表
  const loadWorkflows = async () => {
    setLoading(true);
    try {
      const result = await workflowApi.list();
      setWorkflows(result.items);
    } catch (error: any) {
      message.error(`加载失败: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadWorkflows();
  }, []);

  // 删除工作流
  const handleDelete = async (id: string) => {
    try {
      await workflowApi.delete(id);
      message.success('删除成功');
      loadWorkflows();
    } catch (error: any) {
      message.error(`删除失败: ${error.message}`);
    }
  };

  // 复制工作流
  const handleCopy = async (workflow: Workflow) => {
    try {
      const newWorkflow = {
        ...workflow,
        name: `${workflow.name} (复制)`,
        id: undefined,
        status: 'draft' as WorkflowStatus,
      };
      await workflowApi.create(newWorkflow);
      message.success('复制成功');
      loadWorkflows();
    } catch (error: any) {
      message.error(`复制失败: ${error.message}`);
    }
  };

  // 执行工作流
  const handleExecute = async (id: string) => {
    try {
      const result = await workflowApi.execute(id, {});
      if (result.status === 'completed') {
        message.success('执行成功');
      } else {
        message.error(`执行失败: ${result.error}`);
      }
    } catch (error: any) {
      message.error(`执行失败: ${error.message}`);
    }
  };

  // 过滤工作流
  const filteredWorkflows = workflows.filter((w) =>
    w.name.toLowerCase().includes(searchText.toLowerCase()) ||
    w.description?.toLowerCase().includes(searchText.toLowerCase())
  );

  const columns = [
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: Workflow) => (
        <div>
          <div style={{ fontWeight: 500 }}>{text}</div>
          <div style={{ fontSize: 12, color: '#999' }}>{record.description}</div>
        </div>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: WorkflowStatus) => (
        <Tag color={statusColors[status]}>{statusLabels[status]}</Tag>
      ),
    },
    {
      title: '版本',
      dataIndex: 'version',
      key: 'version',
      width: 80,
    },
    {
      title: '节点数',
      key: 'nodeCount',
      width: 80,
      render: (record: Workflow) => record.nodes?.length || 0,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => date ? new Date(date).toLocaleString() : '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 250,
      render: (record: Workflow) => (
        <Space size="small">
          <Button
            type="text"
            size="small"
            icon={<EditOutlined />}
            onClick={() => navigate(`/editor/${record.id}`)}
          >
            编辑
          </Button>
          <Button
            type="text"
            size="small"
            icon={<PlayCircleOutlined />}
            onClick={() => handleExecute(record.id!)}
          >
            执行
          </Button>
          <Button
            type="text"
            size="small"
            icon={<CopyOutlined />}
            onClick={() => handleCopy(record)}
          >
            复制
          </Button>
          <Popconfirm
            title="确认删除"
            description="删除后无法恢复，是否继续？"
            onConfirm={() => handleDelete(record.id!)}
            okText="删除"
            cancelText="取消"
            okButtonProps={{ danger: true }}
          >
            <Button type="text" size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#fff', borderBottom: '1px solid #f0f0f0', padding: '0 24px' }}>
        <Row align="middle" justify="space-between">
          <Col>
            <h1 style={{ margin: 0, fontSize: 20 }}>经纬工作流平台</h1>
          </Col>
          <Col>
            <Space align="center">
              <Input.Search
                placeholder="搜索工作流"
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                style={{ width: 250 }}
                size="middle"
              />
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => navigate('/editor')}
                size="middle"
              >
                新建工作流
              </Button>
            </Space>
          </Col>
        </Row>
      </Header>

      <Content style={{ padding: 24 }}>
        <Card>
          <Table
            columns={columns}
            dataSource={filteredWorkflows}
            rowKey="id"
            loading={loading}
            pagination={{
              pageSize: 10,
              showSizeChanger: true,
              showTotal: (total) => `共 ${total} 条`,
            }}
          />
        </Card>
      </Content>
    </Layout>
  );
};

export default WorkflowList;
