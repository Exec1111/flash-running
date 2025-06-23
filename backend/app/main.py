from fastapi import FastAPI

app = FastAPI(title="Training Plan API")


@app.get("/")
async def root():
    """Endpoint racine pour tester si l'API fonctionne."""
    return {"message": "Bienvenue sur l'API de plan d'entraînement!"}
