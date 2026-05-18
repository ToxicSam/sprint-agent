from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

import crud
import schemas
from database import get_db

router = APIRouter(prefix="/api/sprint", tags=["sprint"])


@router.get("", response_model=Optional[schemas.SprintResponse])
def get_active_sprint(db: Session = Depends(get_db)):
    sprint = crud.get_active_sprint(db)
    if not sprint:
        return None
    return sprint


@router.post("", response_model=schemas.SprintResponse)
def create_sprint(sprint: schemas.SprintCreate, db: Session = Depends(get_db)):
    return crud.create_sprint(db, sprint)


@router.put("/{sprint_id}", response_model=schemas.SprintResponse)
def update_sprint(sprint_id: str, sprint: schemas.SprintUpdate, db: Session = Depends(get_db)):
    updated = crud.update_sprint(db, sprint_id, sprint)
    if not updated:
        raise HTTPException(status_code=404, detail="Sprint not found")
    return updated


@router.delete("/{sprint_id}")
def delete_sprint(sprint_id: str, db: Session = Depends(get_db)):
    deleted = crud.delete_sprint(db, sprint_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Sprint not found")
    return {"deleted": True}


@router.get("/{sprint_id}/stats", response_model=schemas.SprintStats)
def sprint_stats(sprint_id: str, db: Session = Depends(get_db)):
    stats = crud.get_sprint_stats(db, sprint_id)
    return schemas.SprintStats(**stats)
