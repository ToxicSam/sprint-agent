from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class InterviewStatus(Enum):
    PENDING = "pending"
    ANSWERED = "answered"
    CONFIRMED = "confirmed"
    SKIPPED = "skipped"
    EXPIRED = "expired"


class QuestionType(Enum):
    METHODOLOGY = "methodology"
    STAR_EXTRACTION = "star_extraction"
    DIMENSION_ALIGNMENT = "dimension_alignment"


@dataclass
class Question:
    id: str
    type: QuestionType
    text: str
    target_dimension: str
    order: int

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type.value,
            "text": self.text,
            "target_dimension": self.target_dimension,
            "order": self.order,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Question":
        return cls(
            id=data["id"],
            type=QuestionType(data["type"]),
            text=data["text"],
            target_dimension=data["target_dimension"],
            order=data["order"],
        )


@dataclass
class Answer:
    question_id: str
    text: str
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "question_id": self.question_id,
            "text": self.text,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Answer":
        return cls(
            question_id=data["question_id"],
            text=data["text"],
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
        )


@dataclass
class InterviewSession:
    id: str
    date: datetime
    member_id: str
    task_id: Optional[str]
    standup_log_id: str
    questions: List[Question] = field(default_factory=list)
    answers: List[Answer] = field(default_factory=list)
    stories_extracted: List[str] = field(default_factory=list)  # story_entry ids
    status: InterviewStatus = InterviewStatus.PENDING
    skipped: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "date": self.date.isoformat(),
            "member_id": self.member_id,
            "task_id": self.task_id,
            "standup_log_id": self.standup_log_id,
            "questions": [q.to_dict() for q in self.questions],
            "answers": [a.to_dict() for a in self.answers],
            "stories_extracted": self.stories_extracted,
            "status": self.status.value,
            "skipped": self.skipped,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "InterviewSession":
        session = cls(
            id=data["id"],
            date=datetime.fromisoformat(data["date"]),
            member_id=data["member_id"],
            task_id=data.get("task_id"),
            standup_log_id=data["standup_log_id"],
            status=InterviewStatus(data["status"]),
            skipped=data.get("skipped", False),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
        )
        session.questions = [Question.from_dict(q) for q in data.get("questions", [])]
        session.answers = [Answer.from_dict(a) for a in data.get("answers", [])]
        session.stories_extracted = data.get("stories_extracted", [])
        return session
