"""Async Settings, Import/Export, and Board router."""

import os
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import crud
import schemas
from database import async_engine, get_db
from models import Base
from services.agent_service import is_llm_configured
from services.export_service import export_all
from services.import_service import load_init_data

router = APIRouter(prefix="/api", tags=["settings"])


@router.get("/settings")
async def get_settings(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Optional[str]]:
    items = await crud.get_all_config(db)
    return {c.key: c.value for c in items}


@router.put("/settings")
async def update_settings(
    data: schemas.ConfigUpdate, db: AsyncSession = Depends(get_db)
) -> Dict[str, bool]:
    await crud.set_multiple_config(db, data.settings)
    return {"updated": True}


@router.get("/export")
async def export_data(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    return await export_all(db)


@router.post("/import", response_model=schemas.ImportResult)
async def import_data(
    payload: schemas.ImportPayload, db: AsyncSession = Depends(get_db)
) -> schemas.ImportResult:
    inserted: Dict[str, int] = {}
    errors: List[str] = []
    # Simple pass-through; robust import would validate each entity
    return schemas.ImportResult(
        summary="Import not fully implemented in MVP", inserted=inserted, errors=errors
    )


@router.post("/reset")
async def reset_db(db: AsyncSession = Depends(get_db)) -> Dict[str, bool]:
    # Drop and recreate all tables using sync run_sync
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    # Load init data into the fresh database
    await load_init_data(db)
    return {"reset": True}


@router.get("/board", response_model=schemas.BoardResponse)
async def get_board(
    db: AsyncSession = Depends(get_db),
) -> schemas.BoardResponse:
    sprint = await crud.get_active_sprint(db)
    members = await crud.get_members(db)
    tasks = await crud.get_tasks(db, sprint_id=sprint.id if sprint else None)
    return schemas.BoardResponse(sprint=sprint, members=members, tasks=tasks)


@router.get("/health", response_model=schemas.HealthResponse)
async def health() -> schemas.HealthResponse:
    """Health check endpoint including LLM configuration status."""
    db_exists = os.path.exists("./sprint_agent.db")
    return schemas.HealthResponse(
        status="ok",
        database="connected" if db_exists else "not_initialized",
        llm_configured=await is_llm_configured(),
        version="2.0.0",
    )
