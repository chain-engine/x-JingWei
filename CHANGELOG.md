# 变更日志

所有版本变更记录。

## [0.1.0] - 2026-09-20

### 新增
- 项目初始化，基于 FastAPI + React 的可视化工作流编排平台
- 后端五层架构：API、Service、Repository、Model、Infrastructure
- DAG 工作流引擎：拓扑排序、并行执行、循环依赖检测
- 10+ 种节点类型：LLM、代码、条件、HTTP、文档处理等
- 前端 React Flow 画布编辑器，支持拖拽创建节点
- MySQL 数据库支持，SQLAlchemy ORM
- 完整的 RESTful API 接口
- 双语文档支持（中文/英文）

### 技术栈
- 后端：FastAPI、Pydantic v2、SQLAlchemy、aiomysql、UV
- 前端：React 18、TypeScript、React Flow 11、Ant Design 5、Zustand
- 部署：Docker、docker-compose

---

## 版本说明

本项目遵循 [语义化版本控制](https://semver.org/lang/zh-CN/)。