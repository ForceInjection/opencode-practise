"""Pydantic Schema 定义（请求/响应验证）"""

from typing import Optional
from pydantic import BaseModel, Field

from .models import TaskStatus


# 请求 Schema
class CreateTaskSchema(BaseModel):
    """创建任务请求"""
    title: str = Field(..., min_length=1, description="标题不能为空")
    description: str = Field(default="", description="任务描述")
    priority: int = Field(default=0, ge=0, le=5, description="优先级 0-5")


class UpdateTaskSchema(BaseModel):
    """更新任务请求"""
    title: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[int] = Field(None, ge=0, le=5)


# 响应 Schema
class TaskResponse(BaseModel):
    """任务响应"""
    id: int
    title: str
    description: str
    status: str
    priority: int
    created_at: int
    updated_at: int


class DataResponse(BaseModel):
    """统一数据响应"""
    data: TaskResponse | list[TaskResponse] | dict


class ErrorResponse(BaseModel):
    """统一错误响应"""
    error: str
