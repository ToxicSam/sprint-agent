from typing import Optional, List, Dict, Any
from datetime import date, datetime
import json

from sqlalchemy.orm import Session
from sqlalchemy import func, and_

import models
import schemas


# ---------------------------------------------------------------------------
# Sprint
# ---------------------------------------------------------------------------
def get_sprint(db: Session, sprint_id: str) -> Optional[models.Sprint]:
    return db.query(models.Sprint).filter(models.Sprint.id == sprint_id).first()


def get_active_sprint(db: Session) -> Optional[models.Sprint]:
    return db.query(models.Sprint).filter(models.Sprint.status == "active").first()


def get_sprints(db: Session, skip: int = 0, limit: int = 100) -> List[models.Sprint]:
    return db.query(models.Sprint).offset(skip).limit(limit).all()


def create_sprint(db: Session, sprint: schemas.SprintCreate) -> models.Sprint:
    db_sprint = models.Sprint(**sprint.model_dump())
    db.add(db_sprint)
    db.commit()
    db.refresh(db_sprint)
    return db_sprint


def update_sprint(db: Session, sprint_id: str, sprint: schemas.SprintUpdate) -> Optional[models.Sprint]:
    db_sprint = get_sprint(db, sprint_id)
    if not db_sprint:
        return None
    for key, value in sprint.model_dump(exclude_unset=True).items():
        setattr(db_sprint, key, value)
    db.commit()
    db.refresh(db_sprint)
    return db_sprint


def delete_sprint(db: Session, sprint_id: str) -> bool:
    db_sprint = get_sprint(db, sprint_id)
    if not db_sprint:
        return False
    db.delete(db_sprint)
    db.commit()
    return True


def get_sprint_stats(db: Session, sprint_id: str) -> Dict[str, Any]:
    tasks = db.query(models.Task).filter(models.Task.sprint_id == sprint_id).all()
    total = len(tasks)
    todo = sum(1 for t in tasks if t.status == "todo")
    progress = sum(1 for t in tasks if t.status == "progress")
    done = sum(1 for t in tasks if t.status == "done")
    paused = sum(1 for t in tasks if t.status == "paused")
    total_sp = sum(t.story_points or 0 for t in tasks)
    completed_sp = sum(t.story_points or 0 for t in tasks if t.status == "done")
    remaining = total_sp - completed_sp
    rate = (completed_sp / total_sp * 100) if total_sp else 0.0
    members_active = db.query(models.Task.assignee_id).filter(
        models.Task.sprint_id == sprint_id,
        models.Task.assignee_id.isnot(None)
    ).distinct().count()
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
def get_member(db: Session, member_id: str) -> Optional[models.Member]:
    return db.query(models.Member).filter(models.Member.id == member_id).first()


def get_members(db: Session, skip: int = 0, limit: int = 100) -> List[models.Member]:
    return db.query(models.Member).offset(skip).limit(limit).all()


def create_member(db: Session, member: schemas.MemberCreate) -> models.Member:
    db_member = models.Member(**member.model_dump())
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


def update_member(db: Session, member_id: str, member: schemas.MemberUpdate) -> Optional[models.Member]:
    db_member = get_member(db, member_id)
    if not db_member:
        return None
    for key, value in member.model_dump(exclude_unset=True).items():
        setattr(db_member, key, value)
    db.commit()
    db.refresh(db_member)
    return db_member


def delete_member(db: Session, member_id: str) -> bool:
    db_member = get_member(db, member_id)
    if not db_member:
        return False
    db.delete(db_member)
    db.commit()
    return True


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------
def get_task(db: Session, task_id: str) -> Optional[models.Task]:
    return db.query(models.Task).filter(models.Task.id == task_id).first()


def get_tasks(
    db: Session,
    sprint_id: Optional[str] = None,
    status: Optional[str] = None,
    assignee_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 200,
) -> List[models.Task]:
    query = db.query(models.Task)
    if sprint_id:
        query = query.filter(models.Task.sprint_id == sprint_id)
    if status:
        query = query.filter(models.Task.status == status)
    if assignee_id:
        query = query.filter(models.Task.assignee_id == assignee_id)
    return query.offset(skip).limit(limit).all()


def create_task(db: Session, task: schemas.TaskCreate) -> models.Task:
    db_task = models.Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(db: Session, task_id: str, task: schemas.TaskUpdate) -> Optional[models.Task]:
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    for key, value in task.model_dump(exclude_unset=True).items():
        setattr(db_task, key, value)
    db_task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: str) -> bool:
    db_task = get_task(db, task_id)
    if not db_task:
        return False
    db.delete(db_task)
    db.commit()
    return True


def move_task(db: Session, task_id: str, status: str) -> Optional[models.Task]:
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    db_task.status = status
    db_task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_task)
    return db_task


def get_task_blockers(db: Session, task_id: str) -> List[Dict[str, Any]]:
    db_task = get_task(db, task_id)
    if not db_task or not db_task.blocked_by:
        return []
    try:
        blocker_ids = json.loads(db_task.blocked_by)
    except json.JSONDecodeError:
        return []
    chain = []
    for bid in blocker_ids:
        blocker = get_task(db, bid)
        if blocker:
            chain.append({
                "id": blocker.id,
                "title": blocker.title,
                "status": blocker.status,
            })
    return chain


