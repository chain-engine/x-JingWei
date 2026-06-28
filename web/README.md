# Web - 工作流可视化编辑器

## 概述

基于 React + React Flow 构建的可视化工作流编辑器，提供拖拽式节点编辑、连线配置和工作流执行管理功能。

## 技术栈

- **框架**: React 18 + TypeScript
- **编辑器**: React Flow 11
- **UI**: Ant Design 5
- **状态管理**: Zustand
- **路由**: React Router 6
- **HTTP 客户端**: Axios
- **构建工具**: Vite 5

## 项目结构

```
web/
├── src/
│   ├── components/           # UI 组件
│   │   ├── WorkflowCanvas.tsx    # 工作流画布
│   │   ├── WorkflowNode.tsx      # 自定义节点组件
│   │   ├── NodePanel.tsx         # 节点类型面板
│   │   └── PropertyPanel.tsx     # 属性编辑面板
│   ├── pages/                # 页面
│   │   ├── WorkflowList.tsx      # 工作流列表页
│   │   └── Editor.tsx            # 工作流编辑器页
│   ├── stores/               # 状态管理
│   │   └── workflowStore.ts      # 工作流状态
│   ├── types/                # 类型定义
│   │   └── workflow.ts           # 工作流类型
│   ├── utils/                # 工具
│   │   └── api.ts               # API 客户端
│   ├── App.tsx               # 应用入口
│   └── main.tsx              # 渲染入口
├── package.json
├── tsconfig.json
└── vite.config.ts            # Vite 配置
```

## 快速开始

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

### 生产构建

```bash
npm run build
npm run preview
```

## 页面功能

### 工作流列表页（/）

- 查看所有工作流列表
- 搜索工作流
- 新建工作流
- 编辑/删除/复制工作流
- 一键执行工作流

### 工作流编辑器页（/editor, /editor/:id）

采用三栏布局：

```
┌──────────┬─────────────────────┬──────────┐
│ 节点面板  │                     │ 属性面板  │
│          │      画布区域        │          │
│ 拖拽创建  │  React Flow         │ 配置编辑  │
│ 节点类型  │                     │          │
├──────────┤  顶部工具栏           ├──────────┤
│ 控制/处理 │  保存/验证/执行      │ 节点信息  │
│ 流程/工具 │  导出/导入           │          │
└──────────┴─────────────────────┴──────────┘
```

### 节点面板

节点按分类组织，支持拖拽到画布创建：

- **控制**: 开始、结束
- **处理**: LLM、代码、转换
- **流程**: 条件、并行、聚合
- **工具**: HTTP、文档

### 画布操作

- **拖拽创建**: 从左侧面板拖拽节点到画布
- **连线**: 从节点右边连接点拖拽到另一个节点
- **选择**: 点击节点/边进行选择
- **删除**: 选中后按 Delete 键或在属性面板删除
- **拖拽移动**: 选中节点后拖拽移动位置
- **缩放/平移**: 鼠标滚轮缩放，右键拖拽平移

### 属性面板

选中节点后在右侧编辑：

- 节点名称和描述
- 节点配置参数（根据类型动态渲染）
- 节点运行时信息

## 与后端交互

前端通过 `/api/v1/workflows/*` 路径调用后端 API：

| 功能         | API 路径                                      |
|-------------|-----------------------------------------------|
| 创建工作流   | POST /api/v1/workflows                        |
| 获取工作流   | GET /api/v1/workflows/{id}                    |
| 更新工作流   | PUT /api/v1/workflows/{id}                    |
| 执行工作流   | POST /api/v1/workflows/{id}/execute           |
| 验证工作流   | POST /api/v1/workflows/{id}/validate          |
| 获取节点类型 | GET /api/v1/workflows/node-types/list         |
| 获取执行记录 | GET /api/v1/workflows/executions/list         |

## 环境配置

后端代理在 `vite.config.ts` 中配置：

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```


---

## 联系方式

| 项目 | 信息 |
|------|------|
| **作者** | John Young |
| **邮箱** | john.young@foxmail.com |
| **Gitee** | https://gitee.com/yeyushilai |
| **GitHub** | https://github.com/yeyushilai |
| **项目地址** | https://gitee.com/chain-engine/x-jingwei |
