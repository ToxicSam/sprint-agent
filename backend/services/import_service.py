import json
import os
from typing import Dict, Any, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session

import crud
import schemas
from models import Sprint, Member, Task, DailyLog, Retro, RetroRating, AgentMessage, Config


def load_init_data(db: Session, file_path: str = "data/init.json") -> None:
    """Load init.json into the database if the DB is empty."""
    if db.query(Sprint).first():
        return  # Database already has data

    if not os.path.exists(file_path):
        return

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Sprints
    for item in data.get("sprints", []):
        db.add(Sprint(
            id=item.get("id") or _new_id(),
            name=item["name"],
            goal=item.get("goal"),
            start_date=_parse_date(item.get("start_date")),
            end_date=_parse_date(item.get("end_date")),
            status=item.get("status", "active"),
            created_at=_parse_datetime(item.get("created_at")),
        ))
    db.commit()

    # Members
    for item in data.get("members", []):
        db.add(Member(
            id=item.get("id") or _new_id(),
            name=item["name"],
            role=item["role"],
            capacity=item.get("capacity"),
            avatar=item.get("avatar"),
            created_at=_parse_datetime(item.get("created_at")),
        ))
    db.commit()

    # Tasks
    for item in data.get("tasks", []):
        db.add(Task(
            id=item.get("id") or _new_id(),
            sprint_id=item["sprint_id"],
            title=item["title"],
            assignee_id=item.get("assignee_id"),
            status=item.get("status", "todo"),
            priority=item.get("priority"),
            story_points=item.get("story_points"),
            blocked_by=json.dumps(item["blocked_by"]) if isinstance(item.get("blocked_by"), list) else item.get("blocked_by"),
            description=item.get("description"),
            created_at=_parse_datetime(item.get("created_at")),
            updated_at=_parse_datetime(item.get("updated_at")),
        ))
    db.commit()

    # Daily logs
    for item in data.get("daily_logs", []):
        db.add(DailyLog(
            id=item.get("id") or _new_id(),
            sprint_id=item["sprint_id"],
            member_id=item["member_id"],
            date=_parse_date(item["date"]),
            completed=item.get("completed"),
            planned=item.get("planned"),
            blockers=item.get("blockers"),
            hours_spent=item.get("hours_spent"),
            created_at=_parse_datetime(item.get("created_at")),
        ))
    db.commit()

    # Retros
    for item in data.get("retros", []):
        db.add(Retro(
            id=item.get("id") or _new_id(),
            sprint_id=item["sprint_id"],
            category=item["category"],
            item=item["item"],
            votes=item.get("votes", 0),
            created_at=_parse_datetime(item.get("created_at")),
        ))
    db.commit()

    # Retro ratings
    for item in data.get("retro_ratings", []):
        db.add(RetroRating(
            id=item.get("id") or _new_id(),
            sprint_id=item["sprint_id"],
            dimension=item["dimension"],
            score=item["score"],
            created_at=_parse_datetime(item.get("created_at")),
        ))
    db.commit()

    # Agent messages
    for item in data.get("agent_messages", []):
        db.add(AgentMessage(
            id=item.get("id") or _new_id(),
            role=item["role"],
            content=item["content"],
            context=json.dumps(item["context"]) if isinstance(item.get("context"), dict) else item.get("context"),
            created_at=_parse_datetime(item.get("created_at")),
        ))
    db.commit()

    # Config
    for item in data.get("config", []):
        db.add(Config(
            key=item["key"],
            value=item.get("value"),
        ))
    db.commit()


def _new_id() -> str:
    import uuid
    return str(uuid.uuid4())


def _parse_date(val: Optional[str]) -> Optional[date]:
    if not val:
        return None
    if isinstance(val, str):
        return datetime.strptime(val, "%Y-%m-%d").date()
    return val


def _parse_datetime(val: Optional[str]) -> Optional[datetime]:
    if not val:
        return datetime.utcnow()
    if isinstance(val, str):
        return datetime.fromisoformat(val.replace("Z", "+00:00"))
    return val
