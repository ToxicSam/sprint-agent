from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class STAR:
    situation: str = ""
    task: str = ""
    action: str = ""
    result: str = ""
    review: str = ""

    def to_dict(self) -> dict:
        return {
            "situation": self.situation,
            "task": self.task,
            "action": self.action,
            "result": self.result,
            "review": self.review,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "STAR":
        return cls(
            situation=data.get("situation", ""),
            task=data.get("task", ""),
            action=data.get("action", ""),
            result=data.get("result", ""),
            review=data.get("review", ""),
        )


@dataclass
class StoryPoolEntry:
    id: str
    member_id: str
    sprint_id: str
    dimension: str
    dimension_name: str
    star: STAR
    source: str
    extracted_at: datetime = field(default_factory=datetime.now)
    confirmed: bool = False
    quality_score: float = 0.0
    task_id: Optional[str] = None
    interview_session_id: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "member_id": self.member_id,
            "sprint_id": self.sprint_id,
            "task_id": self.task_id,
            "dimension": self.dimension,
            "dimension_name": self.dimension_name,
            "star": self.star.to_dict(),
            "source": self.source,
            "extracted_at": self.extracted_at.isoformat(),
            "confirmed": self.confirmed,
            "quality_score": self.quality_score,
            "interview_session_id": self.interview_session_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "StoryPoolEntry":
        return cls(
            id=data["id"],
            member_id=data["member_id"],
            sprint_id=data["sprint_id"],
            task_id=data.get("task_id"),
            dimension=data["dimension"],
            dimension_name=data["dimension_name"],
            star=STAR.from_dict(data["star"]),
            source=data["source"],
            extracted_at=datetime.fromisoformat(data["extracted_at"]) if "extracted_at" in data else datetime.now(),
            confirmed=data.get("confirmed", False),
            quality_score=data.get("quality_score", 0.0),
            interview_session_id=data.get("interview_session_id"),
        )
