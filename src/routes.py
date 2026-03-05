"""RESTful API 路由"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .database import get_db
from .models import Task
from .schemas import CreateTaskSchema, UpdateTaskSchema

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("")
def list_tasks(db: Session = Depends(get_db)):
    """获取所有任务"""
    rows = db.query(Task).all()
    return {"data": [row.to_dict() for row in rows]}


@router.get("/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    """获取单个任务"""
    row = db.query(Task).filter(Task.id == task_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="任务不存在")
    return {"data": row.to_dict()}


@router.post("", status_code=201)
def create_task(body: CreateTaskSchema, db: Session = Depends(get_db)):
    """创建任务"""
    now = datetime.now()
    task = Task(
        title=body.title,
        description=body.description,
        priority=body.priority,
        created_at=now,
        updated_at=now,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return {"data": task.to_dict()}


@router.patch("/{task_id}")
def update_task(task_id: int, body: UpdateTaskSchema, db: Session = Depends(get_db)):
    """更新任务"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    update_data = body.model_dump(exclude_unset=True)
    if update_data:
        update_data["updated_at"] = datetime.now()
        for key, val in update_data.items():
            # 处理枚举类型
            if key == "status" and val:
                val = val.value
            setattr(task, key, val)
        db.commit()
        db.refresh(task)

    return {"data": task.to_dict()}


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """删除任务"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    db.delete(task)
    db.commit()
    return {"data": {"message": "任务已删除"}}
