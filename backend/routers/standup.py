from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date, timedelta

import crud
import schemas
from database import get_db

router = APIRouter(prefix="/api/standup", tags=["standup"])


@router.get("", response_model=List[schemas.DailyLogResponse])
def get_standup(
    sprint_id: Optional[str] = None,
    date: Optional[date] = None,
    member_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return crud.get_daily_logs(db, sprint_id=sprint_id, date=date, member_id=member_id)


@router.post("", response_model=schemas.DailyLogResponse)
def create_or_update_standup(log: schemas.DailyLogCreate, db: Session = Depends(get_db)):
    return crud.upsert_daily_log(db, log)


@router.post("/batch", response_model=schemas.DailyLogBatchResult)
def batch_standup(batch: schemas.DailyLogBatch, db: Session = Depends(get_db)):
    return crud.batch_upsert_daily_logs(db, batch)


@router.get("/yesterday", response_model=List[schemas.DailyLogResponse])
def get_yesterday_logs(
    sprint_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    yesterday = date.today() - timedelta(days=1)
    return crud.get_daily_logs(db, sprint_id=sprint_id, date=yesterday)
