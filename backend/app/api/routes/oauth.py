"""Google & GitHub OAuth login routes.

Deliberately NOT mounted under /api (see main.py) -- these paths must match
GOOGLE_REDIRECT_URI / GITHUB_REDIRECT_URI exactly as registered in the
Google Cloud Console / GitHub OAuth App settings, and those are configured
as http://localhost:8000/auth/... (no /api prefix).
"""

from urllib.parse import quote

from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from app.core.config import settings
from app.core.logger import logger
from app.services.auth_service import auth_service
from app.utils.oauth import (
    get_google_auth_url,
    get_google_user_info,
    get_github_auth_url,
    get_github_user_info,
    OAuthError,
)

router = APIRouter(tags=["OAuth"])


def _redirect_with_error(message: str) -> RedirectResponse:
    return RedirectResponse(url=f"{settings.FRONTEND_URL}/login?auth=error&message={quote(message)}")


def _redirect_with_token(user: dict, token: str) -> RedirectResponse:
    url = (
        f"{settings.FRONTEND_URL}/"
        f"?auth=success&token={quote(token)}"
        f"&email={quote(user['email'])}"
        f"&username={quote(user['username'])}"
    )
    return RedirectResponse(url=url)


# ---- Google ----

@router.get("/google")
def google_login():
    return RedirectResponse(url=get_google_auth_url())


@router.get("/google/callback")
async def google_callback(code: str = None, error: str = None):
    if error:
        return _redirect_with_error(f"Google sign-in was cancelled ({error})")
    if not code:
        return _redirect_with_error("Google did not return an authorization code")

    try:
        profile = await get_google_user_info(code)
        user = auth_service.find_or_create_oauth_user(
            email=profile["email"],
            suggested_username=profile["email"].split("@")[0],
            full_name=profile.get("name"),
        )
        token = auth_service.issue_token(user)
        return _redirect_with_token(user, token)
    except OAuthError as e:
        logger.error(f"❌ Google OAuth failed: {e}")
        return _redirect_with_error(str(e))
    except Exception as e:
        logger.error(f"❌ Unexpected Google OAuth error: {e}")
        return _redirect_with_error("Google sign-in failed unexpectedly")


# ---- GitHub ----

@router.get("/github")
def github_login():
    return RedirectResponse(url=get_github_auth_url())


@router.get("/github/callback")
async def github_callback(code: str = None, error: str = None):
    if error:
        return _redirect_with_error(f"GitHub sign-in was cancelled ({error})")
    if not code:
        return _redirect_with_error("GitHub did not return an authorization code")

    try:
        profile = await get_github_user_info(code)
        user = auth_service.find_or_create_oauth_user(
            email=profile["email"],
            suggested_username=profile.get("username") or profile["email"].split("@")[0],
            full_name=profile.get("name"),
        )
        token = auth_service.issue_token(user)
        return _redirect_with_token(user, token)
    except OAuthError as e:
        logger.error(f"❌ GitHub OAuth failed: {e}")
        return _redirect_with_error(str(e))
    except Exception as e:
        logger.error(f"❌ Unexpected GitHub OAuth error: {e}")
        return _redirect_with_error("GitHub sign-in failed unexpectedly")