import json
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from models import Sprint, Member, Task, DailyLog, Retro, RetroRating, AgentMessage, Config


def export_all(db: Session) -> Dict[str, Any]:
    def serialize(obj):
        from datetime import datetime, date
        result: Dict[str, Any] = {}
        for col in obj.__table__.columns:
            val = getattr(obj, col.name)
            if isinstance(val, datetime):
                result[col.name] = val.isoformat()
            elif isinstance(val, date):
                result[col.name] = val.isoformat()
            else:
                result[col.name] = val
        return result

    return {
        "sprints": [serialize(s) for s in db.query(Sprint).all()],
        "members": [serialize(m) for m in db.query(Member).all()],
        "tasks": [serialize(t) for t in db.query(Task).all()],
        "daily_logs": [serialize(d) for d in db.query(DailyLog).all()],
        "retros": [serialize(r) for r in db.query(Retro).all()],
        "retro_ratings": [serialize(r) for r in db.query(RetroRating).all()],
        "agent_messages": [serialize(a) for a in db.query(AgentMessage).all()],
        "config": [serialize(c) for c in db.query(Config).all()],
    }
