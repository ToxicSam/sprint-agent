"""Async Sprint router."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import crud
import schemas
from database import get_db

router = APIRouter(prefix="/api/sprint", tags=["sprint"])


@router.get("", response_model=Optional[schemas.SprintResponse])
async def get_active_sprint(db: AsyncSession = Depends(get_db)) -> Optional[schemas.SprintResponse]:
    sprint = await crud.get_active_sprint(db)
    return sprint


@router.post("", response_model=schemas.SprintResponse)
async def create_sprint(
    sprint: schemas.SprintCreate, db: AsyncSession = Depends(get_db)
) -> schemas.SprintResponse:
    return await crud.create_sprint(db, sprint)


@router.put("/{sprint_id}", response_model=schemas.SprintResponse)
async def update_sprint(
    sprint_id: str, sprint: schemas.SprintUpdate, db: AsyncSession = Depends(get_db)
) -> schemas.SprintResponse:
    updated = await crud.update_sprint(db, sprint_id, sprint)
    if not updated:
        raise HTTPException(status_code=404, detail="Sprint not found")
    return updated


@router.delete("/{sprint_id}")
async def delete_sprint(sprint_id: str, db: AsyncSession = Depends(get_db)) -> dict:
    deleted = await crud.delete_sprint(db, sprint_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Sprint not found")
    return {"deleted": True}


@router.get("/{sprint_id}/stats", response_model=schemas.SprintStats)
async def sprint_stats(
    sprint_id: str, db: AsyncSession = Depends(get_db)
) -> schemas.SprintStats:
    stats = await crud.get_sprint_stats(db, sprint_id)
    return schemas.SprintStats(**stats)
