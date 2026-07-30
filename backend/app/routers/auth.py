# backend/routers/auth.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from config import settings
from utils.oauth import (
    get_google_auth_url,
    get_google_user_info,
    get_github_auth_url,
    get_github_user_info,
)

router = APIRouter(prefix="/auth", tags=["OAuth Authentication"])

# --- GOOGLE ENDPOINTS ---

@router.get("/google")
def google_login():
    # Adding prompt=consent guarantees a fresh single-use code every login attempt
    url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"response_type=code&client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
        f"&scope=openid%20email%20profile"
        f"&access_type=offline&prompt=consent"
    )
    return RedirectResponse(url=url)

@router.get("/google/callback")
async def google_callback(code: str):
    """Callback triggered by Google after successful authentication"""
    try:
        user_info = await get_google_user_info(code)
        email = user_info.get("email")
        name = user_info.get("name")
        
        # TODO: Save user to your SQLite database here if they don't exist yet
        # e.g., token = create_jwt_token({"sub": email, "name": name})

        # Redirect user back to frontend dashboard with token
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/dashboard?auth=success&email={email}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Google authentication failed: {str(e)}")


# --- GITHUB ENDPOINTS ---

@router.get("/github")
def github_login():
    """Redirects the user to GitHub Login Consent Screen"""
    return RedirectResponse(url=get_github_auth_url())

@router.get("/github/callback")
async def github_callback(code: str):
    """Callback triggered by GitHub after successful authentication"""
    try:
        user_info = await get_github_user_info(code)
        email = user_info.get("email")
        username = user_info.get("login")
        
        # TODO: Save user to your SQLite database here if they don't exist yet
        # e.g., token = create_jwt_token({"sub": email, "username": username})

        # Redirect user back to frontend dashboard
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/dashboard?auth=success&email={email}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"GitHub authentication failed: {str(e)}")