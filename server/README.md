# Server - 工作流后端服务

## 概述

基于 FastAPI 构建的生产级工作流后端服务，提供完整的 DAG 执行引擎、节点管理和工作流编排能力。

## 技术栈

- **框架**: FastAPI + Uvicorn
- **数据验证**: Pydantic v2
- **异步支持**: asyncio
- **依赖管理**: UV

## 项目结构

```
server/
├── src/
│   ├── api/                  # API 接口层（极薄，仅参数转发）
│   │   ├── v1/
│   │   │   ├── workflow.py   # 工作流 CRUD & 执行接口
│   │   │   ├── llm.py        # LLM 聊天接口
│   │   │   ├── document.py   # 文档处理接口
│   │   │   ├── health.py     # 健康检查
│   │   │   └── version.py    # 版本信息
│   │   └── router.py         # 路由管理
│   ├── service/              # 业务逻辑层
│   │   ├── llm_service.py    # LLM 业务服务
│   │   └── document_service.py # 文档业务服务
│   ├── repositories/         # 数据访问层
│   │   ├── base.py           # Repository 基类
│   │   ├── workflow_repository.py
│   │   └── document_repository.py
│   ├── models/               # ORM 实体层（数据表映射）
│   │   ├── base.py           # SQLAlchemy 基类
│   │   └── workflow.py       # 工作流实体模型
│   ├── schemas/              # API Schema（Pydantic 请求/响应模型）
│   │   ├── base.py           # Schema 基类
│   │   ├── common.py         # 通用参数（分页等）
│   │   ├── workflow.py       # 工作流相关 Schema
│   │   ├── llm.py            # LLM 相关 Schema
│   │   └── document.py       # 文档相关 Schema
│   ├── core/                 # 核心支撑层
│   │   ├── config.py         # 全局配置中心
│   │   ├── container.py      # IOC依赖注入容器
│   │   ├── middleware.py     # 中间件
│   │   ├── exceptions.py     # 全局异常定义
│   │   ├── logger.py         # 日志配置
│   │   └── response.py       # 统一响应封装
│   ├── infra/                # 基础设施层
│   │   └── mysql/
│   │       ├── models.py     # SQLAlchemy 基类定义
│   │       └── mysql.py      # 数据库连接管理
│   ├── workflow/             # 工作流引擎核心
│   │   ├── engine.py         # DAG执行引擎
│   │   ├── executor.py       # 工作流执行器
│   │   └── nodes.py          # 节点类型定义
│   ├── constants/            # 全局常量定义
│   ├── utils/                # 无状态工具函数
│   └── main.py               # 应用入口
├── tests/                    # 自动化测试（目录层级与 src 对应）
├── logs/                     # 运行时日志（按小时切割）
├── examples/                 # 功能演示示例
├── scripts/                  # 部署运维脚本
├── .env                      # 本地私有配置（禁止提交）
├── .env.example              # 无密钥配置模板（允许提交）
├── config.yaml               # YAML 配置文件
└── pyproject.toml            # 项目配置
```

## 架构分层

### 标准五层业务架构（自上而下）

| 层级 | 目录 | 职责 |
|------|------|------|
| **API 接口层** | `api/` | 仅负责参数接收、鉴权、转发调用、标准化返回，无业务逻辑 |
| **业务逻辑层** | `service/` | 处理业务规则、事务编排、多仓储联动、复杂业务计算 |
| **数据访问层** | `repositories/` | 封装业务 CRUD、多表联查、分页、条件查询 |
| **ORM 实体层** | `models/` | 纯数据表映射模型，仅定义字段、表关联关系 |
| **基础设施层** | `infra/` | 封装第三方中间件、客户端、连接生命周期、底层资源管理 |

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

## 工作流引擎架构

