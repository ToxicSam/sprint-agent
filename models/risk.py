from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict


class RiskType(Enum):
    ESTIMATE_EXCEEDED = "estimate_exceeded"
    NO_PROGRESS = "no_progress"
    CAPACITY_WARNING = "capacity_warning"
    OVER_CAPACITY = "over_capacity"
    DEADLINE_APPROACHING = "deadline_approaching"
    BLOCKER_STUCK = "blocker_stuck"
    MISSING_DATA = "missing_data"


class RiskSeverity(Enum):
    HIGH = "🔴"
    MEDIUM = "🟡"
    LOW = "🟢"


@dataclass
class RiskFlag:
    id: str
    type: RiskType
    severity: RiskSeverity
    member_id: str
    task_id: Optional[str]
    message: str
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    auto_resolved: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type.value,
            "severity": self.severity.value,
            "member_id": self.member_id,
            "task_id": self.task_id,
            "message": self.message,
            "created_at": self.created_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "auto_resolved": self.auto_resolved,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RiskFlag":
        return cls(
            id=data["id"],
            type=RiskType(data["type"]),
            severity=RiskSeverity(data["severity"]),
            member_id=data["member_id"],
            task_id=data.get("task_id"),
            message=data["message"],
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            resolved_at=datetime.fromisoformat(data["resolved_at"]) if data.get("resolved_at") else None,
            auto_resolved=data.get("auto_resolved", False),
        )
