from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

import crud
import schemas
from database import get_db
from services.agent_service import classify_intent, handle_intent, build_context

router = APIRouter(prefix="/api/agent", tags=["agent"])


def _wrap_result(result: dict) -> schemas.AgentActionResult:
    """Wrap raw handle_intent result into AgentActionResult."""
    payload = {
        "success": result.get("success", False),
        "message": result.get("message", ""),
        "data": {},
    }
    extra = {k: v for k, v in result.items() if k not in ("success", "message")}
    if extra:
        payload["data"] = extra
    return schemas.AgentActionResult(**payload)


@router.post("/message", response_model=schemas.AgentActionResult)
def agent_message(
    msg: schemas.AgentMessageCreate,
    db: Session = Depends(get_db),
):
    # Store user message
    crud.create_agent_message(db, msg)

    intent, entities = classify_intent(msg.content)
    result = handle_intent(db, intent, entities, msg.content)

    # Store agent response
    crud.create_agent_message(
        db,
        schemas.AgentMessageCreate(role="agent", content=result["message"]),
    )

    return _wrap_result(result)


@router.get("/history", response_model=List[schemas.AgentMessageResponse])
def agent_history(db: Session = Depends(get_db)):
    return crud.get_agent_messages(db, limit=50)


@router.post("/action", response_model=schemas.AgentActionResult)
def agent_action(
    action: schemas.AgentAction,
    db: Session = Depends(get_db),
):
    result = handle_intent(db, action.action, action.payload, "")
    return _wrap_result(result)


@router.get("/context", response_model=Dict[str, Any])
def agent_context(db: Session = Depends(get_db)):
    return build_context(db)
