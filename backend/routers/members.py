from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import crud
import schemas
from database import get_db

router = APIRouter(prefix="/api/members", tags=["members"])


@router.get("", response_model=List[schemas.MemberResponse])
def list_members(db: Session = Depends(get_db)):
    return crud.get_members(db)


@router.post("", response_model=schemas.MemberResponse)
def create_member(member: schemas.MemberCreate, db: Session = Depends(get_db)):
    return crud.create_member(db, member)


@router.put("/{member_id}", response_model=schemas.MemberResponse)
def update_member(member_id: str, member: schemas.MemberUpdate, db: Session = Depends(get_db)):
    updated = crud.update_member(db, member_id, member)
    if not updated:
        raise HTTPException(status_code=404, detail="Member not found")
    return updated


@router.delete("/{member_id}")
def delete_member(member_id: str, db: Session = Depends(get_db)):
    deleted = crud.delete_member(db, member_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Member not found")
    return {"deleted": True}
