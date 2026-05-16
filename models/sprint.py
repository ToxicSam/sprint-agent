from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import List, Optional


class SprintStatus(Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


@dataclass
class Sprint:
    id: str
    name: str
    start_date: date
    end_date: date
    workdays: int = 10
    status: SprintStatus = SprintStatus.PLANNING
    goal: str = ""
    members: List["Member"] = field(default_factory=list)
    tasks: List["Task"] = field(default_factory=list)
    public_tasks: List["Task"] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    version: int = 1

    def get_member_by_name(self, name: str) -> Optional["Member"]:
        for m in self.members:
            if m.name == name or m.id == name:
                return m
        return None

    def get_task_by_name(self, name: str) -> Optional["Task"]:
        for t in self.tasks + self.public_tasks:
            if t.name == name or t.id == name:
                return t
        return None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "workdays": self.workdays,
            "status": self.status.value,
            "goal": self.goal,
            "members": [m.to_dict() for m in self.members],
            "tasks": [t.to_dict() for t in self.tasks],
            "public_tasks": [t.to_dict() for t in self.public_tasks],
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Sprint":
        from .member import Member
        from .task import Task

        sprint = cls(
            id=data["id"],
            name=data["name"],
            start_date=date.fromisoformat(data["start_date"]),
            end_date=date.fromisoformat(data["end_date"]),
            workdays=data.get("workdays", 10),
            status=SprintStatus(data["status"]),
            goal=data.get("goal", ""),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            version=data.get("version", 1),
        )
        sprint.members = [Member.from_dict(m) for m in data.get("members", [])]
        sprint.tasks = [Task.from_dict(t) for t in data.get("tasks", [])]
        sprint.public_tasks = [Task.from_dict(t) for t in data.get("public_tasks", [])]
        return sprint