```
┌──────────────────────────────────────────┐
│              API 层                       │
│   POST /workflows/execute                │
│   GET  /workflows/execution-plan         │
│   POST /workflows/validate               │
│   (仅参数转发，无业务逻辑)                 │
└──────────────┬───────────────────────────┘
               ↓
┌──────────────────────────────────────────┐
│            Service 层                     │
│   - 业务规则处理                          │
│   - 事务编排                              │
│   - 多仓储联动                            │
└──────────────┬───────────────────────────┘
               ↓
┌──────────────────────────────────────────┐
│            WorkflowExecutor               │
│   - 执行流程编排                          │
│   - 并行/串行调度                         │
│   - 错误处理                              │
└──────────────┬───────────────────────────┘
               ↓
┌──────────────────────────────────────────┐
│            DAGEngine                      │
│   - 拓扑排序 (Kahn算法)                   │
│   - 执行层级划分                          │
│   - 循环依赖检测                          │
│   - 关键路径分析                          │
└──────────────┬───────────────────────────┘
               ↓
┌──────────────────────────────────────────┐
│         ExecutionGraph                    │
│   - 节点执行状态管理                      │
│   - 上下文传递                            │
│   - 结果收集                              │
└──────────────┬───────────────────────────┘
               ↓
┌──────────────────────────────────────────┐
│            NodeRegistry                   │
│   10+ 种节点类型实现                      │
│   - LLMNode / CodeNode                   │
│   - ConditionNode / HTTPNode             │
│   - TransformNode / DocumentNode         │
│   - ParallelNode / AggregateNode         │
└──────────────────────────────────────────┘
```

## 快速开始

### 安装依赖

```bash
# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install -e .
```

### 启动服务

```bash
# 开发模式（热重载）
uv run uvicorn src.main:app --reload --port 8000

# 或直接运行
uv run python src/main.py
```

### 访问 API

- API 文档: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc
- 健康检查: http://localhost:8000/api/v1/health

## API 接口

### 工作流管理

| 方法   | 路径                                    | 说明         |
|--------|-----------------------------------------|--------------|
| POST   | /api/v1/workflows                       | 创建工作流   |
| GET    | /api/v1/workflows                       | 列表工作流   |
| GET    | /api/v1/workflows/{id}                  | 获取工作流   |
| PUT    | /api/v1/workflows/{id}                  | 更新工作流   |
| DELETE | /api/v1/workflows/{id}                  | 删除工作流   |

### 工作流执行

| 方法   | 路径                                            | 说明         |
|--------|-------------------------------------------------|--------------|
| POST   | /api/v1/workflows/{id}/execute                  | 执行工作流   |
| POST   | /api/v1/workflows/{id}/validate                 | 验证工作流   |
| GET    | /api/v1/workflows/{id}/execution-plan           | 获取执行计划 |

### 节点类型

| 方法 | 路径                                      | 说明           |
|------|-------------------------------------------|----------------|
| GET  | /api/v1/workflows/node-types/list         | 获取节点类型列表 |
| GET  | /api/v1/workflows/node-types/{type}       | 获取节点类型详情 |

### 执行记录

| 方法 | 路径                                       | 说明           |
|------|--------------------------------------------|----------------|
| GET  | /api/v1/workflows/executions/list          | 获取执行记录列表 |
| GET  | /api/v1/workflows/executions/{exec_id}     | 获取执行记录详情 |

### LLM 接口

| 方法 | 路径                                       | 说明           |
|------|--------------------------------------------|----------------|
| POST | /api/v1/llm/chat                           | LLM 聊天完成   |
| GET  | /api/v1/llm/providers                      | 获取提供商列表 |

### 文档接口

| 方法   | 路径                                       | 说明           |
|--------|--------------------------------------------|----------------|
| POST   | /api/v1/document/upload                    | 上传文档       |
| GET    | /api/v1/document/                          | 获取文档列表   |
| GET    | /api/v1/document/{document_id}             | 获取文档详情   |
| DELETE | /api/v1/document/{document_id}             | 删除文档       |

## 节点类型

| 类型      | 说明               | 输入配置                     |
|-----------|-------------------|-----------------------------|
| start     | 开始节点           | 无                          |
| end       | 结束节点           | 无                          |
| llm       | LLM 调用节点       | prompt, model, temperature  |
| code      | 代码执行节点       | code, input_data            |
| condition | 条件分支节点       | condition                   |
| http      | HTTP 请求节点      | url, method, headers, body  |
| transform | 数据转换节点       | input_data, transform_type  |
| parallel  | 并行分支节点       | branches                    |
| aggregate | 结果聚合节点       | aggregate_type              |
| document  | 文档处理节点       | content, operation          |

## 引擎特性

- **拓扑排序**: 基于 Kahn 算法的 DAG 拓扑排序
- **并行执行**: 同层级无依赖节点自动并行执行
- **循环依赖检测**: 自动检测并报告循环依赖
- **变量模板**: 支持 `{{variable}}` 模板语法
- **执行计划**: 生成可视化执行计划
- **关键路径**: 识别工作流关键路径

## 测试

```bash
uv run pytest
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