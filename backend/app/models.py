"""Définition des modèles SQLAlchemy."""
from __future__ import annotations

import enum
from datetime import datetime, date

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    Enum as PgEnum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from .database import Base


class SessionType(str, enum.Enum):
    cardio = "cardio"
    running = "course_a_pied"
    other = "autre"
    repos = "repos"


class User(Base):
    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, index=True)
    email: str = Column(String(255), unique=True, nullable=False, index=True)
    name: str | None = Column(String(255))
    password_hash: str = Column(String(128), nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)

    plans = relationship("TrainingPlan", back_populates="owner", cascade="all, delete-orphan")

    strava_token = relationship("StravaToken", back_populates="user", uselist=False)


class TrainingPlan(Base):
    __tablename__ = "training_plans"

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String(255), nullable=False)
    goal: str | None = Column(Text)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)

    owner_id: int = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    owner = relationship("User", back_populates="plans")

    sessions = relationship(
        "Session", back_populates="plan", cascade="all, delete-orphan", order_by="Session.date"
    )


class StravaToken(Base):
    __tablename__ = "strava_tokens"

    id: int = Column(Integer, primary_key=True, index=True)
    user_id: int = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    access_token: str = Column(String(255), nullable=False)
    refresh_token: str = Column(String(255), nullable=False)
    expires_at: int = Column(Integer, nullable=False)

    user = relationship("User", back_populates="strava_token")


class StravaActivity(Base):
    __tablename__ = "strava_activities"

    id: int = Column(Integer, primary_key=True, index=True)
    strava_id: int = Column(BigInteger, unique=True, nullable=False, index=True)
    user_id: int = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    name: str | None = Column(String(255))
    type: str | None = Column(String(50))
    start_date: str | None = Column(String(50))  # ISO date string
    distance: float | None = Column(
        Float
    )  # mètres
    moving_time: int | None = Column(Integer)  # secondes

    user = relationship("User")


class Session(Base):
    __tablename__ = "sessions"

    id: int = Column(Integer, primary_key=True, index=True)
    date: date = Column(Date, nullable=False)
    type: SessionType = Column(PgEnum(SessionType), nullable=False, default=SessionType.running)
    exercise: str = Column(String(255), nullable=False)
    strava_activity_id: str | None = Column(String(64))
    completed: bool = Column(Boolean, default=False)

    plan_id: int = Column(Integer, ForeignKey("training_plans.id", ondelete="CASCADE"), nullable=False)
    plan = relationship("TrainingPlan", back_populates="sessions")
