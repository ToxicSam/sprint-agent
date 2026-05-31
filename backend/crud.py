"""Async CRUD operations for all database entities."""

import json
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import func, and_, select
from sqlalchemy.ext.asyncio import AsyncSession

import models
import schemas


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _parse_blocked_by(value: Optional[str]) -> Optional[List[str]]:
    """Parse a JSON string into a list for native JSON storage."""
    if value is None:
        return None
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, list) else [parsed]
    except (json.JSONDecodeError, TypeError):
        return None


# ---------------------------------------------------------------------------
# Sprint
# ---------------------------------------------------------------------------
async def get_sprint(db: AsyncSession, sprint_id: str) -> Optional[models.Sprint]:
    result = await db.execute(select(models.Sprint).filter(models.Sprint.id == sprint_id))
    return result.scalars().first()


async def get_active_sprint(db: AsyncSession) -> Optional[models.Sprint]:
    result = await db.execute(select(models.Sprint).filter(models.Sprint.status == "active"))
    return result.scalars().first()


async def get_sprints(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.Sprint]:
    result = await db.execute(select(models.Sprint).offset(skip).limit(limit))
    return list(result.scalars().all())


async def create_sprint(db: AsyncSession, sprint: schemas.SprintCreate) -> models.Sprint:
    db_sprint = models.Sprint(**sprint.model_dump())
    db.add(db_sprint)
    await db.commit()
    await db.refresh(db_sprint)
    return db_sprint


async def update_sprint(
    db: AsyncSession, sprint_id: str, sprint: schemas.SprintUpdate
) -> Optional[models.Sprint]:
    db_sprint = await get_sprint(db, sprint_id)
    if not db_sprint:
        return None
    for key, value in sprint.model_dump(exclude_unset=True).items():
        setattr(db_sprint, key, value)
    await db.commit()
    await db.refresh(db_sprint)
    return db_sprint


async def delete_sprint(db: AsyncSession, sprint_id: str) -> bool:
    db_sprint = await get_sprint(db, sprint_id)
    if not db_sprint:
        return False
    await db.delete(db_sprint)
    await db.commit()
    return True


async def get_sprint_stats(db: AsyncSession, sprint_id: str) -> Dict[str, Any]:
    result = await db.execute(select(models.Task).filter(models.Task.sprint_id == sprint_id))
    tasks = list(result.scalars().all())
    total = len(tasks)
    todo = sum(1 for t in tasks if t.status == "todo")
    progress = sum(1 for t in tasks if t.status == "progress")
    done = sum(1 for t in tasks if t.status == "done")
    paused = sum(1 for t in tasks if t.status == "paused")
    total_sp = sum(t.story_points or 0 for t in tasks)
    completed_sp = sum(t.story_points or 0 for t in tasks if t.status == "done")
    remaining = total_sp - completed_sp
    rate = (completed_sp / total_sp * 100) if total_sp else 0.0

    members_active_result = await db.execute(
        select(models.Task.assignee_id)
        .filter(
            models.Task.sprint_id == sprint_id,
            models.Task.assignee_id.isnot(None),
        )
        .distinct()
    )
    members_active = len(members_active_result.scalars().all())

    return {
        "total_tasks": total,
        "todo": todo,
        "progress": progress,
        "done": done,
        "paused": paused,
        "total_story_points": total_sp,
        "completed_story_points": completed_sp,
        "remaining_story_points": remaining,
        "completion_rate": round(rate, 2),
        "members_active": members_active,
    }


# ---------------------------------------------------------------------------
# Member
# ---------------------------------------------------------------------------
async def get_member(db: AsyncSession, member_id: str) -> Optional[models.Member]:
    result = await db.execute(select(models.Member).filter(models.Member.id == member_id))
    return result.scalars().first()


async def get_members(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.Member]:
    result = await db.execute(select(models.Member).offset(skip).limit(limit))
    return list(result.scalars().all())


async def create_member(db: AsyncSession, member: schemas.MemberCreate) -> models.Member:
    db_member = models.Member(**member.model_dump())
    db.add(db_member)
    await db.commit()
    await db.refresh(db_member)
    return db_member


async def update_member(
    db: AsyncSession, member_id: str, member: schemas.MemberUpdate
) -> Optional[models.Member]:
    db_member = await get_member(db, member_id)
    if not db_member:
        return None
    for key, value in member.model_dump(exclude_unset=True).items():
        setattr(db_member, key, value)
    await db.commit()
    await db.refresh(db_member)
    return db_member


