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
- **Linting/Formatting**: Ruff
- **Testing**: pytest + httpx

## Build/Lint/Test Commands

### Installation & Setup

```bash
# Install dependencies (development mode)
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

### Linting & Formatting

```bash
# Run Ruff linter to check for errors
ruff check .

# Run Ruff linter with auto-fix
ruff check --fix .

# Run Ruff formatter
ruff format .

# Check import order and style (I category)
ruff check --select I .
```

### Type Checking

```bash
# Run mypy (if configured) – currently not set up
# mypy src/
```

### Testing

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run a specific test file (when tests exist)
pytest tests/test_routes.py

# Run a single test by name
pytest -k "test_create_task"

# Run tests with coverage
pytest --cov=src

# Run tests in watch mode (requires pytest-watch)
ptw .
```

### Development Server

```bash
# Start development server with hot reload
uvicorn src.main:app --reload --port 3000

# Alternative: run via Python module
python -m src.main
```

### Database Operations

```bash
# Initialize/Recreate database tables
python -c "from src.database import init_db; init_db()"

# Delete database file (SQLite)
rm tasks.db
```

## Code Style Guidelines

### Naming Conventions

- **Variables & Functions**: `snake_case` (e.g., `get_db`, `task_id`, `row`)
- **Classes**: `PascalCase` (e.g., `Task`, `CreateTaskSchema`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DATABASE_URL`)
- **Private Members**: Prefix with underscore `_private_method`
- **Module Names**: `snake_case` (e.g., `database.py`, `models.py`)

### Imports

- **Standard Library imports** first
- **Third-party imports** second
- **Local application imports** last
- Separate groups with a blank line
- Use absolute imports for local modules
- Avoid wildcard imports (`from module import *`)
- Example:

```python
from collections.abc import Generator
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .models import Base
```

### Formatting

- **Line Length**: 100 characters (configured in Ruff)
- **Indentation**: 4 spaces per level (no tabs)
- **Quotes**: Use double quotes (`"`) for strings, single quotes (`'`) for characters within strings
- **Trailing Commas**: Include in multi-line collections
- **Blank Lines**:
  - Two blank lines before class/function definitions
  - One blank line between methods
  - Use blank lines to separate logical sections within functions

### Type Annotations

- Use type hints for all function parameters and return values
- Use `typing` module for complex types (e.g., `Optional`, `Union`, `List`, `Dict`)
- Leverage Python 3.11+ syntax (e.g., `str | None` instead of `Optional[str]`)
- Annotate instance variables in `__init__` method or class body
- Example:

```python
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Error Handling

- Use specific exception types rather than bare `except:` clauses
- Raise `HTTPException` with appropriate status codes in route handlers
- Return descriptive error messages in JSON format: `{"error": "description"}`
- Use early returns to reduce nesting depth
- Validate input with Pydantic schemas before processing
- Example:

```python
task = db.query(Task).filter(Task.id == task_id).first()
if not task:
    raise HTTPException(status_code=404, detail="任务不存在")
```

### Database Conventions

- Model fields use `snake_case` (e.g., `created_at`, `updated_at`)
- Use SQLAlchemy 2.0's `Mapped` type annotations
- Define `__tablename__` explicitly (plural nouns)
- Provide `to_dict()` method for serialization
- Timestamp fields: `created_at` (default=`datetime.now`), `updated_at` (default=`datetime.now`, `onupdate=datetime.now`)
- Use `Base.metadata.create_all()` for table creation

### API Design

- **RESTful conventions**: Use plural resource names (`/api/tasks`)
- **HTTP Methods**: GET (retrieve), POST (create), PATCH (partial update), DELETE (remove)
- **Status Codes**:
  - 200 OK (successful GET/PATCH/DELETE)
  - 201 Created (successful POST)
  - 400 Bad Request (validation error)
  - 404 Not Found (resource doesn't exist)
- **Response Format**: Uniform JSON envelope:
  - Success: `{"data": ...}`
  - Error: `{"error": "description"}`
- **Request Validation**: Use Pydantic schemas for all request bodies
- **Documentation**: Include docstrings with OpenAPI descriptions

### Documentation

- Use docstrings for all public modules, classes, and functions
- Follow Google-style docstring format (brief description, Args, Returns, Raises)
- Include type information in docstrings (redundant with type hints)
- Keep comments minimal; prefer self-documenting code
- Update README.md when adding significant features

## Development Workflow

1. **Setup**: `pip install -e ".[dev]"`
2. **Database**: Ensure SQLite database exists (automatically created on first run)
3. **Development**: Run `uvicorn src.main:app --reload --port 3000`
4. **Testing**: Write tests in `tests/` directory, run `pytest`
5. **Linting**: Run `ruff check .` and `ruff format .` before committing
6. **Commit**: Follow conventional commit messages:

   ```bash
   # Format: <type>: <description>
   git commit -m "feat: add user authentication"
   git commit -m "fix: resolve task creation validation"
   git commit -m "docs: update API documentation"
   git commit -m "test: add unit tests for task routes"
   git commit -m "refactor: simplify database connection logic"
   git commit -m "style: fix formatting in routes.py"
   ```

   - **Types**: `feat`, `fix`, `docs`, `test`, `refactor`, `style`, `perf`, `build`, `ci`, `chore`
   - **Description**: Use imperative mood, keep under 72 characters

## Testing Guidelines

### Test Structure

- Create test files in `tests/` directory with `test_` prefix (e.g., `test_routes.py`)
- Use `pytest` fixtures for database setup/teardown
- Test naming: `test_<function_name>_<scenario>` (e.g., `test_create_task_success`, `test_create_task_validation_error`)

### Test Examples

```python
# Good: Specific assertions with descriptive messages
def test_create_task_success(client):
    response = client.post("/api/tasks", json={"title": "Test task"})
    assert response.status_code == 201
    assert response.json()["data"]["title"] == "Test task"

# Good: Using fixtures for database isolation
def test_get_task_not_found(client, db_session):
    response = client.get("/api/tasks/999")
    assert response.status_code == 404
    assert "任务不存在" in response.json()["error"]
```

### Anti-Patterns to Avoid

```python
# Bad: Vague test name
def test_create():
    # ...

# Bad: Multiple assertions without clear purpose
def test_create_task_all_cases():
    # Too broad - split into individual tests

# Bad: Not cleaning up test data
def test_create_task():
    # Leaves data in database - use transaction rollback
```

### Mocking Guidelines

- Prefer real database operations over mocks when testing API endpoints
- Use mocks only for external services (email, third-party APIs)
- Keep mock setup minimal and close to the test that uses it

## Environment Setup

### Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate on macOS/Linux
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

### Python Version Management

- Use Python 3.11+ (as specified in `pyproject.toml`)
- Consider using `pyenv` for multiple Python versions:

  ```bash
  pyenv install 3.11.0
  pyenv local 3.11.0
  ```

## Cursor & Copilot Rules

No project-specific Cursor rules (`.cursorrules` or `.cursor/rules/`) or Copilot instructions (`.github/copilot-instructions.md`) are currently defined. Agents should follow the coding conventions outlined in this document.

## API Endpoints

| Method | Endpoint          | Description       | Request Body                                                                                 | Response                              |
| ------ | ----------------- | ----------------- | -------------------------------------------------------------------------------------------- | ------------------------------------- |
| GET    | `/api/tasks`      | List all tasks    | None                                                                                         | `{"data": [task1, task2, ...]}`       |
| GET    | `/api/tasks/{id}` | Get specific task | None                                                                                         | `{"data": task}`                      |
| POST   | `/api/tasks`      | Create new task   | `{"title": "string", "description": "string", "priority": 0-5}`                              | `{"data": task}` (201)                |
| PATCH  | `/api/tasks/{id}` | Update task       | `{"title": "string", "description": "string", "status": "todo/doing/done", "priority": 0-5}` | `{"data": task}`                      |
| DELETE | `/api/tasks/{id}` | Delete task       | None                                                                                         | `{"data": {"message": "任务已删除"}}` |

**Request Body Examples:**

```json
// POST /api/tasks
{
  "title": "Complete project",
  "description": "Finish the task manager API",
  "priority": 3
}

// PATCH /api/tasks/1
{
  "status": "doing",
  "priority": 4
}
```

**TaskStatus Enum Definition:**

```python
class TaskStatus(str, Enum):
    """任务状态枚举"""
    todo = "todo"
    doing = "doing"
    done = "done"
```

## Additional Notes

- The project uses SQLite for simplicity; production would use PostgreSQL/MySQL
- All API endpoints are under `/api` prefix
- Timestamps are returned as milliseconds since Unix epoch
- The `priority` field range is 0-5 (inclusive)

## Dependencies

Main dependencies from `pyproject.toml`:

```toml
# Core dependencies
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
sqlalchemy>=2.0.0
pydantic>=2.0.0

# Development dependencies
pytest>=8.0.0
httpx>=0.27.0
```

## Common Pitfalls

### Error Handling Examples

```python
# Good: Specific exception handling
try:
    task = db.query(Task).filter(Task.id == task_id).one()
except NoResultFound:
    raise HTTPException(status_code=404, detail="任务不存在")

# Bad: Bare except clause
try:
    task = db.query(Task).filter(Task.id == task_id).first()
except:  # Don't do this
    return {"error": "Unknown error"}

# Good: Early return for validation
if not title or len(title.strip()) == 0:
    raise HTTPException(status_code=400, detail="标题不能为空")

# Bad: Deep nesting
if task:
    if task.status == "done":
        if task.priority > 3:
            # ... deep nesting
```

### Type Annotation Examples

```python
# Good: Clear type hints
def get_task(task_id: int, db: Session) -> dict:
    # ...

# Bad: Missing type hints
def get_task(task_id, db):
    # ...

# Good: Modern Python 3.11+ syntax
def process_item(item: dict[str, Any] | None) -> str | None:
    # ...

# Bad: Legacy typing syntax
def process_item(item: Optional[Dict[str, Any]]) -> Optional[str]:
    # ...
```

## Quick Reference

```bash
# Most commonly used commands
pip install -e ".[dev]"           # Install all dependencies
uvicorn src.main:app --reload     # Start dev server
ruff check .                      # Lint code
ruff format .                     # Format code
pytest                            # Run tests
```
