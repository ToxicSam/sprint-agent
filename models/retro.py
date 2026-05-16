from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict

from .risk import RiskFlag


@dataclass
class MemberSummary:
    member_id: str
    total_spent: float = 0.0
    total_estimate_low: float = 0.0
    total_estimate_high: float = 0.0
    tasks_completed: int = 0
    tasks_in_progress: int = 0
    tasks_paused: int = 0
    difficulty: float = 0.0
    credibility: float = 0.0
    estimate_deviation: float = 0.0
    capacity_utilization: float = 0.0
    missing_data_days: int = 0
    story_count: int = 0

    def to_dict(self) -> dict:
        return {
            "member_id": self.member_id,
            "total_spent": self.total_spent,
            "total_estimate_low": self.total_estimate_low,
            "total_estimate_high": self.total_estimate_high,
            "tasks_completed": self.tasks_completed,
            "tasks_in_progress": self.tasks_in_progress,
            "tasks_paused": self.tasks_paused,
            "difficulty": self.difficulty,
            "credibility": self.credibility,
            "estimate_deviation": self.estimate_deviation,
            "capacity_utilization": self.capacity_utilization,
            "missing_data_days": self.missing_data_days,
            "story_count": self.story_count,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MemberSummary":
        return cls(
            member_id=data["member_id"],
            total_spent=data.get("total_spent", 0.0),
            total_estimate_low=data.get("total_estimate_low", 0.0),
            total_estimate_high=data.get("total_estimate_high", 0.0),
            tasks_completed=data.get("tasks_completed", 0),
            tasks_in_progress=data.get("tasks_in_progress", 0),
            tasks_paused=data.get("tasks_paused", 0),
            difficulty=data.get("difficulty", 0.0),
            credibility=data.get("credibility", 0.0),
            estimate_deviation=data.get("estimate_deviation", 0.0),
            capacity_utilization=data.get("capacity_utilization", 0.0),
            missing_data_days=data.get("missing_data_days", 0),
            story_count=data.get("story_count", 0),
        )


@dataclass
class PublicOverhead:
    total_hours: float = 0.0
    per_member_avg: float = 0.0
    breakdown: Dict[str, float] = field(default_factory=dict)
    percentage_of_capacity: float = 0.0

    def to_dict(self) -> dict:
        return {
            "total_hours": self.total_hours,
            "per_member_avg": self.per_member_avg,
            "breakdown": self.breakdown,
            "percentage_of_capacity": self.percentage_of_capacity,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PublicOverhead":
        return cls(
            total_hours=data.get("total_hours", 0.0),
            per_member_avg=data.get("per_member_avg", 0.0),
            breakdown=data.get("breakdown", {}),
            percentage_of_capacity=data.get("percentage_of_capacity", 0.0),
        )


@dataclass
class InterviewSummary:
    total_sessions: int = 0
    completed_sessions: int = 0
    skipped_sessions: int = 0
    methodology_improvements: List[str] = field(default_factory=list)
    stories_generated: int = 0

    def to_dict(self) -> dict:
        return {
            "total_sessions": self.total_sessions,
            "completed_sessions": self.completed_sessions,
            "skipped_sessions": self.skipped_sessions,
            "methodology_improvements": self.methodology_improvements,
            "stories_generated": self.stories_generated,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "InterviewSummary":
        return cls(
            total_sessions=data.get("total_sessions", 0),
            completed_sessions=data.get("completed_sessions", 0),
            skipped_sessions=data.get("skipped_sessions", 0),
            methodology_improvements=data.get("methodology_improvements", []),
            stories_generated=data.get("stories_generated", 0),
        )


@dataclass
class TrendAnalysis:
    sprint_ids: List[str] = field(default_factory=list)
    estimate_accuracy_trend: List[float] = field(default_factory=list)
    capacity_utilization_trend: List[float] = field(default_factory=list)
    story_density_trend: List[float] = field(default_factory=list)
    public_overhead_trend: List[float] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "sprint_ids": self.sprint_ids,
            "estimate_accuracy_trend": self.estimate_accuracy_trend,
            "capacity_utilization_trend": self.capacity_utilization_trend,
            "story_density_trend": self.story_density_trend,
            "public_overhead_trend": self.public_overhead_trend,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TrendAnalysis":
        return cls(
            sprint_ids=data.get("sprint_ids", []),
            estimate_accuracy_trend=data.get("estimate_accuracy_trend", []),
            capacity_utilization_trend=data.get("capacity_utilization_trend", []),
            story_density_trend=data.get("story_density_trend", []),
            public_overhead_trend=data.get("public_overhead_trend", []),
        )


@dataclass
class RetroReport:
    id: str
    sprint_id: str
    generated_at: datetime = field(default_factory=datetime.now)
    member_summaries: List[MemberSummary] = field(default_factory=list)
    risk_flags: List[RiskFlag] = field(default_factory=list)
    public_overhead: Optional[PublicOverhead] = None
    interview_summary: Optional[InterviewSummary] = None
    trend_analysis: Optional[TrendAnalysis] = None
    missing_data_days: int = 0
    missing_data_members: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "sprint_id": self.sprint_id,
            "generated_at": self.generated_at.isoformat(),
            "member_summaries": [ms.to_dict() for ms in self.member_summaries],
            "risk_flags": [rf.to_dict() for rf in self.risk_flags],
            "public_overhead": self.public_overhead.to_dict() if self.public_overhead else None,
            "interview_summary": self.interview_summary.to_dict() if self.interview_summary else None,
            "trend_analysis": self.trend_analysis.to_dict() if self.trend_analysis else None,
            "missing_data_days": self.missing_data_days,
            "missing_data_members": self.missing_data_members,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RetroReport":
        report = cls(
            id=data["id"],
            sprint_id=data["sprint_id"],
            generated_at=datetime.fromisoformat(data["generated_at"]) if "generated_at" in data else datetime.now(),
            missing_data_days=data.get("missing_data_days", 0),
            missing_data_members=data.get("missing_data_members", []),
        )
        report.member_summaries = [MemberSummary.from_dict(ms) for ms in data.get("member_summaries", [])]
        report.risk_flags = [RiskFlag.from_dict(rf) for rf in data.get("risk_flags", [])]
        if data.get("public_overhead"):
            report.public_overhead = PublicOverhead.from_dict(data["public_overhead"])
        if data.get("interview_summary"):
            report.interview_summary = InterviewSummary.from_dict(data["interview_summary"])
        if data.get("trend_analysis"):
            report.trend_analysis = TrendAnalysis.from_dict(data["trend_analysis"])
        return report
