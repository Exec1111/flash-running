"""Fonctions CRUD pour les plans d'entraînement et les séances."""
from __future__ import annotations

from sqlalchemy.orm import Session

from . import models, schemas

# ---------- Users ----------

from .security import hash_password, verify_password


def create_user(db: Session, user_in: schemas.UserCreate) -> models.User:
    user = models.User(
        email=user_in.email,
        name=user_in.name,
        password_hash=hash_password(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user(db: Session, user_id: int) -> models.User | None:
    return db.query(models.User).filter(models.User.id == user_id).first()

def authenticate_user(db: Session, email: str, password: str) -> models.User | None:
    user = db.query(models.User).filter(models.User.email == email).first()
    if user and verify_password(password, user.password_hash):
        return user
    return None

def list_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

# ---------- Plans ----------

def create_plan(db: Session, owner_id: int, plan_in: schemas.TrainingPlanCreate) -> models.TrainingPlan:
    plan = models.TrainingPlan(**plan_in.dict(), owner_id=owner_id)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def get_plan(db: Session, plan_id: int) -> models.TrainingPlan | None:
    return db.query(models.TrainingPlan).filter(models.TrainingPlan.id == plan_id).first()


def list_plans(db: Session, owner_id: int | None = None, skip: int = 0, limit: int = 100):
    """Liste les plans.
    - Si *owner_id* est fourni, ne retourne que les plans appartenant à cet utilisateur.
    - Sinon, retourne l'ensemble des plans (usage admin).
    """
    query = db.query(models.TrainingPlan)
    if owner_id is not None:
        query = query.filter(models.TrainingPlan.owner_id == owner_id)
    return query.offset(skip).limit(limit).all()


def delete_plan(db: Session, plan: models.TrainingPlan) -> None:
    db.delete(plan)
    db.commit()


def create_plan_from_gemini(db: Session, owner_id: int, plan_data: schemas.GeminiPlan) -> models.TrainingPlan:
    """
    Crée un plan d'entraînement complet et ses séances à partir d'une structure générée par Gemini.
    """
    db_plan = models.TrainingPlan(
        name=plan_data.name,
        goal=plan_data.goal,
        owner_id=owner_id
    )

    for session_data in plan_data.sessions:
        db_session = models.Session(
            date=session_data.date,
            type=session_data.type,
            exercise=session_data.exercise,
        )
        db_plan.sessions.append(db_session)

    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan


# ---------- Strava ----------

def upsert_strava_token(
    db: Session,
    user_id: int,
    access_token: str,
    refresh_token: str,
    expires_at: int,
):
    token = db.query(models.StravaToken).filter(models.StravaToken.user_id == user_id).first()
    if token:
        token.access_token = access_token
        token.refresh_token = refresh_token
        token.expires_at = expires_at
    else:
        token = models.StravaToken(
            user_id=user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
        )
        db.add(token)
    db.commit()
    db.refresh(token)
    return token


def upsert_strava_activity(db: Session, user_id: int, activity_data: schemas.StravaActivityCreate) -> tuple[models.StravaActivity, bool]:
    """
    Crée ou met à jour une activité Strava dans la base de données.
    Retourne l'objet de l'activité et un booléen `created`.
    """
    existing_activity = (
        db.query(models.StravaActivity)
        .filter(models.StravaActivity.strava_id == activity_data.strava_id)
        .first()
    )

    if existing_activity:
        # Update
        update_data = activity_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(existing_activity, key, value)
        db.commit()
        db.refresh(existing_activity)
        return existing_activity, False  # False for 'created'
    else:
        # Create
        new_activity = models.StravaActivity(**activity_data.dict(), user_id=user_id)
        db.add(new_activity)
        db.commit()
        db.refresh(new_activity)
        return new_activity, True  # True for 'created'


# ---------- Sessions ----------

def add_session(
    db: Session,
    plan: models.TrainingPlan,
    session_in: schemas.SessionCreate,
) -> models.Session:
    session = models.Session(**session_in.dict(), plan_id=plan.id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def list_sessions(db: Session, plan_id: int):
    return db.query(models.Session).filter(models.Session.plan_id == plan_id).all()
