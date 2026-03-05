"""数据库模型定义 (SQLAlchemy ORM)"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Integer, String, Text, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class TaskStatus(str, Enum):
    """任务状态枚举"""
    todo = "todo"
    doing = "doing"
    done = "done"


class Base(DeclarativeBase):
    """SQLAlchemy 基类"""
    pass


class Task(Base):
    """任务表模型"""
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default=TaskStatus.todo.value)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "created_at": int(self.created_at.timestamp() * 1000),
            "updated_at": int(self.updated_at.timestamp() * 1000),
        }