async def delete_member(db: AsyncSession, member_id: str) -> bool:
    db_member = await get_member(db, member_id)
    if not db_member:
        return False
    await db.delete(db_member)
    await db.commit()
    return True


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------
async def get_task(db: AsyncSession, task_id: str) -> Optional[models.Task]:
    result = await db.execute(select(models.Task).filter(models.Task.id == task_id))
    return result.scalars().first()


async def get_tasks(
    db: AsyncSession,
    sprint_id: Optional[str] = None,
    status: Optional[str] = None,
    assignee_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 200,
) -> List[models.Task]:
    query = select(models.Task)
    if sprint_id:
        query = query.filter(models.Task.sprint_id == sprint_id)
    if status:
        query = query.filter(models.Task.status == status)
    if assignee_id:
        query = query.filter(models.Task.assignee_id == assignee_id)
    result = await db.execute(query.offset(skip).limit(limit))
    return list(result.scalars().all())


async def create_task(db: AsyncSession, task: schemas.TaskCreate) -> models.Task:
    task_data = task.model_dump()
    task_data["blocked_by"] = _parse_blocked_by(task_data.get("blocked_by"))
    db_task = models.Task(**task_data)
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task


async def update_task(
    db: AsyncSession, task_id: str, task: schemas.TaskUpdate
) -> Optional[models.Task]:
    db_task = await get_task(db, task_id)
    if not db_task:
        return None
    for key, value in task.model_dump(exclude_unset=True).items():
        if key == "blocked_by":
            value = _parse_blocked_by(value)
        setattr(db_task, key, value)
    db_task.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(db_task)
    return db_task


async def delete_task(db: AsyncSession, task_id: str) -> bool:
    db_task = await get_task(db, task_id)
    if not db_task:
        return False
    await db.delete(db_task)
    await db.commit()
    return True


async def move_task(db: AsyncSession, task_id: str, status: str) -> Optional[models.Task]:
    db_task = await get_task(db, task_id)
    if not db_task:
        return None
    db_task.status = status
    db_task.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(db_task)
    return db_task


async def get_task_blockers(db: AsyncSession, task_id: str) -> List[Dict[str, Any]]:
    db_task = await get_task(db, task_id)
    if not db_task or not db_task.blocked_by:
        return []
    chain: List[Dict[str, Any]] = []
    for bid in db_task.blocked_by:
        blocker = await get_task(db, bid)
        if blocker:
            chain.append({
                "id": blocker.id,
                "title": blocker.title,
                "status": blocker.status,
            })
    return chain


async def bulk_update_tasks(
    db: AsyncSession, data: schemas.BulkTaskUpdate
) -> schemas.BulkTaskResult:
    errors: List[str] = []
    updated = 0
    for tid in data.ids:
        task = await get_task(db, tid)
        if not task:
            errors.append(f"Task {tid} not found")
            continue
        payload = data.model_dump(exclude_unset=True, exclude={"ids"})
        for key, value in payload.items():
            if value is not None:
                if key == "blocked_by":
                    value = _parse_blocked_by(value)
                setattr(task, key, value)
        task.updated_at = datetime.utcnow()
        updated += 1
    await db.commit()
    return schemas.BulkTaskResult(updated=updated, errors=errors)


# ---------------------------------------------------------------------------
# Daily Log
# ---------------------------------------------------------------------------
async def get_daily_log(db: AsyncSession, log_id: str) -> Optional[models.DailyLog]:
    result = await db.execute(select(models.DailyLog).filter(models.DailyLog.id == log_id))
    return result.scalars().first()


async def get_daily_logs(
    db: AsyncSession,
    sprint_id: Optional[str] = None,
    date: Optional[date] = None,
    member_id: Optional[str] = None,
) -> List[models.DailyLog]:
    query = select(models.DailyLog)
    if sprint_id:
        query = query.filter(models.DailyLog.sprint_id == sprint_id)
    if date:
        query = query.filter(models.DailyLog.date == date)
    if member_id:
        query = query.filter(models.DailyLog.member_id == member_id)
    result = await db.execute(query.order_by(models.DailyLog.date.desc()))
    return list(result.scalars().all())


