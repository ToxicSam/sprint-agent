from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional

from .story_pool import StoryPoolEntry


class ReviewStatus(Enum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"


@dataclass
class Dimension:
    key: str
    name: str
    weight: float
    stories: List[StoryPoolEntry] = field(default_factory=list)
    score: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "name": self.name,
            "weight": self.weight,
            "stories": [s.to_dict() for s in self.stories],
            "score": self.score,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Dimension":
        dim = cls(
            key=data["key"],
            name=data["name"],
            weight=data["weight"],
            score=data.get("score"),
        )
        dim.stories = [StoryPoolEntry.from_dict(s) for s in data.get("stories", [])]
        return dim


@dataclass
class SelfAssessment:
    id: str
    period: str
    member_id: str
    generated_at: datetime = field(default_factory=datetime.now)
    dimensions: List[Dimension] = field(default_factory=list)
    auto_stories: List[StoryPoolEntry] = field(default_factory=list)
    manual_stories: List[StoryPoolEntry] = field(default_factory=list)
    raw_sprint_ids: List[str] = field(default_factory=list)
    markdown_content: str = ""
    review_round: int = 0
    review_status: ReviewStatus = ReviewStatus.DRAFT

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "period": self.period,
            "member_id": self.member_id,
            "generated_at": self.generated_at.isoformat(),
            "dimensions": [d.to_dict() for d in self.dimensions],
            "auto_stories": [s.to_dict() for s in self.auto_stories],
            "manual_stories": [s.to_dict() for s in self.manual_stories],
            "raw_sprint_ids": self.raw_sprint_ids,
            "markdown_content": self.markdown_content,
            "review_round": self.review_round,
            "review_status": self.review_status.value,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SelfAssessment":
        assessment = cls(
            id=data["id"],
            period=data["period"],
            member_id=data["member_id"],
            generated_at=datetime.fromisoformat(data["generated_at"]) if "generated_at" in data else datetime.now(),
            markdown_content=data.get("markdown_content", ""),
            review_round=data.get("review_round", 0),
            review_status=ReviewStatus(data["review_status"]) if "review_status" in data else ReviewStatus.DRAFT,
            raw_sprint_ids=data.get("raw_sprint_ids", []),
        )
        assessment.dimensions = [Dimension.from_dict(d) for d in data.get("dimensions", [])]
        assessment.auto_stories = [StoryPoolEntry.from_dict(s) for s in data.get("auto_stories", [])]
        assessment.manual_stories = [StoryPoolEntry.from_dict(s) for s in data.get("manual_stories", [])]
        return assessment
