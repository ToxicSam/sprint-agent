"""Async Retro router."""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import crud
import schemas
from database import get_db

router = APIRouter(prefix="/api/retro", tags=["retro"])


@router.get("/{sprint_id}", response_model=List[schemas.RetroResponse])
async def get_retro_items(
    sprint_id: str, db: AsyncSession = Depends(get_db)
) -> List[schemas.RetroResponse]:
    return await crud.get_retros_by_sprint(db, sprint_id)


@router.post("", response_model=schemas.RetroResponse)
async def add_retro_item(
    retro: schemas.RetroCreate, db: AsyncSession = Depends(get_db)
) -> schemas.RetroResponse:
    return await crud.create_retro(db, retro)


@router.post("/vote", response_model=schemas.RetroResponse)
async def vote_retro(
    data: schemas.RetroVote, db: AsyncSession = Depends(get_db)
) -> schemas.RetroResponse:
    item = await crud.vote_retro(db, data.retro_id)
    if not item:
        raise HTTPException(status_code=404, detail="Retro item not found")
    return item


@router.post("/rate", response_model=schemas.RetroRatingResponse)
async def rate_retro(
    rating: schemas.RetroRatingCreate, db: AsyncSession = Depends(get_db)
) -> schemas.RetroRatingResponse:
    return await crud.create_retro_rating(db, rating)


@router.get("/{sprint_id}/report", response_model=schemas.RetroReport)
async def retro_report(
    sprint_id: str, db: AsyncSession = Depends(get_db)
) -> schemas.RetroReport:
    items = await crud.get_retros_by_sprint(db, sprint_id)
    ratings = await crud.get_retro_ratings(db, sprint_id)

    liked = [i for i in items if i.category == "liked"]
    disliked = [i for i in items if i.category == "disliked"]
    action_items = [i for i in items if i.category == "action"]

    dim_scores: Dict[str, list] = {}
    for r in ratings:
        dim_scores.setdefault(r.dimension, []).append(r.score)
    avg_ratings = {dim: round(sum(scores) / len(scores), 2) for dim, scores in dim_scores.items()}

    summary = (
        f"Retro report: {len(liked)} liked, {len(disliked)} disliked, "
        f"{len(action_items)} action items."
    )

    return schemas.RetroReport(
        liked=liked,
        disliked=disliked,
        action_items=action_items,
        ratings=avg_ratings,
        summary=summary,
    )
