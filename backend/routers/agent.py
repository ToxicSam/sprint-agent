"""Async Agent router with LLM-powered intent classification."""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import crud
import schemas
from database import get_db
from services.agent_service import classify_intent, handle_intent, build_context

router = APIRouter(prefix="/api/agent", tags=["agent"])


def _wrap_result(result: dict) -> schemas.AgentActionResult:
    """Wrap raw handle_intent result into AgentActionResult."""
    payload: Dict[str, Any] = {
        "success": result.get("success", False),
        "message": result.get("message", ""),
        "data": {},
    }
    extra = {k: v for k, v in result.items() if k not in ("success", "message")}
    if extra:
        payload["data"] = extra
    return schemas.AgentActionResult(**payload)


@router.post("/message", response_model=schemas.AgentActionResult)
async def agent_message(
    msg: schemas.AgentMessageCreate,
    db: AsyncSession = Depends(get_db),
) -> schemas.AgentActionResult:
    # Store user message
    await crud.create_agent_message(db, msg)

    # Build context for LLM
    context = await build_context(db)

    # Classify intent (LLM with regex fallback)
    intent, entities, llm_response = await classify_intent(msg.content, context)

    # Handle the intent
    result = await handle_intent(db, intent, entities, msg.content, llm_response)

    # Store agent response
    await crud.create_agent_message(
        db,
        schemas.AgentMessageCreate(role="agent", content=result["message"]),
    )

    return _wrap_result(result)


@router.get("/history", response_model=List[schemas.AgentMessageResponse])
async def agent_history(
    db: AsyncSession = Depends(get_db),
) -> List[schemas.AgentMessageResponse]:
    return await crud.get_agent_messages(db, limit=50)


@router.post("/action", response_model=schemas.AgentActionResult)
async def agent_action(
    action: schemas.AgentAction,
    db: AsyncSession = Depends(get_db),
) -> schemas.AgentActionResult:
    result = await handle_intent(db, action.action, action.payload, "")
    return _wrap_result(result)


@router.get("/context")
async def agent_context(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    return await build_context(db)
