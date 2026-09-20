# 经纬（JingWei）

![x-jingwei](https://img.shields.io/badge/x--jingwei-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-red)
![React](https://img.shields.io/badge/React-18+-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

[English](README.en.md) | 中文

## 项目简介

`经纬（JingWei）`是一个生产级的可视化工作流编排平台，专注于 LLM 应用开发与业务流程自动化。平台提供完整的 DAG 执行引擎、拖拽式节点编辑器和丰富的节点类型，支持从简单对话到复杂多步骤工作流的构建与执行。

**核心特征：**
- **可视化编排**：基于 React Flow 的拖拽式画布编辑器，零代码构建工作流
- **高性能引擎**：基于 Kahn 算法的 DAG 拓扑排序，支持并行执行与循环依赖检测
- **生产级架构**：五层业务架构（API → Service → Repository → Model → Infrastructure）
- **多节点支持**：LLM、代码、条件、HTTP、文档处理等 10+ 种节点类型
- **实时调试**：支持工作流实时执行、状态监控与结果可视化

**适配场景：**
- LLM 应用开发与调试
- 业务流程自动化与编排
- 数据处理流水线构建
- 多步骤任务协调与执行

## 快速开始

### 1. 环境要求

#### Windows
- Python 3.11+
- Node.js 18+ (前端开发)
- Git
- MySQL 8.0+ (可选，用于数据持久化)
- Docker Desktop (可选，用于容器部署)

#### Linux
- Python 3.11+
- Node.js 18+ (前端开发)
- Git
- MySQL 8.0+ (可选，用于数据持久化)
- Docker 与 Docker Compose (可选，用于容器部署)

#### macOS
- Python 3.11+ (推荐使用 Homebrew: `brew install python`)
- Node.js 18+ (前端开发)
- Git
- MySQL 8.0+ (可选，用于数据持久化)
- Docker Desktop for Mac (可选，用于容器部署)

### 2. 项目代码克隆

```bash
# 克隆仓库
git clone https://github.com/chain-engine/x-JingWei.git

# 进入项目目录
cd x-JingWei
```

### 3. 依赖同步安装

#### 后端依赖 (推荐使用 uv)

```bash
# 进入后端目录
cd server

# 安装 uv (如果未安装)
pip install uv

# 同步依赖
uv sync

# 或使用 pip (不推荐)
pip install -e .
```

#### 前端依赖

```bash
# 进入前端目录
cd web

# 安装依赖
npm install
# 或使用 yarn
yarn install
```

### 4. 环境配置

#### 数据库配置 (可选)

创建 MySQL 数据库：
```sql
CREATE DATABASE jingwei CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### 配置文件创建

在 `server/` 目录下创建 `.env` 文件：
```bash
# 复制示例配置
cp config.yaml.example config.yaml
# 或创建 .env 文件
touch .env
```

#### 核心参数说明

**数据库配置：**
- `DATABASE_URL`: MySQL 连接字符串 (格式: `mysql+pymysql://user:password@host:port/database`)
- `DATABASE_ASYNC_URL`: 异步 MySQL 连接字符串 (格式: `mysql+aiomysql://user:password@host:port/database`)

**LLM 配置：**
- `DEEPSEEK_API_KEY`: DeepSeek API 密钥
- `DOUBAO_API_KEY`: 豆包 API 密钥
- `LLM_DEFAULT_PROVIDER`: 默认 LLM 提供商 (deepseek/doubao)

**服务器配置：**
- `SERVER_HOST`: 服务器监听地址 (默认: 0.0.0.0)
- `SERVER_PORT`: 服务器端口 (默认: 8000)
- `SERVER_WORKERS`: 工作进程数 (默认: 1)

**日志配置：**
- `LOG_LEVEL`: 日志级别 (DEBUG/INFO/WARNING/ERROR)
- `LOG_FILE_PATH`: 日志文件路径 (默认: `logs/x-JingWei-{time}.log`)

### 5. 服务启动

#### 方式一：本地开发热重载 (推荐)

```bash
# 启动后端服务
cd server
uv run x-JingWei --reload

# 启动前端应用 (新终端)
cd web
npm run dev
```

访问地址：
- 前端应用: http://localhost:3000
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

#### 方式二：Docker 容器部署

```bash
# 构建并启动所有服务
docker compose up -d --build

# 查看日志
docker compose logs -f

# 停止服务
docker compose down
```

访问地址：
- 前端应用: http://localhost:3000
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

#### 方式三：uvicorn 直接启动 (可选)

```bash
# 启动后端
cd server
uv run python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 启动前端
cd web
npm run dev
```

### 6. 常用工程命令

#### 单元测试
```bash
# 运行所有测试
uv run pytest

# 运行特定测试文件
uv run pytest tests/test_api.py

# 运行带覆盖率的测试
uv run pytest --cov=src --cov-report=html
```

#### 代码格式化
```bash
# 使用 black 格式化
uv run black src/ tests/

# 使用 ruff 格式化
uv run ruff format src/ tests/
```

#### 静态代码检查
```bash
# 使用 ruff 检查
uv run ruff check src/ tests/

# 使用 mypy 类型检查
uv run mypy src/
```

#### 依赖漏洞扫描
```bash
# 使用 pip-audit 检查依赖漏洞
uv run pip-audit

# 或使用 safety
uv run safety check
```

### 7. 使用方法示例

#### 创建简单 LLM 对话工作流

1. **访问前端应用**: 打开 http://localhost:3000
2. **创建新工作流**: 点击 "新建工作流" 按钮
3. **拖拽节点**: 从左侧面板拖拽 "开始"、"LLM"、"结束" 节点到画布
4. **连接节点**: 将 "开始" 节点连接到 "LLM" 节点，再将 "LLM" 节点连接到 "结束" 节点
5. **配置节点**: 点击 "LLM" 节点，配置 prompt 和模型参数
6. **保存工作流**: 点击保存按钮
7. **执行工作流**: 点击执行按钮，查看执行结果

#### API 调用示例

```python
import requests

# 创建工作流
workflow_data = {
    "name": "简单对话",
    "description": "使用 LLM 进行对话",
    "nodes": [
        {"id": "start_1", "type": "start", "position": {"x": 100, "y": 200}, "data": {"label": "开始", "config": {}}},
        {"id": "llm_1", "type": "llm", "position": {"x": 300, "y": 200}, "data": {"label": "LLM", "config": {"prompt": "{{input}}", "model": "deepseek-chat"}}},
        {"id": "end_1", "type": "end", "position": {"x": 500, "y": 200}, "data": {"label": "结束", "config": {}}}
    ],
    "edges": [
        {"id": "edge_1", "source": "start_1", "target": "llm_1"},
        {"id": "edge_2", "source": "llm_1", "target": "end_1"}
    ]
}

response = requests.post("http://localhost:8000/api/v1/workflows", json=workflow_data)
workflow_id = response.json()["data"]["id"]

# 执行工作流
execution_data = {"inputs": {"input": "你好，请介绍一下自己"}}
response = requests.post(f"http://localhost:8000/api/v1/workflows/{workflow_id}/execute", json=execution_data)
print(response.json())
```

## 项目结构

```
x-JingWei/
├── server/                    # 后端服务
│   ├── src/                  # 核心业务代码
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
│   │   ├── infras/          # 基础设施层（第三方中间件封装）
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
│   ├── pyproject.toml        # 项目配置
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
│   ├── package.json          # 前端依赖配置
│   ├── vite.config.ts        # Vite 构建配置
│   ├── tsconfig.json         # TypeScript 配置
│   ├── README.md             # 前端文档
│   └── ...
├── docs/                      # 项目文档
├── scripts/                   # 部署运维脚本
├── docker-compose.yml         # Docker Compose 配置
├── LICENSE                    # MIT 许可证
├── README.md                  # 本文件
└── README.en.md               # 英文文档
```

**核心目录说明：**
- `server/src/api/`: API 接口层，仅负责参数接收、鉴权、转发调用、标准化返回
- `server/src/services/`: 业务逻辑层，处理业务规则、事务编排、多仓储联动
- `server/src/repositories/`: 数据访问层，封装业务 CRUD、多表联查、分页、条件查询
- `server/src/models/`: ORM 实体层，纯数据表映射模型
- `server/src/infras/`: 基础设施层，封装第三方中间件、客户端、连接生命周期
- `server/src/workflow/`: 工作流引擎核心，包含 DAG 引擎、执行器和节点实现
- `web/src/components/`: 前端 UI 组件，包含画布、节点、属性面板等
- `web/src/stores/`: Zustand 状态管理，管理应用状态

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

### 核心业务流程

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

## 技术栈

### 开发语言
- **Python 3.11+**: 后端主要开发语言
- **TypeScript 5+**: 前端主要开发语言
- **JavaScript**: 前端辅助语言
- **SQL**: 数据库查询语言

### Web 框架
- **FastAPI**: 高性能异步 Web 框架，支持 OpenAPI 自动生成
- **Uvicorn**: ASGI 服务器，支持热重载
- **React 18**: 前端 UI 框架，支持并发模式
- **Vite 5**: 前端构建工具，支持快速热重载

### 数据存储
- **MySQL 8.0+**: 关系型数据库，存储工作流数据
- **SQLAlchemy 2.0**: Python ORM 框架，支持异步操作
- **aiomysql**: 异步 MySQL 驱动

### 缓存 (可选)
- **Redis**: 内存数据库，用于缓存和会话存储
- **aioredis**: 异步 Redis 客户端

### 消息队列 (可选)
- **RabbitMQ**: 消息队列，用于异步任务处理
- **Celery**: 分布式任务队列

### 核心工具库
- **Pydantic v2**: 数据验证和序列化
- **Loguru**: 结构化日志记录
- **python-dotenv**: 环境变量管理
- **SlowAPI**: API 限流中间件
- **httpx**: 异步 HTTP 客户端

### 前端核心库
- **React Flow 11**: 节点编辑器库
- **Ant Design 5**: UI 组件库
- **Zustand**: 状态管理库
- **Axios**: HTTP 客户端
- **React Router 6**: 前端路由

### 部署运维工具
- **Docker**: 容器化部署
- **Docker Compose**: 多容器编排
- **uv**: 现代化 Python 包管理器
- **pytest**: Python 测试框架
- **black/ruff**: 代码格式化和检查工具

## API 文档说明

### 交互式文档访问

项目自动生成 OpenAPI 规范，提供以下文档访问方式：

1. **Swagger UI (交互式文档)**
   - 访问地址: http://localhost:8000/docs
   - 功能: 在线测试 API 接口、查看请求/响应示例

2. **ReDoc (只读文档)**
   - 访问地址: http://localhost:8000/redoc
   - 功能: 美观的 API 文档展示，适合阅读

3. **OpenAPI JSON 规范**
   - 访问地址: http://localhost:8000/openapi.json
   - 功能: 标准 OpenAPI 3.0 规范文件，可用于代码生成

### 核心 API 接口清单

#### 工作流管理
- `POST /api/v1/workflows` - 创建工作流
- `GET /api/v1/workflows` - 获取工作流列表
- `GET /api/v1/workflows/{id}` - 获取工作流详情
- `PUT /api/v1/workflows/{id}` - 更新工作流
- `DELETE /api/v1/workflows/{id}` - 删除工作流

#### 工作流执行
- `POST /api/v1/workflows/{id}/execute` - 执行工作流
- `POST /api/v1/workflows/{id}/validate` - 验证工作流
- `GET /api/v1/workflows/{id}/execution-plan` - 获取执行计划

#### 节点类型
- `GET /api/v1/workflows/node-types/list` - 获取节点类型列表
- `GET /api/v1/workflows/node-types/{type}` - 获取节点类型详情

#### 执行记录
- `GET /api/v1/workflows/executions/list` - 获取执行记录列表
- `GET /api/v1/workflows/executions/{execution_id}` - 获取执行记录详情

#### LLM 接口
- `POST /api/v1/llm/chat` - LLM 聊天完成
- `GET /api/v1/llm/providers` - 获取提供商列表

#### 文档接口
- `POST /api/v1/document/upload` - 上传文档
- `GET /api/v1/document/` - 获取文档列表
- `GET /api/v1/document/{document_id}` - 获取文档详情
- `DELETE /api/v1/document/{document_id}` - 删除文档

#### 系统接口
- `GET /api/v1/health` - 健康检查
- `GET /api/v1/version` - 版本信息

### 权限控制说明

- **公开接口**: 健康检查、版本信息、API 文档
- **认证接口**: 工作流管理、执行记录等需要 API 密钥认证
- **限流控制**: 默认 60 请求/分钟，1000 请求/小时
- **CORS 配置**: 默认允许所有来源，生产环境建议配置具体域名

## 存储配置说明

### 数据库存储

#### MySQL 配置
项目使用 MySQL 作为主要数据存储，配置参数如下：

```yaml
# config.yaml 示例
database:
  enabled: true
  url: "mysql+pymysql://root:123456@localhost:3306/jingwei?charset=utf8mb4"
  url_async: "mysql+aiomysql://root:123456@localhost:3306/jingwei?charset=utf8mb4"
  pool_size: 10
  max_overflow: 20
  pool_timeout: 30
  pool_recycle: 3600
  echo: false
```

**配置参数说明：**
- `url`: 同步数据库连接字符串
- `url_async`: 异步数据库连接字符串
- `pool_size`: 连接池大小
- `max_overflow`: 最大溢出连接数
- `pool_timeout`: 连接超时时间（秒）
- `pool_recycle`: 连接回收时间（秒）
- `echo`: 是否打印 SQL 语句

#### 数据库表结构

```sql
-- 工作流主表
CREATE TABLE workflows (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    status ENUM('draft', 'active', 'disabled') DEFAULT 'draft',
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 节点表
CREATE TABLE workflow_nodes (
    id VARCHAR(36) PRIMARY KEY,
    workflow_id VARCHAR(36) NOT NULL,
    type VARCHAR(50) NOT NULL,
    data JSON,
    position_x INT,
    position_y INT,
    FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE CASCADE
);

-- 边表
CREATE TABLE workflow_edges (
    id VARCHAR(36) PRIMARY KEY,
    workflow_id VARCHAR(36) NOT NULL,
    source VARCHAR(36) NOT NULL,
    target VARCHAR(36) NOT NULL,
    source_handle VARCHAR(255),
    target_handle VARCHAR(255),
    FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE CASCADE
);

-- 执行记录表
CREATE TABLE workflow_executions (
    id VARCHAR(36) PRIMARY KEY,
    workflow_id VARCHAR(36) NOT NULL,
    status ENUM('pending', 'running', 'completed', 'failed') DEFAULT 'pending',
    inputs JSON,
    outputs JSON,
    node_results JSON,
    error TEXT,
    start_time DATETIME,
    end_time DATETIME,
    duration_ms INT,
    FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE CASCADE
);
```

### 缓存存储 (可选)

#### Redis 配置
```yaml
# config.yaml 示例
redis:
  enabled: false
  url: "redis://localhost:6379/0"
  pool_size: 10
  max_connections: 50
  decode_responses: true
  socket_timeout: 5
```

**使用场景：**
- 会话缓存
- API 限流计数
- 临时数据存储

### 文件存储

项目支持本地文件存储，用于文档上传和处理：

- **上传目录**: `server/uploads/`
- **临时目录**: `server/temp/`
- **日志目录**: `server/logs/`

**注意事项：**
- 上传文件大小限制：10MB
- 支持文件类型：PDF、TXT、DOCX、MD
- 文件存储路径可在配置文件中修改

## 许可证

本项目基于 [MIT License](LICENSE) 开源。

MIT 许可证是一种宽松的许可证，允许用户自由使用、修改、分发软件，包括商业用途，只需保留版权声明和许可证声明。

## 参考资料

### 核心依赖官方文档

#### Python 生态
- [Python 官方文档](https://docs.python.org/3/)
- [uv 包管理器](https://github.com/astral-sh/uv)
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Pydantic 官方文档](https://docs.pydantic.dev/)
- [SQLAlchemy 官方文档](https://docs.sqlalchemy.org/)
- [Loguru 官方文档](https://loguru.readthedocs.io/)
- [pytest 官方文档](https://docs.pytest.org/)

#### 前端生态
- [React 官方文档](https://react.dev/)
- [TypeScript 官方文档](https://www.typescriptlang.org/)
- [Vite 官方文档](https://vitejs.dev/)
- [React Flow 官方文档](https://reactflow.dev/)
- [Ant Design 官方文档](https://ant.design/)
- [Zustand 官方文档](https://github.com/pmndrs/zustand)

#### 部署运维
- [Docker 官方文档](https://docs.docker.com/)
- [Docker Compose 官方文档](https://docs.docker.com/compose/)
- [MySQL 官方文档](https://dev.mysql.com/doc/)
- [Redis 官方文档](https://redis.io/documentation)

#### 代码质量
- [Black 代码格式化](https://black.readthedocs.io/)
- [Ruff 代码检查](https://docs.astral.sh/ruff/)
- [mypy 类型检查](https://mypy-lang.org/)

## 联系方式

| 项目 | 信息 |
|------|------|
| **作者** | John Young（夜雨诗来） |
| **邮箱** | john.young@foxmail.com |
| **Gitee** | https://gitee.com/yeyushilai |
| **GitHub** | https://github.com/yeyushilai |
| **项目地址** | https://github.com/chain-engine/x-JingWei |