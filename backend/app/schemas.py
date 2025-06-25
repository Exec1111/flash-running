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
    repos = "repos"


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


# ---------- Gemini Generation ----------

class PlanGenerateRequest(BaseModel):
    prompt: str = Field(..., description="Le prompt de l'utilisateur pour générer le plan.")

class GeminiSession(BaseModel):
    date: dt_date
    type: SessionType
    exercise: str

class GeminiPlan(BaseModel):
    name: str
    goal: str
    sessions: list[GeminiSession]


# ---------- Strava Activity ----------

class StravaActivityBase(BaseModel):
    strava_id: int
    name: str | None
    type: str | None
    start_date: str | None
    distance: float | None
    moving_time: int | None

class StravaActivityCreate(StravaActivityBase):
    pass

class StravaActivity(StravaActivityBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

class StravaSyncResult(BaseModel):
    imported: int
    updated: int
    skipped: int

