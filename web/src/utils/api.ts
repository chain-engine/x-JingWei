/**
 * API 客户端
 */

import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { Workflow, WorkflowExecution, ExecutionPlan, NodeTypeInfo } from '@/types/workflow';

// 创建 axios 实例
const api: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 响应拦截器
api.interceptors.response.use(
  (response: AxiosResponse) => {
    if (response.data && response.data.code === 200) {
      return response.data.data;
    }
    return response.data;
  },
  (error) => {
    const message = error.response?.data?.message || error.message || '请求失败';
    return Promise.reject(new Error(message));
  }
);

// API 方法
export const workflowApi = {
  // 工作流 CRUD
  create: (data: Partial<Workflow>): Promise<Workflow> => 
    api.post('/workflows', data),
  
  list: (params?: { page?: number; page_size?: number; status?: string }): Promise<{
    items: Workflow[];
    total: number;
    page: number;
    page_size: number;
  }> => api.get('/workflows', { params }),
  
  get: (id: string): Promise<Workflow> => 
    api.get(`/workflows/${id}`),
  
  update: (id: string, data: Partial<Workflow>): Promise<Workflow> => 
    api.put(`/workflows/${id}`, data),
  
  delete: (id: string): Promise<void> => 
    api.delete(`/workflows/${id}`),
  
  // 执行相关
  execute: (id: string, inputs?: Record<string, any>): Promise<WorkflowExecution> => 
    api.post(`/workflows/${id}/execute`, { inputs }),
  
  validate: (id: string): Promise<{ valid: boolean; error?: string; execution_plan?: ExecutionPlan }> => 
    api.post(`/workflows/${id}/validate`),
  
  getExecutionPlan: (id: string): Promise<ExecutionPlan> => 
    api.get(`/workflows/${id}/execution-plan`),
  
  // 节点类型
  listNodeTypes: (): Promise<NodeTypeInfo[]> => 
    api.get('/workflows/node-types/list'),
  
  getNodeType: (type: string): Promise<NodeTypeInfo> => 
    api.get(`/workflows/node-types/${type}`),
  
  // 执行记录
  listExecutions: (params?: { workflow_id?: string; page?: number; page_size?: number }): Promise<{
    items: Array<{
      execution_id: string;
      workflow_id: string;
      status: string;
      start_time?: string;
      end_time?: string;
      duration_ms?: number;
      error?: string;
    }>;
    total: number;
    page: number;
    page_size: number;
  }> => api.get('/workflows/executions/list', { params }),
  
  getExecution: (executionId: string): Promise<WorkflowExecution> => 
    api.get(`/workflows/executions/${executionId}`),
};

export default api;
