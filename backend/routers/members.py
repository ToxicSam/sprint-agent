"""Async Members router."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import crud
import schemas
from database import get_db

router = APIRouter(prefix="/api/members", tags=["members"])


@router.get("", response_model=List[schemas.MemberResponse])
async def list_members(db: AsyncSession = Depends(get_db)) -> List[schemas.MemberResponse]:
    return await crud.get_members(db)


@router.post("", response_model=schemas.MemberResponse)
async def create_member(
    member: schemas.MemberCreate, db: AsyncSession = Depends(get_db)
) -> schemas.MemberResponse:
    return await crud.create_member(db, member)


@router.put("/{member_id}", response_model=schemas.MemberResponse)
async def update_member(
    member_id: str, member: schemas.MemberUpdate, db: AsyncSession = Depends(get_db)
) -> schemas.MemberResponse:
    updated = await crud.update_member(db, member_id, member)
    if not updated:
        raise HTTPException(status_code=404, detail="Member not found")
    return updated


@router.delete("/{member_id}")
async def delete_member(member_id: str, db: AsyncSession = Depends(get_db)) -> dict:
    deleted = await crud.delete_member(db, member_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Member not found")
    return {"deleted": True}
