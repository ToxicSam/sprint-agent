import json
import re
from typing import Dict, Any, List, Tuple, Optional
from sqlalchemy.orm import Session

import crud
import schemas
from models import Sprint, Task, Member, AgentMessage


INTENT_PATTERNS = [
    ("create_task", [
        r"create\s+(?:a\s+)?(?:new\s+)?task",
        r"add\s+(?:a\s+)?(?:new\s+)?task",
        r"make\s+(?:a\s+)?(?:new\s+)?task",
        r"new\s+task",
    ]),
    ("move_task", [
        r"move\s+(?:task\s+)?(\S+)\s+to\s+(\S+)",
        r"move\s+(?:task\s+)?(\S+)\s+(?:into|in)\s+(\S+)",
        r"set\s+(?:task\s+)?(\S+)\s+(?:status\s+)?to\s+(\S+)",
    ]),
    ("update_task", [
        r"update\s+(?:task\s+)?(\S+)",
        r"change\s+(?:task\s+)?(\S+)",
        r"edit\s+(?:task\s+)?(\S+)",
    ]),
    ("standup_log", [
        r"log\s+(?:standup|daily)\s+(?:for\s+)?(\S+)",
        r"submit\s+(?:standup|daily)\s+(?:for\s+)?(\S+)",
        r"add\s+(?:a\s+)?(?:daily\s+)?log",
        r"standup\s+(?:for\s+)?(\S+)",
    ]),
    ("retro_score", [
        r"rate\s+(?:the\s+)?(?:retro|sprint)",
        r"score\s+(?:the\s+)?(?:retro|sprint)",
        r"retro\s+rating",
        r"sprint\s+score",
    ]),
    ("delete_task", [
        r"delete\s+(?:task\s+)?(\S+)",
        r"remove\s+(?:task\s+)?(\S+)",
    ]),
    ("sprint_stats", [
        r"sprint\s+stats",
        r"show\s+(?:me\s+)?(?:the\s+)?stats",
        r"how\s+is\s+the\s+sprint\s+going",
        r"sprint\s+progress",
    ]),
]

STATUS_ALIASES = {
    "todo": ["todo", "backlog", "to do", "to-do", "open", "not started"],
    "progress": ["progress", "in progress", "in-progress", "doing", "wip", "working", "started"],
    "done": ["done", "completed", "complete", "finished", "closed", "resolved"],
    "paused": ["paused", "blocked", "on hold", "hold", "waiting"],
}


def classify_intent(message: str) -> Tuple[str, Dict[str, Any]]:
    text = message.lower().strip()
    for intent, patterns in INTENT_PATTERNS:
        for pat in patterns:
            match = re.search(pat, text)
            if match:
                entities: Dict[str, Any] = {}
                groups = match.groups()
                if intent == "move_task" and len(groups) >= 2:
                    entities["task_ref"] = groups[0]
                    entities["target_status"] = normalize_status(groups[1])
                elif intent in ("update_task", "delete_task", "standup_log") and groups:
                    entities["task_ref"] = groups[0]
                return intent, entities
    return "general_chat", {}


def normalize_status(raw: str) -> str:
    raw_lower = raw.lower().strip()
    for canonical, aliases in STATUS_ALIASES.items():
        if raw_lower in aliases:
            return canonical
    return raw_lower


def resolve_task_ref(db: Session, ref: str) -> Optional[Task]:
    # Try exact id
    task = crud.get_task(db, ref)
    if task:
        return task
    # Try title search
    from sqlalchemy import func
    task = db.query(Task).filter(func.lower(Task.title).like(f"%{ref.lower()}%")).first()
    return task


def resolve_member_ref(db: Session, ref: str) -> Optional[Member]:
    member = crud.get_member(db, ref)
    if member:
        return member
    from sqlalchemy import func
    member = db.query(Member).filter(func.lower(Member.name).like(f"%{ref.lower()}%")).first()
    return member


def handle_intent(
    db: Session,
    intent: str,
    entities: Dict[str, Any],
    message: str,
) -> Dict[str, Any]:
    if intent == "create_task":
        title_match = re.search(r'["\'](.+?)["\']', message)
        title = title_match.group(1) if title_match else "New Task"
        active = crud.get_active_sprint(db)
        sprint_id = active.id if active else ""
        task = crud.create_task(db, schemas.TaskCreate(title=title, sprint_id=sprint_id))
        return {"success": True, "message": f"Created task '{task.title}' ({task.id}).", "task_id": task.id}

    if intent == "move_task":
        ref = entities.get("task_ref", "")
        status = entities.get("target_status", "progress")
        task = resolve_task_ref(db, ref)
        if not task:
            return {"success": False, "message": f"Task '{ref}' not found."}
        moved = crud.move_task(db, task.id, status)
        return {"success": True, "message": f"Moved task '{moved.title}' to {moved.status}.", "task_id": moved.id}

    if intent == "update_task":
        ref = entities.get("task_ref", "")
        task = resolve_task_ref(db, ref)
        if not task:
            return {"success": False, "message": f"Task '{ref}' not found."}
        return {"success": True, "message": f"Task '{task.title}' found. Use the UI to edit details.", "task_id": task.id}

    if intent == "delete_task":
        ref = entities.get("task_ref", "")
        task = resolve_task_ref(db, ref)
        if not task:
            return {"success": False, "message": f"Task '{ref}' not found."}
        crud.delete_task(db, task.id)
        return {"success": True, "message": f"Deleted task '{task.title}'.", "task_id": task.id}

    if intent == "sprint_stats":
        active = crud.get_active_sprint(db)
        if not active:
            return {"success": True, "message": "No active sprint."}
        stats = crud.get_sprint_stats(db, active.id)
        msg = (
            f"Sprint '{active.name}': {stats['done']}/{stats['total_tasks']} tasks done, "
            f"{stats['completed_story_points']}/{stats['total_story_points']} SP."
        )
        return {"success": True, "message": msg, "stats": stats}

    if intent == "standup_log":
        return {"success": True, "message": "Open the standup page to log your daily update."}

    if intent == "retro_score":
        return {"success": True, "message": "Open the retro page to submit sprint ratings."}

    return {"success": True, "message": "I'm here to help. You can ask me to create or move tasks, show sprint stats, or help with standups and retros."}


def build_context(db: Session) -> Dict[str, Any]:
    active = crud.get_active_sprint(db)
    recent_tasks = crud.get_tasks(db, sprint_id=active.id if active else None, limit=10)
    members = crud.get_members(db)
    messages = crud.get_agent_messages(db, limit=10)
    return {
        "current_sprint": {
            "id": active.id,
            "name": active.name,
            "status": active.status,
        } if active else None,
        "recent_tasks": [{"id": t.id, "title": t.title, "status": t.status} for t in recent_tasks],
        "members": [{"id": m.id, "name": m.name, "role": m.role} for m in members],
        "messages": [{"role": m.role, "content": m.content} for m in messages],
    }
