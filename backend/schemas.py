from datetime import datetime, date
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
# Sprint
# ---------------------------------------------------------------------------
class SprintBase(BaseModel):
    name: str
    goal: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str = "active"


class SprintCreate(SprintBase):
    pass


class SprintUpdate(BaseModel):
    name: Optional[str] = None
    goal: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None


class SprintResponse(SprintBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime


class SprintStats(BaseModel):
    total_tasks: int
    todo: int
    progress: int
    done: int
    paused: int
    total_story_points: float
    completed_story_points: float
    remaining_story_points: float
    completion_rate: float
    members_active: int


# ---------------------------------------------------------------------------
# Member
# ---------------------------------------------------------------------------
class MemberBase(BaseModel):
    name: str
    role: str
    capacity: Optional[float] = None
    avatar: Optional[str] = None


class MemberCreate(MemberBase):
    pass


class MemberUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    capacity: Optional[float] = None
    avatar: Optional[str] = None


class MemberResponse(MemberBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------
class TaskBase(BaseModel):
    title: str
    sprint_id: str
    assignee_id: Optional[str] = None
    status: str = "todo"
    priority: Optional[int] = None
    story_points: Optional[float] = None
    blocked_by: Optional[str] = None
    description: Optional[str] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    sprint_id: Optional[str] = None
    assignee_id: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = None
    story_points: Optional[float] = None
    blocked_by: Optional[str] = None
    description: Optional[str] = None


class TaskResponse(TaskBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime
    updated_at: datetime
    assignee: Optional[MemberResponse] = None


class TaskMove(BaseModel):
    status: str


class BulkTaskUpdate(BaseModel):
    ids: List[str]
    status: Optional[str] = None
    assignee_id: Optional[str] = None
    sprint_id: Optional[str] = None


class BulkTaskResult(BaseModel):
    updated: int
    errors: List[str] = []


# ---------------------------------------------------------------------------
# Board (aggregated view)
# ---------------------------------------------------------------------------
class BoardResponse(BaseModel):
    sprint: Optional[SprintResponse] = None
    members: List[MemberResponse] = []
    tasks: List[TaskResponse] = []


# ---------------------------------------------------------------------------
# Daily Log
# ---------------------------------------------------------------------------
class DailyLogBase(BaseModel):
    sprint_id: str
    member_id: str
    date: date
    completed: Optional[str] = None
    planned: Optional[str] = None
    blockers: Optional[str] = None
    hours_spent: Optional[float] = None


class DailyLogCreate(DailyLogBase):
    pass


class DailyLogUpdate(BaseModel):
    completed: Optional[str] = None
    planned: Optional[str] = None
    blockers: Optional[str] = None
    hours_spent: Optional[float] = None


class DailyLogResponse(DailyLogBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime
    member: Optional[MemberResponse] = None


class DailyLogBatch(BaseModel):
    logs: List[DailyLogCreate]


class DailyLogBatchResult(BaseModel):
    created: int
    updated: int
    errors: List[str] = []


# ---------------------------------------------------------------------------
# Retro
# ---------------------------------------------------------------------------
class RetroBase(BaseModel):
    sprint_id: str
    category: str
    item: str
    votes: int = 0


class RetroCreate(RetroBase):
    pass


class RetroVote(BaseModel):
    retro_id: str


class RetroRatingCreate(BaseModel):
    sprint_id: str
    dimension: str
    score: int


class RetroResponse(RetroBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime


class RetroRatingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    sprint_id: str
    dimension: str
    score: int
    created_at: datetime


class RetroReport(BaseModel):
    liked: List[RetroResponse]
    disliked: List[RetroResponse]
    action_items: List[RetroResponse]
    ratings: Dict[str, float]
    summary: str


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------
class AgentMessageCreate(BaseModel):
    role: str = "user"
    content: str
    context: Optional[Dict[str, Any]] = None


class AgentMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    role: str
    content: str
    context: Optional[str] = None
    created_at: datetime


class AgentAction(BaseModel):
    action: str
    payload: Dict[str, Any]


class AgentActionResult(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class AgentContext(BaseModel):
    current_sprint: Optional[SprintResponse] = None
    recent_tasks: List[TaskResponse] = []
    members: List[MemberResponse] = []
    messages: List[AgentMessageResponse] = []


# ---------------------------------------------------------------------------
# Config / Settings
# ---------------------------------------------------------------------------
class ConfigItem(BaseModel):
    key: str
    value: Optional[str] = None


class ConfigUpdate(BaseModel):
    settings: Dict[str, Optional[str]]


# ---------------------------------------------------------------------------
# Import / Export
# ---------------------------------------------------------------------------
class ImportPayload(BaseModel):
    data: Dict[str, Any]


class ImportResult(BaseModel):
    summary: str
    inserted: Dict[str, int]
    errors: List[str] = []


class ExportData(BaseModel):
    sprints: List[Dict[str, Any]]
    members: List[Dict[str, Any]]
    tasks: List[Dict[str, Any]]
    daily_logs: List[Dict[str, Any]]
    retros: List[Dict[str, Any]]
    retro_ratings: List[Dict[str, Any]]
    agent_messages: List[Dict[str, Any]]
    config: List[Dict[str, Any]]
