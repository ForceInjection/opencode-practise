# Task Manager API — Agent 指导文件

## 项目概览

这是一个使用 Python + FastAPI + SQLAlchemy + SQLite 构建的任务管理 REST API。
该项目作为 OpenCode 的实战学习案例，演示如何在真实项目中使用 OpenCode 进行 AI 辅助开发。

## 架构

```text
src/
├── main.py      — 服务器入口，启动 FastAPI HTTP 服务
├── database.py  — SQLite 数据库初始化（SQLAlchemy）
├── models.py    — 数据库模型定义（tasks 表）
├── schemas.py   — Pydantic Schema 定义（请求/响应验证）
└── routes.py    — RESTful 路由处理（CRUD）
```

## 技术选型

- **Runtime**: Python 3.11+
- **HTTP Framework**: FastAPI
- **ORM**: SQLAlchemy 2.0
- **Database**: SQLite
- **Validation**: Pydantic
- **Language**: Python (type hints)

## 编码规范

### 命名

- 变量和函数名使用 `snake_case`（如 `get_db`, `task_id`, `row`）
- 类名使用 `PascalCase`（如 `Task`, `CreateTaskSchema`）

### 风格

- 使用类型注解（Type Hints）
- 使用 Early Return，避免深层嵌套
- 避免过度使用 try/except，除非必须处理特定异常
- 优先使用列表推导式和生成器表达式
- 使用 f-string 进行字符串格式化

### 数据库

- 模型字段使用 `snake_case`（如 `created_at`）
- 使用 SQLAlchemy 2.0 的 `Mapped` 类型注解
- 通过 `Base.metadata.create_all()` 自动创建表

### API 设计

- RESTful 风格，路径使用小写复数名词（如 `/api/tasks`）
- 响应使用统一的 JSON 格式：`{ "data": ... }` 或 `{ "error": "..." }`
- 使用 Pydantic 进行请求体校验
- HTTP 状态码：200（成功）、201（创建）、400（参数错误）、404（未找到）

## 运行命令

```bash
# 安装依赖
pip install -e .

# 开发模式运行
uvicorn src.main:app --reload --port 3000

# 或使用 python 直接运行
python -m src.main
```

## 测试

- 直接测试实际实现，不使用 mock
- 使用 pytest 和 httpx 进行 API 测试
