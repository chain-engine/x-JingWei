# JingWei

![x-jingwei](https://img.shields.io/badge/x--jingwei-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-red)
![React](https://img.shields.io/badge/React-18+-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

[中文](README.md) | English

## Project Introduction

`JingWei` is a production-grade visual workflow orchestration platform focused on LLM application development and business process automation. The platform provides a complete DAG execution engine, drag-and-drop node editor, and rich node types, supporting the construction and execution from simple conversations to complex multi-step workflows.

**Core Features:**
- **Visual Orchestration**: Drag-and-drop canvas editor based on React Flow for zero-code workflow construction
- **High-Performance Engine**: DAG topological sorting based on Kahn algorithm, supporting parallel execution and cycle dependency detection
- **Production-Grade Architecture**: Five-layer business architecture (API → Service → Repository → Model → Infrastructure)
- **Multi-Node Support**: 10+ node types including LLM, code, condition, HTTP, document processing
- **Real-time Debugging**: Support workflow real-time execution, status monitoring, and result visualization

**Application Scenarios:**
- LLM application development and debugging
- Business process automation and orchestration
- Data processing pipeline construction
- Multi-step task coordination and execution

## Quick Start

### 1. Environment Requirements

#### Windows
- Python 3.11+
- Node.js 18+ (for frontend development)
- Git
- MySQL 8.0+ (optional, for data persistence)
- Docker Desktop (optional, for container deployment)

#### Linux
- Python 3.11+
- Node.js 18+ (for frontend development)
- Git
- MySQL 8.0+ (optional, for data persistence)
- Docker and Docker Compose (optional, for container deployment)

#### macOS
- Python 3.11+ (recommended via Homebrew: `brew install python`)
- Node.js 18+ (for frontend development)
- Git
- MySQL 8.0+ (optional, for data persistence)
- Docker Desktop for Mac (optional, for container deployment)

### 2. Project Code Cloning

```bash
# Clone repository
git clone https://github.com/chain-engine/x-JingWei.git

# Enter project directory
cd x-JingWei
```

### 3. Dependency Synchronization Installation

#### Backend Dependencies (Recommended using uv)

```bash
# Enter backend directory
cd server

# Install uv (if not installed)
pip install uv

# Synchronize dependencies
uv sync

# Or use pip (not recommended)
pip install -e .
```

#### Frontend Dependencies

```bash
# Enter frontend directory
cd web

# Install dependencies
npm install
# Or use yarn
yarn install
```

### 4. Environment Configuration

#### Database Configuration (Optional)

Create MySQL database:
```sql
CREATE DATABASE jingwei CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### Configuration File Creation

Create `.env` file in `server/` directory:
```bash
# Copy example configuration
cp config.yaml.example config.yaml
# Or create .env file
touch .env
```

#### Core Parameter Description

**Database Configuration:**
- `DATABASE_URL`: MySQL connection string (format: `mysql+pymysql://user:password@host:port/database`)
- `DATABASE_ASYNC_URL`: Async MySQL connection string (format: `mysql+aiomysql://user:password@host:port/database`)

**LLM Configuration:**
- `DEEPSEEK_API_KEY`: DeepSeek API key
- `DOUBAO_API_KEY`: Doubao API key
- `LLM_DEFAULT_PROVIDER`: Default LLM provider (deepseek/doubao)

**Server Configuration:**
- `SERVER_HOST`: Server listening address (default: 0.0.0.0)
- `SERVER_PORT`: Server port (default: 8000)
- `SERVER_WORKERS`: Worker processes (default: 1)

**Log Configuration:**
- `LOG_LEVEL`: Log level (DEBUG/INFO/WARNING/ERROR)
- `LOG_FILE_PATH`: Log file path (default: `logs/x-JingWei-{time}.log`)

### 5. Service Startup

#### Method 1: Local Development with Hot Reload (Recommended)

```bash
# Start backend service
cd server
uv run x-JingWei --reload

# Start frontend application (new terminal)
cd web
npm run dev
```

Access addresses:
- Frontend application: http://localhost:3000
- Backend API: http://localhost:8000
- API documentation: http://localhost:8000/docs

#### Method 2: Docker Container Deployment

```bash
# Build and start all services
docker compose up -d --build

# View logs
docker compose logs -f

# Stop services
docker compose down
```

Access addresses:
- Frontend application: http://localhost:3000
- Backend API: http://localhost:8000
- API documentation: http://localhost:8000/docs

#### Method 3: uvicorn Direct Startup (Optional)

```bash
# Start backend
cd server
uv run python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend
cd web
npm run dev
```

### 6. Common Engineering Commands

#### Unit Testing
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_api.py

# Run tests with coverage
uv run pytest --cov=src --cov-report=html
```

#### Code Formatting
```bash
# Format with black
uv run black src/ tests/

# Format with ruff
uv run ruff format src/ tests/
```

#### Static Code Analysis
```bash
# Check with ruff
uv run ruff check src/ tests/

# Type check with mypy
uv run mypy src/
```

#### Dependency Vulnerability Scanning
```bash
# Check dependency vulnerabilities with pip-audit
uv run pip-audit

# Or use safety
uv run safety check
```

### 7. Usage Examples

#### Creating a Simple LLM Conversation Workflow

1. **Access frontend application**: Open http://localhost:3000
2. **Create new workflow**: Click "New Workflow" button
3. **Drag nodes**: Drag "Start", "LLM", "End" nodes from left panel to canvas
4. **Connect nodes**: Connect "Start" node to "LLM" node, then connect "LLM" node to "End" node
5. **Configure node**: Click "LLM" node, configure prompt and model parameters
6. **Save workflow**: Click save button
7. **Execute workflow**: Click execute button, view execution results

#### API Call Example

```python
import requests

# Create workflow
workflow_data = {
    "name": "Simple Conversation",
    "description": "Use LLM for conversation",
    "nodes": [
        {"id": "start_1", "type": "start", "position": {"x": 100, "y": 200}, "data": {"label": "Start", "config": {}}},
        {"id": "llm_1", "type": "llm", "position": {"x": 300, "y": 200}, "data": {"label": "LLM", "config": {"prompt": "{{input}}", "model": "deepseek-chat"}}},
        {"id": "end_1", "type": "end", "position": {"x": 500, "y": 200}, "data": {"label": "End", "config": {}}}
    ],
    "edges": [
        {"id": "edge_1", "source": "start_1", "target": "llm_1"},
        {"id": "edge_2", "source": "llm_1", "target": "end_1"}
    ]
}

response = requests.post("http://localhost:8000/api/v1/workflows", json=workflow_data)
workflow_id = response.json()["data"]["id"]

# Execute workflow
execution_data = {"inputs": {"input": "Hello, please introduce yourself"}}
response = requests.post(f"http://localhost:8000/api/v1/workflows/{workflow_id}/execute", json=execution_data)
print(response.json())
```

## Project Structure

```
x-JingWei/
├── server/                    # Backend service
│   ├── src/                  # Core business code
│   │   ├── api/              # API interface layer (thin, only parameter forwarding)
│   │   │   └── v1/
│   │   │       ├── workflow.py    # Workflow CRUD & execution API
│   │   │       ├── llm.py         # LLM chat interface
│   │   │       ├── document.py    # Document processing interface
│   │   │       ├── health.py      # Health check
│   │   │       └── version.py     # Version information
│   │   ├── core/             # Core support layer
│   │   │   ├── config.py     # Global configuration center
│   │   │   ├── container.py  # IOC dependency injection container
│   │   │   ├── middleware.py # Middleware
│   │   │   ├── exceptions.py # Global exception definitions
│   │   │   ├── logger.py     # Log configuration
│   │   │   └── response.py   # Unified response encapsulation
│   │   ├── services/         # Business logic layer
│   │   │   ├── llm_service.py      # LLM business service
│   │   │   ├── document_service.py # Document business service
│   │   │   └── workflow_service.py # Workflow business service
│   │   ├── repositories/     # Data access layer
│   │   │   ├── base.py           # Repository base class
│   │   │   ├── workflow_repository.py
│   │   │   └── document_repository.py
│   │   ├── models/           # ORM entity layer (data table mapping)
│   │   │   ├── base.py           # SQLAlchemy base class
│   │   │   └── workflow.py       # Workflow entity model
│   │   ├── schemas/          # API Schema (Pydantic request/response models)
│   │   │   ├── base.py           # Schema base class
│   │   │   ├── common.py         # Common parameters (pagination, etc.)
│   │   │   ├── workflow.py       # Workflow related Schema
│   │   │   ├── llm.py            # LLM related Schema
│   │   │   └── document.py       # Document related Schema
│   │   ├── infras/          # Infrastructure layer (third-party middleware encapsulation)
│   │   │   └── mysql/
│   │   │       ├── __init__.py   # Export database connection management module
│   │   │       └── mysql.py      # Database connection management
│   │   ├── workflow/         # Workflow engine core
│   │   │   ├── engine.py     # DAG execution engine (topological sorting/parallel/validation)
│   │   │   ├── executor.py   # Workflow executor
│   │   │   └── nodes.py      # 10+ node type implementations
│   │   ├── utils/            # Stateless utility functions
│   │   ├── constants/        # Global constant definitions
│   │   └── main.py           # Application entry point
│   ├── tests/                # Automated tests (directory hierarchy corresponds to src)
│   ├── logs/                 # Runtime logs (hourly rotation)
│   ├── examples/             # Feature demonstration examples
│   ├── scripts/              # Deployment and operation scripts
│   ├── .env                  # Local private configuration (prohibited to submit)
│   ├── .env.example          # No-secret configuration template (allowed to submit)
│   ├── config.yaml           # YAML configuration file
│   ├── pyproject.toml        # Project configuration
│   ├── README.md             # Backend documentation
│   └── ...
├── web/                       # Frontend application
│   ├── src/
│   │   ├── components/       # Components
│   │   │   ├── WorkflowCanvas.tsx   # Canvas component (React Flow)
│   │   │   ├── WorkflowNode.tsx     # Custom node component
│   │   │   ├── NodePanel.tsx        # Draggable node panel
│   │   │   └── PropertyPanel.tsx    # Property editing panel
│   │   ├── pages/           # Pages
│   │   │   ├── WorkflowList.tsx     # Workflow list
│   │   │   └── Editor.tsx           # Three-column editor
│   │   ├── stores/          # Zustand state management
│   │   ├── types/           # TypeScript type definitions
│   │   └── utils/           # API client
│   ├── package.json          # Frontend dependency configuration
│   ├── vite.config.ts        # Vite build configuration
│   ├── tsconfig.json         # TypeScript configuration
│   ├── README.md             # Frontend documentation
│   └── ...
├── docs/                      # Project documentation
├── scripts/                   # Deployment and operation scripts
├── docker-compose.yml         # Docker Compose configuration
├── LICENSE                    # MIT License
├── README.md                  # Chinese documentation
└── README.en.md               # This file
```

**Core Directory Description:**
- `server/src/api/`: API interface layer, only responsible for parameter receiving, authentication, forwarding calls, standardized returns
- `server/src/services/`: Business logic layer, handles business rules, transaction orchestration, multi-repository linkage
- `server/src/repositories/`: Data access layer, encapsulates business CRUD, multi-table queries, pagination, conditional queries
- `server/src/models/`: ORM entity layer, pure data table mapping models
- `server/src/infras/`: Infrastructure layer, encapsulates third-party middleware, clients, connection lifecycle
- `server/src/workflow/`: Workflow engine core, includes DAG engine, executor, and node implementations
- `web/src/components/`: Frontend UI components, includes canvas, nodes, property panels
- `web/src/stores/`: Zustand state management, manages application state

## System Architecture

### System Layered Architecture

```mermaid
graph TB
    subgraph FrontendLayer["Frontend Layer (Web)"]
        UI[React UI Components<br/>Ant Design + React Flow]
        Store[Zustand State Management]
        API[Axios API Client]
        UI --> Store
        Store --> API
    end

    subgraph APIGatewayLayer["API Gateway Layer (FastAPI)"]
        Router[API Router]
        MW[Middleware<br/>CORS / Rate Limiting / Logging]
        Handler[Request Handler<br/>CRUD + Execution + Validation]
        Router --> MW
        MW --> Handler
    end

    subgraph ServiceLayer["Service Layer"]
        WFE[WorkflowExecutor<br/>Workflow Executor]
        LLMS[LLMService<br/>LLM Service]
        DocS[DocumentService<br/>Document Service]
    end

    subgraph EngineLayer["Engine Layer"]
        DAG[DAGEngine<br/>Topological Sorting / Parallel Scheduling]
        EG[ExecutionGraph<br/>Execution Graph Management]
        NR[NodeRegistry<br/>Node Registry]
        DAG --> EG
        EG --> NR
    end

    subgraph NodeLayer["Node Execution Layer"]
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

    subgraph StorageLayer["Data Layer"]
        MySQL[(MySQL<br/>Relational Database)]
        Base[Base<br/>SQLAlchemy ORM]
        MySQL --> Base
    end

    API --> ServiceLayer
    ServiceLayer --> EngineLayer
    EngineLayer --> NodeLayer
    Handler --> WFE
    WFE --> DAG
    NR --> NodeLayer
    WFE --> MySQL
    Handler --> MySQL

    classDef frontend fill:#e3f2fd,stroke:#1565c0
    classDef api fill:#fff3e0,stroke:#e65100
    classDef service fill:#e8f5e9,stroke:#2e7d32
    classDef engine fill:#fce4ec,stroke:#c62828
    classDef node fill:#f3e5f5,stroke:#6a1b9a
    classDef storage fill:#e1f5fe,stroke:#0277bd

    class FrontendLayer frontend
    class APIGatewayLayer api
    class ServiceLayer service
    class EngineLayer engine
    class NodeLayer node
    class StorageLayer storage
```

### Core Business Process

```mermaid
sequenceDiagram
    participant User as User (Browser)
    participant ReactFlow as Canvas Editor
    participant API as Backend API
    participant Executor as Workflow Executor
    participant DAG as DAG Engine
    participant Nodes as Node Executors

    Note over User,Nodes: Design Phase
    User->>ReactFlow: Drag nodes to canvas
    User->>ReactFlow: Connect nodes to form DAG
    User->>ReactFlow: Configure node parameters
    User->>ReactFlow: Click save
    ReactFlow->>API: POST /workflows (JSON)
    API->>API: Validate workflow
    API->>API: Store workflow
    API-->>ReactFlow: Return workflow ID

    Note over User,Nodes: Execution Phase
    User->>ReactFlow: Click execute
    ReactFlow->>API: POST /workflows/{id}/execute
    
    API->>Executor: Start execution
    Executor->>DAG: validate_workflow()
    DAG-->>Executor: Validation result
    
    Executor->>DAG: topological_sort()
    DAG-->>Executor: [start, llm, end]
    
    loop Execute layer by layer
        Executor->>DAG: get_ready_nodes()
        DAG-->>Executor: Ready node list
        par Execute ready nodes in parallel
            Executor->>Nodes: execute(node)
            Nodes-->>Executor: ExecutionResult
        end
        Executor->>DAG: Record execution results
    end
    
    Executor-->>API: WorkflowExecution
    API-->>ReactFlow: Execution result
    ReactFlow-->>User: Display execution status
```

### Module Dependency Relationship

```mermaid
graph LR
    subgraph BackendDependencies
        FastAPI[FastAPI] --> Pydantic[Pydantic v2]
        FastAPI --> Uvicorn[Uvicorn]
        FastAPI --> SlowAPI[SlowAPI Rate Limiting]
        FastAPI --> Loguru[Loguru Logging]
    end

    subgraph FrontendDependencies
        React[React 18] --> ReactFlow[React Flow 11]
        React --> Antd[Ant Design 5]
        React --> ReactRouter[React Router 6]
        React --> Zustand[Zustand]
        React --> Axios[Axios]
        Vite[Vite 5] --> TypeScript[TypeScript 5]
    end

    subgraph ProjectModules
        Server["server/<br/>Backend Core"] --> Workflow["workflow/<br/>Workflow Engine"]
        Server --> API["api/v1/<br/>HTTP Interface"]
        Server --> Core["core/<br/>Basic Framework"]
        Workflow --> Engine["engine<br/>DAG Execution"]
        Workflow --> Executor["executor<br/>Execution Scheduling"]
        Workflow --> Nodes["nodes<br/>Node Types"]
        Workflow --> Models["models<br/>Data Models"]
        Web["web/<br/>Frontend Application"] --> Components["components<br/>UI Components"]
        Web --> Pages["pages<br/>Pages"]
        Web --> Stores["stores<br/>State Management"]
    end

    Web -.->|HTTP API| Server

    classDef core fill:#e3f2fd,stroke:#1565c0
    classDef infra fill:#f5f5f5,stroke:#616161

    class Server,Web core
    class FastAPI,Uvicorn,React,Vite infra
```

## Technology Stack

### Development Languages
- **Python 3.11+**: Main backend development language
- **TypeScript 5+**: Main frontend development language
- **JavaScript**: Frontend auxiliary language
- **SQL**: Database query language

### Web Frameworks
- **FastAPI**: High-performance asynchronous Web framework, supports OpenAPI auto-generation
- **Uvicorn**: ASGI server, supports hot reload
- **React 18**: Frontend UI framework, supports concurrent mode
- **Vite 5**: Frontend build tool, supports fast hot reload

### Data Storage
- **MySQL 8.0+**: Relational database, stores workflow data
- **SQLAlchemy 2.0**: Python ORM framework, supports asynchronous operations
- **aiomysql**: Asynchronous MySQL driver

### Cache (Optional)
- **Redis**: In-memory database, used for caching and session storage
- **aioredis**: Asynchronous Redis client

### Message Queue (Optional)
- **RabbitMQ**: Message queue, used for asynchronous task processing
- **Celery**: Distributed task queue

### Core Tool Libraries
- **Pydantic v2**: Data validation and serialization
- **Loguru**: Structured logging
- **python-dotenv**: Environment variable management
- **SlowAPI**: API rate limiting middleware
- **httpx**: Asynchronous HTTP client

### Frontend Core Libraries
- **React Flow 11**: Node editor library
- **Ant Design 5**: UI component library
- **Zustand**: State management library
- **Axios**: HTTP client
- **React Router 6**: Frontend routing

### Deployment and Operation Tools
- **Docker**: Containerized deployment
- **Docker Compose**: Multi-container orchestration
- **uv**: Modern Python package manager
- **pytest**: Python testing framework
- **black/ruff**: Code formatting and checking tools

## API Documentation

### Interactive Documentation Access

The project auto-generates OpenAPI specifications, providing the following documentation access methods:

1. **Swagger UI (Interactive Documentation)**
   - Access URL: http://localhost:8000/docs
   - Function: Online testing of API interfaces, viewing request/response examples

2. **ReDoc (Read-only Documentation)**
   - Access URL: http://localhost:8000/redoc
   - Function: Beautiful API documentation display, suitable for reading

3. **OpenAPI JSON Specification**
   - Access URL: http://localhost:8000/openapi.json
   - Function: Standard OpenAPI 3.0 specification file, can be used for code generation

### Core API Interface List

#### Workflow Management
- `POST /api/v1/workflows` - Create workflow
- `GET /api/v1/workflows` - Get workflow list
- `GET /api/v1/workflows/{id}` - Get workflow details
- `PUT /api/v1/workflows/{id}` - Update workflow
- `DELETE /api/v1/workflows/{id}` - Delete workflow

#### Workflow Execution
- `POST /api/v1/workflows/{id}/execute` - Execute workflow
- `POST /api/v1/workflows/{id}/validate` - Validate workflow
- `GET /api/v1/workflows/{id}/execution-plan` - Get execution plan

#### Node Types
- `GET /api/v1/workflows/node-types/list` - Get node type list
- `GET /api/v1/workflows/node-types/{type}` - Get node type details

#### Execution Records
- `GET /api/v1/workflows/executions/list` - Get execution record list
- `GET /api/v1/workflows/executions/{execution_id}` - Get execution record details

#### LLM Interface
- `POST /api/v1/llm/chat` - LLM chat completion
- `GET /api/v1/llm/providers` - Get provider list

#### Document Interface
- `POST /api/v1/document/upload` - Upload document
- `GET /api/v1/document/` - Get document list
- `GET /api/v1/document/{document_id}` - Get document details
- `DELETE /api/v1/document/{document_id}` - Delete document

#### System Interface
- `GET /api/v1/health` - Health check
- `GET /api/v1/version` - Version information

### Access Control Description

- **Public Interfaces**: Health check, version information, API documentation
- **Authenticated Interfaces**: Workflow management, execution records, etc. require API key authentication
- **Rate Limiting Control**: Default 60 requests/minute, 1000 requests/hour
- **CORS Configuration**: Default allows all origins, production environment recommends configuring specific domains

## Storage Configuration Description

### Database Storage

#### MySQL Configuration
The project uses MySQL as the main data storage, with the following configuration parameters:

```yaml
# config.yaml example
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

**Configuration Parameter Description:**
- `url`: Synchronous database connection string
- `url_async`: Asynchronous database connection string
- `pool_size`: Connection pool size
- `max_overflow`: Maximum overflow connection count
- `pool_timeout`: Connection timeout (seconds)
- `pool_recycle`: Connection recycle time (seconds)
- `echo`: Whether to print SQL statements

#### Database Table Structure

```sql
-- Workflow main table
CREATE TABLE workflows (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    status ENUM('draft', 'active', 'disabled') DEFAULT 'draft',
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Node table
CREATE TABLE workflow_nodes (
    id VARCHAR(36) PRIMARY KEY,
    workflow_id VARCHAR(36) NOT NULL,
    type VARCHAR(50) NOT NULL,
    data JSON,
    position_x INT,
    position_y INT,
    FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE CASCADE
);

-- Edge table
CREATE TABLE workflow_edges (
    id VARCHAR(36) PRIMARY KEY,
    workflow_id VARCHAR(36) NOT NULL,
    source VARCHAR(36) NOT NULL,
    target VARCHAR(36) NOT NULL,
    source_handle VARCHAR(255),
    target_handle VARCHAR(255),
    FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE CASCADE
);

-- Execution record table
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

### Cache Storage (Optional)

#### Redis Configuration
```yaml
# config.yaml example
redis:
  enabled: false
  url: "redis://localhost:6379/0"
  pool_size: 10
  max_connections: 50
  decode_responses: true
  socket_timeout: 5
```

**Usage Scenarios:**
- Session caching
- API rate limiting counting
- Temporary data storage

### File Storage

The project supports local file storage for document upload and processing:

- **Upload Directory**: `server/uploads/`
- **Temporary Directory**: `server/temp/`
- **Log Directory**: `server/logs/`

**Notes:**
- Upload file size limit: 10MB
- Supported file types: PDF, TXT, DOCX, MD
- File storage path can be modified in configuration file

## License

This project is licensed under the [MIT License](LICENSE).

The MIT License is a permissive license that allows users to freely use, modify, and distribute software, including commercial use, as long as the copyright notice and license notice are preserved.

## References

### Core Dependency Official Documentation

#### Python Ecosystem
- [Python Official Documentation](https://docs.python.org/3/)
- [uv Package Manager](https://github.com/astral-sh/uv)
- [FastAPI Official Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Official Documentation](https://docs.pydantic.dev/)
- [SQLAlchemy Official Documentation](https://docs.sqlalchemy.org/)
- [Loguru Official Documentation](https://loguru.readthedocs.io/)
- [pytest Official Documentation](https://docs.pytest.org/)

#### Frontend Ecosystem
- [React Official Documentation](https://react.dev/)
- [TypeScript Official Documentation](https://www.typescriptlang.org/)
- [Vite Official Documentation](https://vitejs.dev/)
- [React Flow Official Documentation](https://reactflow.dev/)
- [Ant Design Official Documentation](https://ant.design/)
- [Zustand Official Documentation](https://github.com/pmndrs/zustand)

#### Deployment and Operation
- [Docker Official Documentation](https://docs.docker.com/)
- [Docker Compose Official Documentation](https://docs.docker.com/compose/)
- [MySQL Official Documentation](https://dev.mysql.com/doc/)
- [Redis Official Documentation](https://redis.io/documentation)

#### Code Quality
- [Black Code Formatting](https://black.readthedocs.io/)
- [Ruff Code Checking](https://docs.astral.sh/ruff/)
- [mypy Type Checking](https://mypy-lang.org/)

## Contact Information

| Project | Information |
|---------|-------------|
| **Author** | John Young (夜雨诗来) |
| **Email** | john.young@foxmail.com |
| **Gitee** | https://gitee.com/yeyushilai |
| **GitHub** | https://github.com/yeyushilai |
| **Project URL** | https://github.com/chain-engine/x-JingWei |