async def upsert_daily_log(db: AsyncSession, log: schemas.DailyLogCreate) -> models.DailyLog:
    result = await db.execute(
        select(models.DailyLog).filter(
            and_(
                models.DailyLog.sprint_id == log.sprint_id,
                models.DailyLog.member_id == log.member_id,
                models.DailyLog.date == log.date,
            )
        )
    )
    existing = result.scalars().first()
    if existing:
        for key, value in log.model_dump().items():
            setattr(existing, key, value)
        await db.commit()
        await db.refresh(existing)
        return existing
    db_log = models.DailyLog(**log.model_dump())
    db.add(db_log)
    await db.commit()
    await db.refresh(db_log)
    return db_log


async def batch_upsert_daily_logs(
    db: AsyncSession, batch: schemas.DailyLogBatch
) -> schemas.DailyLogBatchResult:
    created = 0
    updated = 0
    errors: List[str] = []
    for log in batch.logs:
        try:
            result = await db.execute(
                select(models.DailyLog).filter(
                    and_(
                        models.DailyLog.sprint_id == log.sprint_id,
                        models.DailyLog.member_id == log.member_id,
                        models.DailyLog.date == log.date,
                    )
                )
            )
            existing = result.scalars().first()
            if existing:
                for key, value in log.model_dump().items():
                    setattr(existing, key, value)
                updated += 1
            else:
                db_log = models.DailyLog(**log.model_dump())
                db.add(db_log)
                created += 1
        except Exception as e:
            errors.append(str(e))
    await db.commit()
    return schemas.DailyLogBatchResult(created=created, updated=updated, errors=errors)


# ---------------------------------------------------------------------------
# Retro
# ---------------------------------------------------------------------------
async def get_retro(db: AsyncSession, retro_id: str) -> Optional[models.Retro]:
    result = await db.execute(select(models.Retro).filter(models.Retro.id == retro_id))
    return result.scalars().first()


async def get_retros_by_sprint(db: AsyncSession, sprint_id: str) -> List[models.Retro]:
    result = await db.execute(select(models.Retro).filter(models.Retro.sprint_id == sprint_id))
    return list(result.scalars().all())


async def create_retro(db: AsyncSession, retro: schemas.RetroCreate) -> models.Retro:
    db_retro = models.Retro(**retro.model_dump())
    db.add(db_retro)
    await db.commit()
    await db.refresh(db_retro)
    return db_retro


async def vote_retro(db: AsyncSession, retro_id: str) -> Optional[models.Retro]:
    db_retro = await get_retro(db, retro_id)
    if not db_retro:
        return None
    db_retro.votes += 1
    await db.commit()
    await db.refresh(db_retro)
    return db_retro


async def create_retro_rating(
    db: AsyncSession, rating: schemas.RetroRatingCreate
) -> models.RetroRating:
    db_rating = models.RetroRating(**rating.model_dump())
    db.add(db_rating)
    await db.commit()
    await db.refresh(db_rating)
    return db_rating


async def get_retro_ratings(db: AsyncSession, sprint_id: str) -> List[models.RetroRating]:
    result = await db.execute(
        select(models.RetroRating).filter(models.RetroRating.sprint_id == sprint_id)
    )
    return list(result.scalars().all())


# ---------------------------------------------------------------------------
# Agent Message
# ---------------------------------------------------------------------------
async def create_agent_message(
    db: AsyncSession, msg: schemas.AgentMessageCreate
) -> models.AgentMessage:
    db_msg = models.AgentMessage(
        role=msg.role,
        content=msg.content,
        context=msg.context,
    )
    db.add(db_msg)
    await db.commit()
    await db.refresh(db_msg)
    return db_msg


async def get_agent_messages(db: AsyncSession, limit: int = 50) -> List[models.AgentMessage]:
    result = await db.execute(
        select(models.AgentMessage)
        .order_by(models.AgentMessage.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
async def get_config(db: AsyncSession, key: str) -> Optional[models.Config]:
    result = await db.execute(select(models.Config).filter(models.Config.key == key))
    return result.scalars().first()


async def get_all_config(db: AsyncSession) -> List[models.Config]:
    result = await db.execute(select(models.Config))
    return list(result.scalars().all())


async def set_config(
    db: AsyncSession, key: str, value: Optional[str]
) -> models.Config:
    existing = await get_config(db, key)
    if existing:
        existing.value = value
        await db.commit()
        await db.refresh(existing)
        return existing
    item = models.Config(key=key, value=value)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def set_multiple_config(
    db: AsyncSession, settings: Dict[str, Optional[str]]
) -> List[models.Config]:
    results: List[models.Config] = []
    for key, value in settings.items():
        result = await set_config(db, key, value)
        results.append(result)
    return results
