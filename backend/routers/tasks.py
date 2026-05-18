from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

import crud
import schemas
from database import get_db

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=List[schemas.TaskResponse])
def list_tasks(
    sprint_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    assignee_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return crud.get_tasks(db, sprint_id=sprint_id, status=status, assignee_id=assignee_id)


@router.post("", response_model=schemas.TaskResponse)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db, task)


@router.put("/{task_id}", response_model=schemas.TaskResponse)
def update_task(task_id: str, task: schemas.TaskUpdate, db: Session = Depends(get_db)):
    updated = crud.update_task(db, task_id, task)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated


@router.delete("/{task_id}")
def delete_task(task_id: str, db: Session = Depends(get_db)):
    deleted = crud.delete_task(db, task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"deleted": True}


@router.post("/{task_id}/move", response_model=schemas.TaskResponse)
def move_task(task_id: str, move: schemas.TaskMove, db: Session = Depends(get_db)):
    moved = crud.move_task(db, task_id, move.status)
    if not moved:
        raise HTTPException(status_code=404, detail="Task not found")
    return moved


@router.post("/bulk", response_model=schemas.BulkTaskResult)
def bulk_update_tasks(data: schemas.BulkTaskUpdate, db: Session = Depends(get_db)):
    return crud.bulk_update_tasks(db, data)


@router.get("/{task_id}/blockers")
def get_blockers(task_id: str, db: Session = Depends(get_db)):
    return crud.get_task_blockers(db, task_id)
