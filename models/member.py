from dataclasses import dataclass, field
from typing import List, Set


@dataclass
class Member:
    id: str
    name: str
    coefficient: float = 1.0
    leave_days: float = 0.0
    timezone: str = "Asia/Shanghai"
    interviewed_tasks: Set[str] = field(default_factory=set)
    tasks: List["Task"] = field(default_factory=list)

    def capacity(self, sprint) -> float:
        return sprint.workdays * self.coefficient - self.leave_days

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "coefficient": self.coefficient,
            "leave_days": self.leave_days,
            "timezone": self.timezone,
            "interviewed_tasks": list(self.interviewed_tasks),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Member":
        member = cls(
            id=data["id"],
            name=data["name"],
            coefficient=data.get("coefficient", 1.0),
            leave_days=data.get("leave_days", 0.0),
            timezone=data.get("timezone", "Asia/Shanghai"),
            interviewed_tasks=set(data.get("interviewed_tasks", [])),
        )
        return member
