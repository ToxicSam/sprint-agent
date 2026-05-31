"""Async Tasks router."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

import crud
import schemas
from database import get_db

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=List[schemas.TaskResponse])
async def list_tasks(
    sprint_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    assignee_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> List[schemas.TaskResponse]:
    return await crud.get_tasks(db, sprint_id=sprint_id, status=status, assignee_id=assignee_id)


@router.post("", response_model=schemas.TaskResponse)
async def create_task(
    task: schemas.TaskCreate, db: AsyncSession = Depends(get_db)
) -> schemas.TaskResponse:
    return await crud.create_task(db, task)


@router.put("/{task_id}", response_model=schemas.TaskResponse)
async def update_task(
    task_id: str, task: schemas.TaskUpdate, db: AsyncSession = Depends(get_db)
) -> schemas.TaskResponse:
    updated = await crud.update_task(db, task_id, task)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated


@router.delete("/{task_id}")
async def delete_task(task_id: str, db: AsyncSession = Depends(get_db)) -> dict:
    deleted = await crud.delete_task(db, task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"deleted": True}


@router.post("/{task_id}/move", response_model=schemas.TaskResponse)
async def move_task(
    task_id: str, move: schemas.TaskMove, db: AsyncSession = Depends(get_db)
) -> schemas.TaskResponse:
    moved = await crud.move_task(db, task_id, move.status)
    if not moved:
        raise HTTPException(status_code=404, detail="Task not found")
    return moved


@router.post("/bulk", response_model=schemas.BulkTaskResult)
async def bulk_update_tasks(
    data: schemas.BulkTaskUpdate, db: AsyncSession = Depends(get_db)
) -> schemas.BulkTaskResult:
    return await crud.bulk_update_tasks(db, data)


@router.get("/{task_id}/blockers")
async def get_blockers(task_id: str, db: AsyncSession = Depends(get_db)) -> List[dict]:
    return await crud.get_task_blockers(db, task_id)
