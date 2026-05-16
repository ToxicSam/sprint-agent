from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class DailyLog:
    id: str
    date: date
    member_id: str
    task_id: str
    hours: float
    progress_percent: int = None
    blocker: str = None
    notes: str = ""
    created_at: datetime = datetime.now()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "date": self.date.isoformat() if self.date else None,
            "member_id": self.member_id,
            "task_id": self.task_id,
            "hours": self.hours,
            "progress_percent": self.progress_percent,
            "blocker": self.blocker,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DailyLog":
        return cls(
            id=data["id"],
            date=date.fromisoformat(data["date"]) if data.get("date") else None,
            member_id=data["member_id"],
            task_id=data["task_id"],
            hours=data["hours"],
            progress_percent=data.get("progress_percent"),
            blocker=data.get("blocker"),
            notes=data.get("notes", ""),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(),
        )
