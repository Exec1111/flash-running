"""Schémas Pydantic pour les endpoints FastAPI."""
from __future__ import annotations

from datetime import date as dt_date
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class SessionType(str, Enum):
    cardio = "cardio"
    running = "course_a_pied"
    other = "autre"


# ---------- Session ----------
class SessionBase(BaseModel):
    date: dt_date = Field(..., description="Date de la séance")
    type: SessionType = Field(SessionType.running, description="Type de séance")
    exercise: str = Field(..., description="Exercice (ex: 3x10 accélérations)")
    strava_activity_id: Optional[str] = None
    completed: bool = False


class SessionCreate(SessionBase):
    pass


class Session(SessionBase):
    id: int
    plan_id: int

    class Config:
        orm_mode = True


# ---------- User ----------

class UserBase(BaseModel):
    email: str = Field(..., description="Adresse email")
    name: str | None = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class User(UserBase):
    id: int
    class Config:
        orm_mode = True

# ---------- Auth ----------

class AuthResponse(BaseModel):
    user: "User"
    access_token: str

# ---------- TrainingPlan ----------
class TrainingPlanBase(BaseModel):
    name: str
    goal: Optional[str] = None


class TrainingPlanCreate(TrainingPlanBase):
    pass


class TrainingPlan(TrainingPlanBase):
    id: int
    owner_id: int
    sessions: list["Session"] = Field(default_factory=list)

    class Config:
        orm_mode = True
