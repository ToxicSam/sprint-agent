"""Async Standup (Daily Log) router."""

from datetime import date, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import crud
import schemas
from database import get_db

router = APIRouter(prefix="/api/standup", tags=["standup"])


@router.get("", response_model=List[schemas.DailyLogResponse])
async def get_standup(
    sprint_id: Optional[str] = None,
    date: Optional[date] = None,
    member_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> List[schemas.DailyLogResponse]:
    return await crud.get_daily_logs(db, sprint_id=sprint_id, date=date, member_id=member_id)


@router.post("", response_model=schemas.DailyLogResponse)
async def create_or_update_standup(
    log: schemas.DailyLogCreate, db: AsyncSession = Depends(get_db)
) -> schemas.DailyLogResponse:
    return await crud.upsert_daily_log(db, log)


@router.post("/batch", response_model=schemas.DailyLogBatchResult)
async def batch_standup(
    batch: schemas.DailyLogBatch, db: AsyncSession = Depends(get_db)
) -> schemas.DailyLogBatchResult:
    return await crud.batch_upsert_daily_logs(db, batch)


@router.get("/yesterday", response_model=List[schemas.DailyLogResponse])
async def get_yesterday_logs(
    sprint_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> List[schemas.DailyLogResponse]:
    yesterday = date.today() - timedelta(days=1)
    return await crud.get_daily_logs(db, sprint_id=sprint_id, date=yesterday)
