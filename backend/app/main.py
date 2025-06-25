from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import timedelta

from .security import SECRET_KEY, ALGORITHM, create_access_token


from .database import SessionLocal
from . import schemas, crud, models

app = FastAPI(title="Training Plan API")

# --- CORS ---
from fastapi.middleware.cors import CORSMiddleware

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
