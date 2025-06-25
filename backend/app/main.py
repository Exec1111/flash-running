from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import timedelta

from .security import SECRET_KEY, ALGORITHM, create_access_token


from .database import SessionLocal
from . import schemas, crud, models, strava_utils, gemini
import json

app = FastAPI(title="Training Plan API")

# --- CORS ---
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import httpx

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Dépendance Database

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    """Endpoint racine pour tester si l'API fonctionne."""
    return {"message": "Bienvenue sur l'API de plan d'entraînement!"}


# ----- Auth helpers -----

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(lambda: SessionLocal())):
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user(db, int(user_id))
    if user is None:
        raise credentials_exception
    return user

# ---------- Auth ----------

@app.post("/register", response_model=schemas.AuthResponse, status_code=201)
async def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user(db, user_id=0) and db.query(models.User).filter(models.User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud.create_user(db, user_in)
    token = create_access_token({"sub": str(user.id)})
    return {"user": user, "access_token": token}

@app.post("/login", response_model=schemas.AuthResponse)
async def login(form_data: schemas.UserCreate = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.email, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    token = create_access_token({"sub": str(user.id)})
    return {"user": user, "access_token": token}

# ---------- Users ----------

@app.post("/users", response_model=schemas.User, status_code=201)
async def create_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user_in)

@app.get("/users", response_model=list[schemas.User])
async def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.list_users(db, skip=skip, limit=limit)

@app.get("/users/{user_id}", response_model=schemas.User)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ---------- Plans ----------

@app.post("/plans/generate", response_model=schemas.TrainingPlan, status_code=201)
async def generate_plan(
    request: schemas.PlanGenerateRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Génère un plan d'entraînement à partir d'un prompt en utilisant l'API Gemini.
    """
    raw_plan_json = gemini.generate_training_plan_from_prompt(request.prompt)
    if not raw_plan_json:
        raise HTTPException(status_code=500, detail="Failed to generate plan from Gemini.")

    try:
        plan_data_dict = json.loads(raw_plan_json)
        gemini_plan = schemas.GeminiPlan(**plan_data_dict)
    except (json.JSONDecodeError, Exception) as e:
        print(f"Error parsing Gemini response: {e}")
        raise HTTPException(status_code=500, detail="Failed to parse the generated plan.")

    try:
        db_plan = crud.create_plan_from_gemini(db, owner_id=current_user.id, plan_data=gemini_plan)
        return db_plan
    except Exception as e:
        print(f"Error saving generated plan to DB: {e}")
        raise HTTPException(status_code=500, detail="Failed to save the generated plan.")


@app.post("/plans", response_model=schemas.TrainingPlan, status_code=201)
async def create_plan(
    plan_in: schemas.TrainingPlanCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    plan = crud.create_plan(db, owner_id=current_user.id, plan_in=plan_in)
    return plan


@app.get("/plans", response_model=list[schemas.TrainingPlan])
async def list_plans(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return crud.list_plans(db, owner_id=current_user.id, skip=skip, limit=limit)


@app.get("/plans/{plan_id}", response_model=schemas.TrainingPlan)
async def get_plan(
    plan_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    plan = crud.get_plan(db, plan_id)
    if not plan or plan.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@app.delete("/plans/{plan_id}", status_code=204)
async def delete_plan(
    plan_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    plan = crud.get_plan(db, plan_id)
    if not plan or plan.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Plan not found")
    crud.delete_plan(db, plan)
    return None


# ---------- Sessions ----------

@app.post("/plans/{plan_id}/sessions", response_model=schemas.Session, status_code=201)
async def add_session(
    plan_id: int,
    session_in: schemas.SessionCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    plan = crud.get_plan(db, plan_id)
    if not plan or plan.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Plan not found")
    return crud.add_session(db, plan, session_in)


@app.get("/plans/{plan_id}/sessions", response_model=list[schemas.Session])
async def list_sessions(
    plan_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    plan = crud.get_plan(db, plan_id)
    if not plan or plan.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Plan not found")
    return crud.list_sessions(db, plan_id)


# ---------- Strava ----------

@app.get("/strava/connect", status_code=307)
async def strava_connect(current_user: models.User = Depends(get_current_user)):
    """Redirige l'utilisateur vers l'écran d'autorisation Strava."""
    url = strava_utils.get_authorize_url(state=str(current_user.id))
    return RedirectResponse(url)


@app.get("/strava/connect-url", response_model=dict[str, str])
async def strava_connect_url(current_user: models.User = Depends(get_current_user)):
    """Retourne l'URL d'autorisation Strava (pour frontend fetch)."""
    return {"url": strava_utils.get_authorize_url(state=str(current_user.id))}


@app.get("/strava/callback")
async def strava_callback(code: str, state: str | None = None, db: Session = Depends(get_db)):
    """Callback OAuth Strava. Échange le *code* contre un token et le stocke."""
    token_data = strava_utils.exchange_code(code)
    user_id = int(state) if state else None
    if not user_id:
        raise HTTPException(status_code=400, detail="State manquant")
    crud.upsert_strava_token(
        db,
        user_id=user_id,
        access_token=token_data["access_token"],
        refresh_token=token_data["refresh_token"],
        expires_at=token_data["expires_at"],
    )
    # Redirige vers le dashboard frontend
    return RedirectResponse("http://localhost:3000/dashboard")


@app.post("/strava/sync", response_model=schemas.StravaSyncResult)
async def strava_sync(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Synchronise les dernières activités Strava pour l'utilisateur courant."""
    token = (
        db.query(models.StravaToken)
        .filter(models.StravaToken.user_id == current_user.id)
        .first()
    )
    if not token:
        raise HTTPException(status_code=400, detail="Compte Strava non lié.")

    # 1. Rafraîchir le token si nécessaire
    try:
        new_token_data = strava_utils.refresh_access_token_if_needed(token)
        # Si le token a été rafraîchi, les nouvelles données sont dans `new_token_data`
        if new_token_data["access_token"] != token.access_token:
            crud.upsert_strava_token(
                db,
                user_id=current_user.id,
                access_token=new_token_data["access_token"],
                refresh_token=new_token_data["refresh_token"],
                expires_at=new_token_data["expires_at"],
            )
            access_token = new_token_data["access_token"]
        else:
            access_token = token.access_token
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=400, detail=f"Erreur de rafraîchissement du token Strava: {e.response.text}"
        )

    # 2. Récupérer les activités
    try:
        activities = strava_utils.fetch_activities(access_token, per_page=30)
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=400, detail=f"Erreur de récupération des activités Strava: {e.response.text}"
        )

    if not activities:
        return {"imported": 0, "updated": 0, "skipped": 0}

    # 3. Enregistrer les activités en base
    stats = {"imported": 0, "updated": 0, "skipped": 0}
    for activity in activities:
        activity_data = schemas.StravaActivityCreate(
            strava_id=activity["id"],
            name=activity.get("name"),
            type=activity.get("type"),
            start_date=activity.get("start_date_local"),
            distance=activity.get("distance"),
            moving_time=activity.get("moving_time"),
        )
        _, created = crud.upsert_strava_activity(
            db, user_id=current_user.id, activity_data=activity_data
        )
        if created:
            stats["imported"] += 1
        else:
            stats["updated"] += 1

    return stats

