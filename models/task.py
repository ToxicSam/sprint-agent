from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import List, Optional


class TaskStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"


@dataclass
class Task:
    id: str
    name: str
    us: str = ""
    owner_id: str = ""
    priority: int = 5
    ddl: Optional[date] = None
    estimate_low: float = 0.0
    estimate_high: float = 0.0
    status: TaskStatus = TaskStatus.NOT_STARTED
    is_public: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    daily_logs: List["DailyLog"] = field(default_factory=list)
    total_spent: float = 0.0
    paused_at: Optional[datetime] = None
    paused_reason: str = ""
    blocker: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "us": self.us,
            "owner_id": self.owner_id,
            "priority": self.priority,
            "ddl": self.ddl.isoformat() if self.ddl else None,
            "estimate_low": self.estimate_low,
            "estimate_high": self.estimate_high,
            "status": self.status.value,
            "is_public": self.is_public,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "daily_logs": [log.to_dict() for log in self.daily_logs],
            "total_spent": self.total_spent,
            "paused_at": self.paused_at.isoformat() if self.paused_at else None,
            "paused_reason": self.paused_reason,
            "blocker": self.blocker,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        from .daily_log import DailyLog

        task = cls(
            id=data["id"],
            name=data["name"],
            us=data.get("us", ""),
            owner_id=data.get("owner_id", ""),
            priority=data.get("priority", 5),
            ddl=date.fromisoformat(data["ddl"]) if data.get("ddl") else None,
            estimate_low=data.get("estimate_low", 0.0),
            estimate_high=data.get("estimate_high", 0.0),
            status=TaskStatus(data["status"]) if "status" in data else TaskStatus.NOT_STARTED,
            is_public=data.get("is_public", False),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            total_spent=data.get("total_spent", 0.0),
            paused_at=datetime.fromisoformat(data["paused_at"]) if data.get("paused_at") else None,
            paused_reason=data.get("paused_reason", ""),
            blocker=data.get("blocker"),
        )
        task.daily_logs = [DailyLog.from_dict(log) for log in data.get("daily_logs", [])]
        return task
