from datetime import datetime, date
from typing import Optional, List
import uuid

from sqlalchemy import (
    String,
    Text,
    Date,
    DateTime,
    Float,
    Integer,
    ForeignKey,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    pass


class Sprint(Base):
    __tablename__ = "sprints"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    goal: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String, default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="sprint", cascade="all, delete-orphan")
    daily_logs: Mapped[List["DailyLog"]] = relationship("DailyLog", back_populates="sprint", cascade="all, delete-orphan")
    retros: Mapped[List["Retro"]] = relationship("Retro", back_populates="sprint", cascade="all, delete-orphan")
    retro_ratings: Mapped[List["RetroRating"]] = relationship("RetroRating", back_populates="sprint", cascade="all, delete-orphan")


class Member(Base):
    __tablename__ = "members"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)
    capacity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    avatar: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="assignee")
    daily_logs: Mapped[List["DailyLog"]] = relationship("DailyLog", back_populates="member", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sprint_id: Mapped[str] = mapped_column(ForeignKey("sprints.id"), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    assignee_id: Mapped[Optional[str]] = mapped_column(ForeignKey("members.id"), nullable=True)
    status: Mapped[str] = mapped_column(String, default="todo")
    priority: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    story_points: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    blocked_by: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array of task IDs
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sprint: Mapped["Sprint"] = relationship("Sprint", back_populates="tasks")
    assignee: Mapped[Optional["Member"]] = relationship("Member", back_populates="tasks")


class DailyLog(Base):
    __tablename__ = "daily_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sprint_id: Mapped[str] = mapped_column(ForeignKey("sprints.id"), nullable=False)
    member_id: Mapped[str] = mapped_column(ForeignKey("members.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    completed: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    planned: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    blockers: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hours_spent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    sprint: Mapped["Sprint"] = relationship("Sprint", back_populates="daily_logs")
    member: Mapped["Member"] = relationship("Member", back_populates="daily_logs")


class Retro(Base):
    __tablename__ = "retros"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sprint_id: Mapped[str] = mapped_column(ForeignKey("sprints.id"), nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    item: Mapped[str] = mapped_column(Text, nullable=False)
    votes: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    sprint: Mapped["Sprint"] = relationship("Sprint", back_populates="retros")


class RetroRating(Base):
    __tablename__ = "retro_ratings"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sprint_id: Mapped[str] = mapped_column(ForeignKey("sprints.id"), nullable=False)
    dimension: Mapped[str] = mapped_column(String, nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    sprint: Mapped["Sprint"] = relationship("Sprint", back_populates="retro_ratings")


class AgentMessage(Base):
    __tablename__ = "agent_messages"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    role: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Config(Base):
    __tablename__ = "config"

    key: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