def bulk_update_tasks(db: Session, data: schemas.BulkTaskUpdate) -> schemas.BulkTaskResult:
    errors: List[str] = []
    updated = 0
    for tid in data.ids:
        task = get_task(db, tid)
        if not task:
            errors.append(f"Task {tid} not found")
            continue
        payload = data.model_dump(exclude_unset=True, exclude={"ids"})
        for key, value in payload.items():
            if value is not None:
                setattr(task, key, value)
        task.updated_at = datetime.utcnow()
        updated += 1
    db.commit()
    return schemas.BulkTaskResult(updated=updated, errors=errors)


# ---------------------------------------------------------------------------
# Daily Log
# ---------------------------------------------------------------------------
def get_daily_log(db: Session, log_id: str) -> Optional[models.DailyLog]:
    return db.query(models.DailyLog).filter(models.DailyLog.id == log_id).first()


def get_daily_logs(
    db: Session,
    sprint_id: Optional[str] = None,
    date: Optional[date] = None,
    member_id: Optional[str] = None,
) -> List[models.DailyLog]:
    query = db.query(models.DailyLog)
    if sprint_id:
        query = query.filter(models.DailyLog.sprint_id == sprint_id)
    if date:
        query = query.filter(models.DailyLog.date == date)
    if member_id:
        query = query.filter(models.DailyLog.member_id == member_id)
    return query.order_by(models.DailyLog.date.desc()).all()


def upsert_daily_log(db: Session, log: schemas.DailyLogCreate) -> models.DailyLog:
    existing = db.query(models.DailyLog).filter(
        and_(
            models.DailyLog.sprint_id == log.sprint_id,
            models.DailyLog.member_id == log.member_id,
            models.DailyLog.date == log.date,
        )
    ).first()
    if existing:
        for key, value in log.model_dump().items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return existing
    db_log = models.DailyLog(**log.model_dump())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def batch_upsert_daily_logs(db: Session, batch: schemas.DailyLogBatch) -> schemas.DailyLogBatchResult:
    created = 0
    updated = 0
    errors: List[str] = []
    for log in batch.logs:
        try:
            existing = db.query(models.DailyLog).filter(
                and_(
                    models.DailyLog.sprint_id == log.sprint_id,
                    models.DailyLog.member_id == log.member_id,
                    models.DailyLog.date == log.date,
                )
            ).first()
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
    db.commit()
    return schemas.DailyLogBatchResult(created=created, updated=updated, errors=errors)


# ---------------------------------------------------------------------------
# Retro
# ---------------------------------------------------------------------------
def get_retro(db: Session, retro_id: str) -> Optional[models.Retro]:
    return db.query(models.Retro).filter(models.Retro.id == retro_id).first()


def get_retros_by_sprint(db: Session, sprint_id: str) -> List[models.Retro]:
    return db.query(models.Retro).filter(models.Retro.sprint_id == sprint_id).all()


def create_retro(db: Session, retro: schemas.RetroCreate) -> models.Retro:
    db_retro = models.Retro(**retro.model_dump())
    db.add(db_retro)
    db.commit()
    db.refresh(db_retro)
    return db_retro


def vote_retro(db: Session, retro_id: str) -> Optional[models.Retro]:
    db_retro = get_retro(db, retro_id)
    if not db_retro:
        return None
    db_retro.votes += 1
    db.commit()
    db.refresh(db_retro)
    return db_retro


def create_retro_rating(db: Session, rating: schemas.RetroRatingCreate) -> models.RetroRating:
    db_rating = models.RetroRating(**rating.model_dump())
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return db_rating


def get_retro_ratings(db: Session, sprint_id: str) -> List[models.RetroRating]:
    return db.query(models.RetroRating).filter(models.RetroRating.sprint_id == sprint_id).all()


# ---------------------------------------------------------------------------
# Agent Message
# ---------------------------------------------------------------------------
def create_agent_message(db: Session, msg: schemas.AgentMessageCreate) -> models.AgentMessage:
    context_json = None
    if msg.context:
        context_json = json.dumps(msg.context)
    db_msg = models.AgentMessage(
        role=msg.role,
        content=msg.content,
        context=context_json,
    )
    db.add(db_msg)
    db.commit()
    db.refresh(db_msg)
    return db_msg


def get_agent_messages(db: Session, limit: int = 50) -> List[models.AgentMessage]:
    return db.query(models.AgentMessage).order_by(models.AgentMessage.created_at.desc()).limit(limit).all()


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
def get_config(db: Session, key: str) -> Optional[models.Config]:
    return db.query(models.Config).filter(models.Config.key == key).first()


def get_all_config(db: Session) -> List[models.Config]:
    return db.query(models.Config).all()


def set_config(db: Session, key: str, value: Optional[str]) -> models.Config:
    existing = get_config(db, key)
    if existing:
        existing.value = value
        db.commit()
        db.refresh(existing)
        return existing
    item = models.Config(key=key, value=value)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def set_multiple_config(db: Session, settings: Dict[str, Optional[str]]) -> List[models.Config]:
    results = []
    for key, value in settings.items():
        results.append(set_config(db, key, value))
    return results
