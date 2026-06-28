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
│   ├── api/                  # API 层
│   │   ├── v1/
│   │   │   ├── workflow.py   # 工作流 CRUD & 执行接口
│   │   │   ├── llm.py        # LLM 接口
│   │   │   ├── document.py   # 文档接口
│   │   │   ├── health.py     # 健康检查
│   │   │   └── version.py    # 版本信息
│   │   └── router.py         # 路由管理
│   ├── workflow/             # 工作流引擎核心
│   │   ├── models.py         # 数据模型
│   │   ├── engine.py         # DAG执行引擎
│   │   ├── executor.py       # 工作流执行器
│   │   └── nodes.py          # 节点类型定义
│   ├── core/                 # 核心模块
│   │   ├── config.py         # 配置管理
│   │   ├── container.py      # 依赖注入容器
│   │   ├── middleware.py     # 中间件
│   │   └── ...
│   ├── services/             # 业务服务
│   ├── models/               # 数据模型
│   └── main.py               # 应用入口
├── config/                   # 配置文件
│   ├── config.yaml           # YAML配置
│   └── .env.example          # 环境变量示例
└── pyproject.toml            # 项目配置
```

## 工作流引擎架构

```
┌──────────────────────────────────────────┐
│              API 层                       │
│   POST /workflows/execute                │
│   GET  /workflows/execution-plan         │
│   POST /workflows/validate               │
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
