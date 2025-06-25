import os
import httpx
from typing import Any, Dict, TYPE_CHECKING

STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
STRAVA_REDIRECT_URI = os.getenv("STRAVA_REDIRECT_URI", "http://localhost:8000/strava/callback")
STRAVA_OAUTH_URL = "https://www.strava.com/oauth/authorize"
STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"


def get_authorize_url(state: str = "") -> str:
    if not STRAVA_CLIENT_ID:
        raise RuntimeError("STRAVA_CLIENT_ID non défini")
    params = {
        "client_id": STRAVA_CLIENT_ID,
        "redirect_uri": STRAVA_REDIRECT_URI,
        "response_type": "code",
        "scope": "read,activity:read",
        "state": state,
        "approval_prompt": "auto",
    }
    import urllib.parse as up

    return f"{STRAVA_OAUTH_URL}?{up.urlencode(params)}"


def exchange_code(code: str) -> Dict[str, Any]:
    if not (STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET):
        raise RuntimeError("STRAVA_CLIENT_ID/SECRET non définis")
    data = {
        "client_id": STRAVA_CLIENT_ID,
        "client_secret": STRAVA_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
    }
    with httpx.Client() as client:
        resp = client.post(STRAVA_TOKEN_URL, data=data, timeout=10)
        resp.raise_for_status()
        return resp.json()


def refresh_access_token(refresh_token: str) -> Dict[str, Any]:
    data = {
        "client_id": STRAVA_CLIENT_ID,
        "client_secret": STRAVA_CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    with httpx.Client() as client:
        resp = client.post(STRAVA_TOKEN_URL, data=data, timeout=10)
        resp.raise_for_status()
        return resp.json()


import time

if TYPE_CHECKING:
    from . import models


def refresh_access_token_if_needed(token: "models.StravaToken") -> dict[str, Any]:
    """Vérifie l'expiration et rafraîchit si nécessaire. Retourne un dict avec les nouvelles données du token."""
    # Check if token expires in the next 60 seconds
    if token.expires_at > int(time.time()) + 60:
        return {
            "access_token": token.access_token,
            "refresh_token": token.refresh_token,
            "expires_at": token.expires_at,
        }

    # Token is expired or about to expire, refresh it
    new_token_data = refresh_access_token(token.refresh_token)
    return new_token_data


def fetch_activities(access_token: str, page: int = 1, per_page: int = 30) -> list[dict[str, Any]]:
    """Récupère une page d'activités de l'athlète depuis l'API Strava."""
    url = "https://www.strava.com/api/v3/athlete/activities"
    params = {"page": page, "per_page": per_page}
    headers = {"Authorization": f"Bearer {access_token}"}

    with httpx.Client() as client:
        resp = client.get(url, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.json()
