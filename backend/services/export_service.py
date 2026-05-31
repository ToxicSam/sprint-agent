"""Async data export service."""

import json as _json
from datetime import date, datetime
from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Sprint, Member, Task, DailyLog, Retro, RetroRating, AgentMessage, Config


def _serialize(obj: Any) -> Dict[str, Any]:
    """Serialize a SQLAlchemy model instance to a dict."""
    result: Dict[str, Any] = {}
    for col in obj.__table__.columns:
        val = getattr(obj, col.name)
        if isinstance(val, datetime):
            result[col.name] = val.isoformat()
        elif isinstance(val, date):
            result[col.name] = val.isoformat()
        elif isinstance(val, list):
            result[col.name] = val
        elif isinstance(val, dict):
            result[col.name] = _json.dumps(val, ensure_ascii=False)
        else:
            result[col.name] = val
    return result


async def export_all(db: AsyncSession) -> Dict[str, Any]:
    """Export all database content as JSON-serializable dict."""
    sprints_result = await db.execute(select(Sprint))
    members_result = await db.execute(select(Member))
    tasks_result = await db.execute(select(Task))
    daily_logs_result = await db.execute(select(DailyLog))
    retros_result = await db.execute(select(Retro))
    retro_ratings_result = await db.execute(select(RetroRating))
    agent_messages_result = await db.execute(select(AgentMessage))
    config_result = await db.execute(select(Config))

    return {
        "sprints": [_serialize(s) for s in sprints_result.scalars().all()],
        "members": [_serialize(m) for m in members_result.scalars().all()],
        "tasks": [_serialize(t) for t in tasks_result.scalars().all()],
        "daily_logs": [_serialize(d) for d in daily_logs_result.scalars().all()],
        "retros": [_serialize(r) for r in retros_result.scalars().all()],
        "retro_ratings": [_serialize(r) for r in retro_ratings_result.scalars().all()],
        "agent_messages": [_serialize(a) for a in agent_messages_result.scalars().all()],
        "config": [_serialize(c) for c in config_result.scalars().all()],
    }
