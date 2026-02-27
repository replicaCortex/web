from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.task import PaginatedTaskResponse, TaskCreate, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=PaginatedTaskResponse)
def list_tasks(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = TaskService(db)
    items, total = service.get_all(page, limit)
    return {
        "data": items,
        "meta": {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit,
        },
    }


@router.get("/{task_id}")
def read_task(task_id: int, db: Session = Depends(get_db)):
    task = TaskService(db).get_one(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    return task


@router.post("", status_code=status.HTTP_201_CREATED)
def create_task(data: TaskCreate, db: Session = Depends(get_db)):
    return TaskService(db).create(data)


@router.put("/{task_id}")
def update_task_full(task_id: int, data: TaskUpdate, db: Session = Depends(get_db)):
    task = TaskService(db).update(task_id, data, partial=False)
    if not task:
        raise HTTPException(404, "Task not found")
    return task


@router.patch("/{task_id}")
def update_task_partial(task_id: int, data: TaskUpdate, db: Session = Depends(get_db)):
    task = TaskService(db).update(task_id, data, partial=True)
    if not task:
        raise HTTPException(404, "Task not found")
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    if not TaskService(db).soft_delete(task_id):
        raise HTTPException(404, "Task not found")
