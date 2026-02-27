from datetime import datetime

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, page: int, limit: int):
        offset = (page - 1) * limit
        stmt = select(Task).where(Task.deleted_at == None)

        total = self.db.scalar(select(func.count()).select_from(stmt.subquery()))
        items = self.db.scalars(stmt.offset(offset).limit(limit)).all()

        return items, total

    def get_one(self, task_id: int):
        return self.db.scalar(
            select(Task).where(Task.id == task_id, Task.deleted_at == None)
        )

    def create(self, data: TaskCreate):
        task = Task(**data.model_dump())
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def update(self, task_id: int, data: TaskUpdate, partial: bool = False):
        task = self.get_one(task_id)
        if not task:
            return None

        update_data = data.model_dump(exclude_unset=partial)
        for key, value in update_data.items():
            setattr(task, key, value)

        self.db.commit()
        return task

    def soft_delete(self, task_id: int):
        task = self.get_one(task_id)
        if task:
            task.deleted_at = datetime.now()
            self.db.commit()
        return task
