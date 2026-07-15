# 经纬（JingWei）

<div align="center">

![x-jingwei](https://img.shields.io/badge/x--jingwei-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-red)
![React](https://img.shields.io/badge/React-18+-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

**一个生产级的可视化工作流编排平台**

前端可视化编辑器 + 后端DAG执行引擎

</div>

## 项目简介

JingWei（经纬）是一个生产级的可视化工作流编排平台，提供：

- **可视化工作流编辑器**：基于 React Flow 的拖拽式节点编辑器
- **DAG 执行引擎**：支持拓扑排序、并行执行的工作流引擎
- **多节点类型**：LLM、代码、条件、HTTP、文档处理等多种节点
- **实时执行**：支持工作流的实时执行和调试

## 系统架构

### 系统分层架构

```mermaid
graph TB
    subgraph 前端层["前端层 (Web)"]
        UI[React UI 组件<br/>Ant Design + React Flow]
        Store[Zustand 状态管理]
        API[Axios API 客户端]
        UI --> Store
        Store --> API
    end

    subgraph API网关层["API 网关层 (FastAPI)"]
        Router[API 路由]
        MW[中间件<br/>CORS / 限流 / 日志]
        Handler[请求处理器<br/>CRUD + 执行 + 验证]
        Router --> MW
        MW --> Handler
    end

    subgraph 服务层["服务层"]
        WFE[WorkflowExecutor<br/>工作流执行器]
        LLMS[LLMService<br/>LLM 服务]
        DocS[DocumentService<br/>文档服务]
    end

    subgraph 引擎层["引擎层"]
        DAG[DAGEngine<br/>拓扑排序 / 并行调度]
        EG[ExecutionGraph<br/>执行图管理]
        NR[NodeRegistry<br/>节点注册表]
        DAG --> EG
        EG --> NR
    end

    subgraph 节点层["节点执行层"]
        N1[StartNode]
        N2[LLMNode]
        N3[CodeNode]
        N4[ConditionNode]
        N5[HTTPNode]
        N6[TransformNode]
        N7[ParallelNode]
        N8[AggregateNode]
        N9[DocumentNode]
    end

    subgraph 存储层["数据层"]
        MySQL[(MySQL<br/>关系型数据库)]
        Base[Base<br/>SQLAlchemy ORM]
        MySQL --> Base
    end

    API --> 服务层
    服务层 --> 引擎层
    引擎层 --> 节点层
    Handler --> WFE
    WFE --> DAG
    NR --> 节点层
    WFE --> MySQL
    Handler --> MySQL

    classDef frontend fill:#e3f2fd,stroke:#1565c0
    classDef api fill:#fff3e0,stroke:#e65100
    classDef service fill:#e8f5e9,stroke:#2e7d32
    classDef engine fill:#fce4ec,stroke:#c62828
    classDef node fill:#f3e5f5,stroke:#6a1b9a
    classDef storage fill:#e1f5fe,stroke:#0277bd

    class 前端层 frontend
    class API网关层 api
    class 服务层 service
    class 引擎层 engine
    class 节点层 node
    class 存储层 storage
```

### 核心功能业务流程

```mermaid
sequenceDiagram
    participant User as 用户 (浏览器)
    participant ReactFlow as 画布编辑器
    participant API as 后端 API
    participant Executor as 工作流执行器
    participant DAG as DAG 引擎
    participant Nodes as 节点执行器

    Note over User,Nodes: 设计阶段
    User->>ReactFlow: 拖拽节点到画布
    User->>ReactFlow: 连接节点形成 DAG
    User->>ReactFlow: 配置节点参数
    User->>ReactFlow: 点击保存
    ReactFlow->>API: POST /workflows (JSON)
    API->>API: 验证工作流
    API->>API: 存储工作流
    API-->>ReactFlow: 返回工作流 ID

    Note over User,Nodes: 执行阶段
    User->>ReactFlow: 点击执行
    ReactFlow->>API: POST /workflows/{id}/execute
    
    API->>Executor: 启动执行
    Executor->>DAG: validate_workflow()
    DAG-->>Executor: 验证结果
    
    Executor->>DAG: topological_sort()
    DAG-->>Executor: [start, llm, end]
    
    loop 逐层执行
        Executor->>DAG: get_ready_nodes()
        DAG-->>Executor: 就绪节点列表
        par 并行执行就绪节点
            Executor->>Nodes: execute(node)
            Nodes-->>Executor: ExecutionResult
        end
        Executor->>DAG: 记录执行结果
    end
    
    Executor-->>API: WorkflowExecution
    API-->>ReactFlow: 执行结果
    ReactFlow-->>User: 展示执行状态
```

### 模块依赖关系

```mermaid
graph LR
    subgraph 后端依赖
        FastAPI[FastAPI] --> Pydantic[Pydantic v2]
        FastAPI --> Uvicorn[Uvicorn]
        FastAPI --> SlowAPI[SlowAPI 限流]
        FastAPI --> Loguru[Loguru 日志]
    end

    subgraph 前端依赖
        React[React 18] --> ReactFlow[React Flow 11]
        React --> Antd[Ant Design 5]
        React --> ReactRouter[React Router 6]
        React --> Zustand[Zustand]
        React --> Axios[Axios]
        Vite[Vite 5] --> TypeScript[TypeScript 5]
    end

    subgraph 项目模块
        Server["server/<br/>后端核心"] --> Workflow["workflow/<br/>工作流引擎"]
        Server --> API["api/v1/<br/>HTTP 接口"]
        Server --> Core["core/<br/>基础框架"]
        Workflow --> Engine["engine<br/>DAG 执行"]
        Workflow --> Executor["executor<br/>执行调度"]
        Workflow --> Nodes["nodes<br/>节点类型"]
        Workflow --> Models["models<br/>数据模型"]
        Web["web/<br/>前端应用"] --> Components["components<br/>UI 组件"]
        Web --> Pages["pages<br/>页面"]
        Web --> Stores["stores<br/>状态管理"]
    end

    Web -.->|HTTP API| Server

    classDef core fill:#e3f2fd,stroke:#1565c0
    classDef infra fill:#f5f5f5,stroke:#616161

    class Server,Web core
    class FastAPI,Uvicorn,React,Vite infra
```

## 项目结构

```
x-jingwei/
├── server/                    # 后端服务
│   ├── src/
│   │   ├── api/              # API 接口层（极薄，仅参数转发）
│   │   │   └── v1/
│   │   │       ├── workflow.py    # 工作流 CRUD & 执行 API
│   │   │       ├── llm.py         # LLM 聊天接口
│   │   │       ├── document.py    # 文档处理接口
│   │   │       ├── health.py      # 健康检查
│   │   │       └── version.py     # 版本信息
│   │   ├── core/             # 核心支撑层
│   │   │   ├── config.py     # 全局配置中心
│   │   │   ├── container.py  # IOC依赖注入容器
│   │   │   ├── middleware.py # 中间件
│   │   │   ├── exceptions.py # 全局异常定义
│   │   │   ├── logger.py     # 日志配置
│   │   │   └── response.py   # 统一响应封装
│   │   ├── services/         # 业务逻辑层
│   │   │   ├── llm_service.py      # LLM 业务服务
│   │   │   ├── document_service.py # 文档业务服务
│   │   │   └── workflow_service.py # 工作流业务服务
│   │   ├── repositories/     # 数据访问层
│   │   │   ├── base.py           # Repository 基类
│   │   │   ├── workflow_repository.py
│   │   │   └── document_repository.py
│   │   ├── models/           # ORM 实体层（数据表映射）
│   │   │   ├── base.py           # SQLAlchemy 基类
│   │   │   └── workflow.py       # 工作流实体模型
│   │   ├── schemas/          # API Schema（Pydantic 请求/响应模型）
│   │   │   ├── base.py           # Schema 基类
│   │   │   ├── common.py         # 通用参数（分页等）
│   │   │   ├── workflow.py       # 工作流相关 Schema
│   │   │   ├── llm.py            # LLM 相关 Schema
│   │   │   └── document.py       # 文档相关 Schema
│   │   ├── infra/            # 基础设施层（第三方中间件封装）
│   │   │   └── mysql/
│   │   │       ├── __init__.py   # 导出数据库连接管理模块
│   │   │       └── mysql.py      # 数据库连接管理
│   │   ├── workflow/         # 工作流引擎核心
│   │   │   ├── engine.py     # DAG执行引擎(拓扑排序/并行/验证)
│   │   │   ├── executor.py   # 工作流执行器
│   │   │   └── nodes.py      # 10+ 种节点类型实现
│   │   ├── utils/            # 无状态工具函数
│   │   ├── constants/        # 全局常量定义
│   │   └── main.py           # 应用入口
│   ├── tests/                # 自动化测试（目录层级与 src 对应）
│   ├── logs/                 # 运行时日志（按小时切割）
│   ├── examples/             # 功能演示示例
│   ├── scripts/              # 部署运维脚本
│   ├── .env                  # 本地私有配置（禁止提交）
│   ├── .env.example          # 无密钥配置模板（允许提交）
│   ├── config.yaml           # YAML 配置文件
│   ├── README.md             # 后端文档
│   └── ...
├── web/                       # 前端应用
│   ├── src/
│   │   ├── components/       # 组件
│   │   │   ├── WorkflowCanvas.tsx   # 画布组件(React Flow)
│   │   │   ├── WorkflowNode.tsx     # 自定义节点组件
│   │   │   ├── NodePanel.tsx        # 可拖拽节点面板
│   │   │   └── PropertyPanel.tsx    # 属性编辑面板
│   │   ├── pages/           # 页面
│   │   │   ├── WorkflowList.tsx     # 工作流列表
│   │   │   └── Editor.tsx           # 三栏编辑器
│   │   ├── stores/          # Zustand 状态管理
│   │   ├── types/           # TypeScript 类型定义
│   │   └── utils/           # API 客户端
│   ├── README.md             # 前端文档
│   └── ...
└── README.md                 # 本文件
```

## 架构分层

后端采用标准五层业务架构 + 通用核心支撑层：

### 标准五层业务架构（自上而下）

| 层级 | 目录 | 职责 |
|------|------|------|
| **API 接口层** | `api/` | 仅负责参数接收、鉴权、转发调用、标准化返回，无业务逻辑 |
| **业务逻辑层** | `services/` | 处理业务规则、事务编排、多仓储联动、复杂业务计算 |
| **数据访问层** | `repositories/` | 封装业务 CRUD、多表联查、分页、条件查询 |
| **ORM 实体层** | `models/` | 纯数据表映射模型，仅定义字段、表关联关系 |
| **基础设施层** | `infra/` | 封装第三方中间件、客户端、连接生命周期、底层资源管理 |

### 核心支撑层

| 目录 | 职责 |
|------|------|
| `core/` | 框架级底层核心能力（配置、日志、异常、中间件、IOC容器、标准化响应） |
| `schemas/` | 统一存放接口请求入参、响应返回 Pydantic 模型 |
| `constants/` | 全局常量、业务模块常量、状态枚举定义 |
| `utils/` | 无状态纯工具函数（加密、日期、文件、序列化、脱敏工具） |
| `common/` | 业务通用公共组件（业务基类、通用装饰器、全局枚举、分页封装） |

### 层间依赖规则

```
api → service → repository → models/infra
          ↓
       utils/schemas/constants/common/core
```

- 依赖流向不可逆、禁止跨层直接调用
- `repository` 引用 `models` 实体
- `repository` 依赖 `infra` 获取数据库/缓存会话资源
- `models`、`infra` 不依赖上层任何业务层代码

## 快速开始

### 0. 数据库配置

确保 MySQL 服务已启动，并创建数据库：

```sql
CREATE DATABASE jingwei CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

配置数据库连接（通过环境变量或 .env 文件）：

```bash
# 环境变量
export DATABASE_URL="mysql+pymysql://root:123456@localhost:3306/jingwei?charset=utf8mb4"
export ASYNC_DATABASE_URL="mysql+aiomysql://root:123456@localhost:3306/jingwei?charset=utf8mb4"
```

或创建 `.env` 文件在 `server/src/config/` 目录：

```env
DATABASE_URL=mysql+pymysql://root:123456@localhost:3306/jingwei?charset=utf8mb4
ASYNC_DATABASE_URL=mysql+aiomysql://root:123456@localhost:3306/jingwei?charset=utf8mb4
```

### 1. 启动后端服务

```bash
cd server

# 安装依赖
uv sync

# 启动服务（热重载）
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. 启动前端应用

```bash
cd web

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 3. 访问应用

- 前端: http://localhost:3000（若被占用会自动分配其他端口）
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

## 功能特性

### 工作流引擎

- ✅ **拓扑排序**：基于 Kahn 算法的 DAG 拓扑排序
- ✅ **并行执行**：支持同层级节点并行执行
- ✅ **循环依赖检测**：自动检测并报告循环依赖
- ✅ **执行计划**：生成可视化的执行计划
- ✅ **关键路径分析**：识别工作流的关键路径

### 节点类型

- ✅ **开始/结束**：控制工作流的起点和终点
- ✅ **LLM**：调用大语言模型
- ✅ **代码**：执行 Python 代码
- ✅ **条件**：条件分支判断
- ✅ **HTTP**：发送 HTTP 请求
- ✅ **转换**：数据转换处理
- ✅ **并行/聚合**：支持并行分支和结果聚合
- ✅ **文档**：文档处理（解析、分块、摘要）

### 前端编辑器

- ✅ **拖拽创建**：从节点面板拖拽创建节点
- ✅ **连线编辑**：连接节点配置数据流
- ✅ **属性配置**：编辑节点配置参数
- ✅ **导入/导出**：支持 JSON 格式的导入导出
- ✅ **执行调试**：实时执行并查看结果

## API 接口

### 工作流管理

- `POST /api/v1/workflows` - 创建工作流
- `GET /api/v1/workflows` - 获取工作流列表
- `GET /api/v1/workflows/{id}` - 获取工作流详情
- `PUT /api/v1/workflows/{id}` - 更新工作流
- `DELETE /api/v1/workflows/{id}` - 删除工作流

### 工作流执行

- `POST /api/v1/workflows/{id}/execute` - 执行工作流
- `POST /api/v1/workflows/{id}/validate` - 验证工作流
- `GET /api/v1/workflows/{id}/execution-plan` - 获取执行计划

### 节点类型

- `GET /api/v1/workflows/node-types/list` - 获取节点类型列表
- `GET /api/v1/workflows/node-types/{type}` - 获取节点类型详情

### 执行记录

- `GET /api/v1/workflows/executions/list` - 获取执行记录列表
- `GET /api/v1/workflows/executions/{execution_id}` - 获取执行记录详情

## 示例工作流

创建一个简单的 LLM 对话工作流：

```json
{
  "name": "简单对话",
  "description": "使用 LLM 进行对话",
  "nodes": [
    {
      "id": "start_1",
      "type": "start",
      "position": { "x": 100, "y": 200 },
      "data": { "label": "开始", "config": {} }
    },
    {
      "id": "llm_1",
      "type": "llm",
      "position": { "x": 300, "y": 200 },
      "data": {
        "label": "LLM",
        "config": {
          "prompt": "{{input}}",
          "model": "deepseek-chat"
        }
      }
    },
    {
      "id": "end_1",
      "type": "end",
      "position": { "x": 500, "y": 200 },
      "data": { "label": "结束", "config": {} }
    }
  ],
  "edges": [
    { "id": "edge_1", "source": "start_1", "target": "llm_1" },
    { "id": "edge_2", "source": "llm_1", "target": "end_1" }
  ]
}
```

## 技术栈

### 后端

- **FastAPI**：高性能异步 Web 框架
- **Pydantic**：数据验证和序列化
- **SQLAlchemy**：ORM 数据库访问
- **aiomysql**：异步 MySQL 驱动
- **UV**：现代化 Python 包管理

### 前端

- **React 18**：UI 框架
- **TypeScript**：类型安全
- **React Flow**：节点编辑器
- **Ant Design**：UI 组件库
- **Zustand**：状态管理
- **Axios**：HTTP 客户端

## 数据库设计

系统使用 MySQL 数据库存储工作流数据，主要包含以下表：

### ER 图

```mermaid
erDiagram
    WORKFLOWS ||--o{ WORKFLOW_NODES : contains
    WORKFLOWS ||--o{ WORKFLOW_EDGES : contains
    WORKFLOWS ||--o{ WORKFLOW_EXECUTIONS : has

    WORKFLOWS {
        string id PK "工作流ID"
        string name "名称"
        enum status "状态(draft/active/disabled)"
        text description "描述"
        datetime created_at "创建时间"
        datetime updated_at "更新时间"
    }

    WORKFLOW_NODES {
        string id PK "节点ID"
        string workflow_id FK "工作流ID"
        enum type "节点类型"
        json data "节点配置数据"
        int position_x "X坐标"
        int position_y "Y坐标"
    }

    WORKFLOW_EDGES {
        string id PK "边ID"
        string workflow_id FK "工作流ID"
        string source "源节点ID"
        string target "目标节点ID"
        string source_handle "源Handle"
        string target_handle "目标Handle"
    }

    WORKFLOW_EXECUTIONS {
        string id PK "执行ID"
        string workflow_id FK "工作流ID"
        enum status "执行状态"
        json inputs "输入参数"
        json outputs "输出结果"
        json node_results "节点执行结果"
        text error "错误信息"
        datetime start_time "开始时间"
        datetime end_time "结束时间"
        int duration_ms "执行时长(ms)"
    }
```

### 数据模型

- **Workflow**：工作流主表，存储工作流的基本信息
- **WorkflowNode**：节点表，存储工作流中的所有节点
- **WorkflowEdge**：边表，存储节点之间的连接关系
- **WorkflowExecution**：执行记录表，存储每次执行的详细信息

## 开发计划

- [x] 数据库持久化（MySQL + SQLAlchemy）
- [ ] 用户认证和权限管理
- [ ] 工作流版本控制
- [ ] 执行历史记录
- [ ] WebSocket 实时执行状态
- [ ] 更多节点类型（数据库、缓存、消息队列等）
- [ ] 工作流模板市场

## License

MIT License


---

## 联系方式

| 项目 | 信息 |
|------|------|
| **作者** | John Young |
| **邮箱** | john.young@foxmail.com |
| **Gitee** | https://gitee.com/yeyushilai |
| **GitHub** | https://github.com/yeyushilai |
| **项目地址** | https://gitee.com/chain-engine/x-jingwei |
